import subprocess

def pull_repo():
    """Pulls the latest changes in the current directory."""
    try:
        # Runs 'git pull' right where the script is executed
        result = subprocess.run(
            ['git', 'pull'], 
            capture_output=True,      
            text=True,                
            check=True                
        )
        
        print("Successfully pulled from remote.")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("Failed to pull from remote.")
        print("Error details:\n", e.stderr)

# Execute the function
pull_repo()

from pathlib import Path

def parse_watchlist_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    # Remove outer brackets
    inner = line.strip("[]").strip()

    # Split into the first element and the inner ticker list
    first, rest = inner.split(",", 1)
    category = first.strip()

    tickers = rest.strip().strip("[]").split(",")
    tickers = [t.strip().upper() for t in tickers if t.strip()]

    return [category, tickers]

watchlist_path = Path("watchlist.txt")
ticker_list = []
with watchlist_path.open("r", encoding="utf-8") as f:
    for line in f:
        parsed = parse_watchlist_line(line)
        if parsed:
            ticker_list.append(parsed)

import sys
sys.path.insert(0, "_src")
from financial_tools import FinancialAnalyzer, FMPClient

import os
import subprocess
import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path


pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
# --- Configuration ---

import subprocess
def git_push(message, folder_path):
    try:
        # Add files in the specific output directory
        subprocess.run(["git", "add", folder_path], check=True)
        # Also add any other modified files in the repo
        #subprocess.run(["git", "add", "-A"], check=True)
        
        # Check if there are staged changes
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if result.returncode == 0:
            print("No changes to commit")
            return
        
        # Commit with a custom message
        subprocess.run(["git", "commit", "-m", message], check=True)
        # Push to the remote repository
        subprocess.run(["git", "push"], check=True)
        print("Successfully pushed to Git!")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")


for TICKER_LIST in ticker_list[1::]:
    if TICKER_LIST is not None:
        # --- Setup Output Directory ---
        output_dir = Path("outputs") / f"{TICKER_LIST[0]}_{TICKER_LIST[1][0]}" / date.today().isoformat()
        output_dir.mkdir(parents=True, exist_ok=True)

        # --- Instantiate the Classes ---
        client1 = FMPClient()
        analyzer = FinancialAnalyzer()

        # --- Run the Logic ---
        all_tickers_data = []
        all_tickers_price = []

        all_tickers_news = {}
        all_tickers_sec_filings = {}

        for symbol in np.unique(TICKER_LIST[1]):
            print(f"\n--- Processing {symbol} ---")

            # Fetch Data
            inc = client1.get_data('income-statement', symbol)
            # inc = client1.get_data('income-statement-as-reported', symbol)
            # df = client2.get_data('INCOME_STATEMENT', symbol)
            bs  = client1.get_data('balance-sheet-statement', symbol)
            cf  = client1.get_data('cash-flow-statement', symbol)
            ev = client1.get_data('enterprise-values', symbol)
            news = client1.get_data('news', symbol)
            sec_filings = client1.get_data('sec-filings-search', symbol)
            price = pd.DataFrame(client1.get_data('historical-price-eod', symbol))
            all_tickers_price.append(price)
            all_tickers_news[symbol] = news
            all_tickers_sec_filings[symbol] = sec_filings

            # 1. Fetch data
            rev_bus_seg = client1.get_data('revenue-product-segmentation', symbol)
            rev_geo_seg = client1.get_data('revenue-geographic-segmentation', symbol)
            # 2. Determine which source to use
            raw_data = rev_bus_seg if rev_bus_seg else rev_geo_seg
            # 3. Create DataFrame (or empty fallback with columns)
            if raw_data:
                rev_seg = pd.DataFrame(raw_data)
                rev_seg = rev_seg.apply(analyzer.process_segments, axis=1)
            else:
                # Initialize with your required columns so .set_index(self.id_vars) doesn't fail
                rev_seg = pd.DataFrame(columns=analyzer.segment_vars + analyzer.id_vars)
            # Optional: Ensure it's never None
            rev_seg = rev_seg if rev_seg is not None else pd.DataFrame()

            # Process
            if inc and bs and cf and ev:
                df_merged = analyzer.build_merged_dataframe(inc, bs, cf, ev, rev_seg)
                output = analyzer.process_ltm_data(df_merged)
                output = analyzer.add_category(output)

                if not output.empty:
                    print(output.map(analyzer.format_numbers).iloc[:, :5])
                    file_path = os.path.join(output_dir, f"{symbol}_{output.iloc[2, 0]}.csv")
                    output.to_csv(file_path, index=True)
                    print(f"Saved {file_path}")

                    output = output.replace('-', np.nan).bfill(axis=1)
                    latest_col = output.iloc[:, [0]].fillna('-')
                    latest_col.columns = [symbol]
                    all_tickers_data.append(latest_col)
            else:
                print(f"Skipping {symbol} due to missing data.")

        # --- Combine and Export ---
        if all_tickers_data:
            # Concatenate horizontally (axis=1) based on the row labels (Income/BS/CF items)
            final_df = pd.concat(all_tickers_data, axis=1)
            price_df = pd.concat(all_tickers_price, axis=0, ignore_index=False)

            # Export to CSV and Excel in the expected peer-analysis layout
            csv_file = os.path.join(output_dir, "_peer_analysis.csv")
            final_df.to_csv(csv_file, index=True)
            print(f"\nSuccess! Combined dataset saved to {csv_file}")
            # Export daily price history
            price_file = os.path.join(output_dir, "_price.xlsx")
            price_df.to_excel(price_file, index=False)
            print(f"\nSuccess! daily price dataset saved to {price_file}")
            # Export to Excel
            news_file = os.path.join("outputs", TICKER_LIST[0], "_news.xlsx")
            writer_kwargs = {'engine': 'openpyxl', 'mode': 'w'}
            if os.path.exists(news_file):
                writer_kwargs['mode'] = 'a'
                writer_kwargs['if_sheet_exists'] = 'replace'
            with pd.ExcelWriter(news_file, **writer_kwargs)as writer:   
                for k, v in all_tickers_news.items():
                    pd.DataFrame(v).to_excel(writer, sheet_name=k, index=False)
            print(f"\nSuccess! news dataset saved to {news_file}")

            sec_filings_file = os.path.join("outputs", TICKER_LIST[0], "_sec_filings.xlsx")
            with pd.ExcelWriter(sec_filings_file, **writer_kwargs) as writer:   
                for k, v in all_tickers_sec_filings.items():
                    pd.DataFrame(v).to_excel(writer, sheet_name=k, index=False)       
            print(f"\nSuccess! SEC filings dataset saved to {sec_filings_file}")
            
        else:
            print("\nNo data was collected to export.")

        git_push(f"peer_analysis: {TICKER_LIST[1][0]}_{TICKER_LIST[0]}", output_dir)
