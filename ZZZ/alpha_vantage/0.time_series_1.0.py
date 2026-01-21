from financial_tools import AlphaVantageClient, FinancialAnalyzer, FMPClient
import time

# --- Configuration ---

# API_KEY = "PTIKPYJ08KJ0X8T5"
# API_KEY = "DLTHXPRVU26T0J2K"
# API_KEY = "1PJAD8TJTI99U5V4"
# API_KEY = 'BUPOTKIYO88O640R'
API_KEY = 'C0QD6H0OLHXD1EKE'
TICKER_LIST = ['HELE', 'NWL', 'LCUT', 'SPB', 'YETI']
# --- Instantiate the Classes ---
main = FMPClient()
client = AlphaVantageClient(API_KEY)
analyzer = FinancialAnalyzer()

symbol = 'HELE'
inc = main.get_data('income-statement', symbol)
bs = main.get_data('balance-sheet-statement', symbol)
cf = main.get_data('cash-flow-statement', symbol)
df_merged = analyzer.build_merged_dataframe(inc, bs, cf)


# --- Run the Logic ---
for symbol in TICKER_LIST:
    print(f"\n--- Processing {symbol} ---")

    # Fetch Data
    inc = client.get_data('INCOME_STATEMENT', symbol)
    time.sleep(5)

    bs = client.get_data('BALANCE_SHEET', symbol)
    time.sleep(5)

    cf = client.get_data('CASH_FLOW', symbol)
    time.sleep(5)

    # Process
    if inc and bs and cf:
        df_merged = analyzer.build_merged_dataframe(inc, bs, cf)
        output = analyzer.process_ltm_data(df_merged)

        if not output.empty:
            print(output.iloc[:, :4])  # Print preview
            output.reset_index().to_csv(f"{symbol}_{output.iloc[0,0]}.csv")
            print(f"Saved {symbol}_Analysis.csv")
    else:
        print(f"Skipping {symbol} due to missing data.")