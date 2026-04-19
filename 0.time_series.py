import sys
sys.path.insert(0, "_src")
from financial_tools import FinancialAnalyzer, FMPClient

import os
import subprocess
import pandas as pd
import numpy as np
from datetime import date


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
# --- Configuration ---

TICKER_LIST = ['stock_Refinery',
               ["MPC", "DK", 'PBF']
]

# --- Setup Output Directory ---
output_dir = os.path.join("outputs", TICKER_LIST[0], date.today().isoformat())
# Create the folder path if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# --- Instantiate the Classes ---
client1 = FMPClient()
analyzer = FinancialAnalyzer()

# --- Run the Logic ---
all_tickers_data = []
all_tickers_price = []
for symbol in np.unique(TICKER_LIST[1]):
    print(f"\n--- Processing {symbol} ---")

    # Fetch Data
    inc = client1.get_data('income-statement', symbol)
    # inc = client1.get_data('income-statement-as-reported', symbol)
    # df = client2.get_data('INCOME_STATEMENT', symbol)
    bs  = client1.get_data('balance-sheet-statement', symbol)
    cf  = client1.get_data('cash-flow-statement', symbol)
    ev = client1.get_data('enterprise-values', symbol)
    price = pd.DataFrame(client1.get_data('historical-price-eod', symbol))
    all_tickers_price.append(price)

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
            print(output.applymap(analyzer.format_numbers).iloc[:, :5])
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

    # Export to Excel
    file_name = os.path.join(output_dir, "_peer_analysis.csv")
    final_df.reset_index().to_csv(file_name, index=False)
    print(f"\nSuccess! Combined dataset saved to {file_name}")
    print(final_df.applymap(analyzer.format_numbers).iloc[:,:5])
    # Export to Excel
    file_name = price_file = os.path.join(output_dir, "_price.xlsx")
    price_df.to_excel(file_name, index=False)
    print(f"\nSuccess! daily price dataset saved to {file_name}")
else:
    print("\nNo data was collected to export.")


def git_push(message, folder_path):
    try:
        # Add all files in the specific output directory
        subprocess.run(["git", "add", folder_path], check=True)
        # Commit with a custom message
        subprocess.run(["git", "commit", "-m", message], check=True)
        # Push to the remote repository (usually 'origin main' or 'origin master')
        subprocess.run(["git", "push"], check=True)
        print("Successfully pushed to Git!")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")
git_push(TICKER_LIST[0], output_dir)