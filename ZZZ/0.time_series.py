from financial_tools import AlphaVantageClient, FinancialAnalyzer, FMPClient
import pandas as pd
import numpy as np
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
# --- Configuration ---

API_KEY = "PTIKPYJ08KJ0X8T5"
TICKER_LIST = ['HELE', 'NWL', 'LCUT', 'SPB', 'YETI']
TICKER_LIST = ['JELD', 'BLDR', 'OC', 'FBIN']

# --- Instantiate the Classes ---
client2 = AlphaVantageClient(API_KEY)
client1 = FMPClient()
analyzer = FinancialAnalyzer()

# --- Run the Logic ---
all_tickers_data = []
for symbol in TICKER_LIST:
    print(f"\n--- Processing {symbol} ---")

    # Fetch Data
    inc = client1.get_data('income-statement', symbol)
    # inc = client1.get_data('income-statement-as-reported', symbol)
    # df = client2.get_data('INCOME_STATEMENT', symbol)
    bs  = client1.get_data('balance-sheet-statement', symbol)
    cf  = client1.get_data('cash-flow-statement', symbol)
    ev = client1.get_data('enterprise-values', symbol)
    #price = client1.get_data('historical-price-eod', symbol)


    rev_bus_seg = client1.get_data('revenue-product-segmentation', symbol)
    rev_geo_seg = client1.get_data('revenue-geographic-segmentation', symbol)
    if rev_bus_seg:
        rev_seg = pd.DataFrame(rev_bus_seg)
        rev_seg = rev_seg.apply(analyzer.process_segments, axis=1)
    else:
        rev_seg = pd.DataFrame(rev_geo_seg)
        rev_seg = rev_seg.apply(analyzer.process_segments, axis=1)

    # Process
    if inc and bs and cf and ev:
        df_merged = analyzer.build_merged_dataframe(inc, bs, cf, ev, rev_seg)
        output = analyzer.process_ltm_data(df_merged)
        output = analyzer.add_category(output)

        if not output.empty:
            print(output.applymap(analyzer.format_numbers).iloc[:, :5])
            output.to_csv(f"{symbol}_{output.iloc[2,0]}.csv", index=True)
            print(f"Saved {symbol}_{output.iloc[2,0]}.csv")

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

    # Export to Excel
    file_name = f"peer_analysis_{TICKER_LIST[0]}.csv"
    final_df.reset_index().to_csv(file_name, index=False)
    print(f"\nSuccess! Combined dataset saved to {file_name}")
    print(final_df.applymap(analyzer.format_numbers).iloc[:,:5])
else:
    print("\nNo data was collected to export.")