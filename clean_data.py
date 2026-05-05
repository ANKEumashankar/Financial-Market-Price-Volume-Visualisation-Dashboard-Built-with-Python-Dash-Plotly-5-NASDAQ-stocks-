import pandas as pd
import os

TICKERS = ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL"]

os.makedirs("cleaned_data", exist_ok=True)

print("Cleaning stock data...")

for ticker in TICKERS:
    print(f"\n  Processing {ticker}...")

    # Read raw CSV
    df = pd.read_csv(f"raw_data/{ticker}_raw.csv")

    # Show before cleaning
    print(f"     Rows before cleaning : {len(df)}")

    # Fix Date column
    df["Date"] = pd.to_datetime(df["Date"])

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove missing values
    df = df.dropna()

    # Fix column data types
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Round prices to 2 decimal places
    df[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]].round(2)

    # Reset index
    df = df.reset_index(drop=True)

    # Save clean file
    df.to_csv(f"cleaned_data/{ticker}_clean.csv", index=False)

    print(f"     Rows after cleaning  : {len(df)}")
    print(f"     Date range : {df['Date'].min().date()} → {df['Date'].max().date()}")
    print(f"     ✅ Saved to cleaned_data/{ticker}_clean.csv")

print("\n✅ All stocks cleaned and saved in cleaned_data folder!")
