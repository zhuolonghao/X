from financial_tools import AlphaVantageClient, FinancialAnalyzer, FMPClient
import time

# --- Configuration ---

# API_KEY = "PTIKPYJ08KJ0X8T5"
TICKER_LIST = ['HELE', 'NWL', 'LCUT', 'SPB', 'YETI']
# --- Instantiate the Classes ---
client2 = AlphaVantageClient(API_KEY)
client1 = FMPClient()
analyzer = FinancialAnalyzer()

# --- Run the Logic ---
for symbol in TICKER_LIST:
    print(f"\n--- Processing {symbol} ---")

    # Fetch Data
    inc = client1.get_data('income-statement', symbol)
    bs  = client1.get_data('balance-sheet-statement', symbol)
    cf  = client1.get_data('cash-flow-statement', symbol)

    # Process
    if inc and bs and cf:
        df_merged = analyzer.build_merged_dataframe(inc, bs, cf)
        output = analyzer.process_ltm_data(df_merged)

        if not output.empty:
            print(output.applymap(analyzer.format_numbers).iloc[:, :3])
            output.reset_index().to_csv(f"{symbol}_{output.iloc[0,0]}.csv", index=False)
            print(f"Saved {symbol}_{output.iloc[0,0]}.csv")
    else:
        print(f"Skipping {symbol} due to missing data.")