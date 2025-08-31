import yfinance as yf
import pandas as pd
import os
import re
from datetime import datetime, timedelta


def is_a_share_stock(symbol):
    """Check if symbol is a 6-digit A-share stock code."""
    return bool(re.match(r'^\d{6}$', str(symbol)))


def convert_a_share_to_yahoo(symbol):
    """Convert 6-digit A-share stock code to Yahoo Finance format."""
    if symbol.startswith('6'):
        return f"{symbol}.SS"  # Shanghai Stock Exchange
    elif symbol.startswith('0') or symbol.startswith('3'):
        return f"{symbol}.SZ"  # Shenzhen Stock Exchange
    else:
        return symbol  # Return as-is if not recognized


def fetch_yahoo_data(asset_symbols, period="52wk", interval="1wk"):
    """
    Fetch weekly data from Yahoo Finance for given asset symbols.
    Supports A-share stocks (6-digit codes) by converting to Yahoo format.
    
    Args:
        asset_symbols (str or list): Asset symbol(s) to fetch data for
        period (str): Time period to fetch (default: "52wk")
        interval (str): Data interval (default: "1wk")
        
    Returns:
        dict: Dictionary with asset symbols as keys and DataFrames as values
    """
    if isinstance(asset_symbols, str):
        asset_symbols = [asset_symbols]
    
    data_dict = {}
    
    for symbol in asset_symbols:
        try:
            # Handle A-share stock codes
            original_symbol = symbol
            if is_a_share_stock(symbol):
                yahoo_symbol = convert_a_share_to_yahoo(symbol)
                print(f"Converting A-share code {symbol} to Yahoo format: {yahoo_symbol}")
            else:
                yahoo_symbol = symbol
            
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"Warning: No data found for {symbol} (Yahoo: {yahoo_symbol})")
                continue
                
            # Reset index to make Date a column
            df = df.reset_index()
            df.rename(columns={'Date': 'timestamps'}, inplace=True)
            
            # Rename columns to match Kronos format
            df.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            # Add amount column (approximated as close * volume)
            df['amount'] = df['close'] * df['volume']
            
            # Select only the columns we need
            df = df[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]
            
            data_dict[original_symbol] = df
            print(f"Successfully fetched {len(df)} records for {original_symbol} (Yahoo: {yahoo_symbol})")
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    
    return data_dict


def save_data_to_csv(data_dict, output_dir="data"):
    """
    Save fetched data to CSV files in the specified directory.
    
    Args:
        data_dict (dict): Dictionary with asset symbols and DataFrames
        output_dir (str): Directory to save CSV files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for symbol, df in data_dict.items():
        # Clean symbol for filename
        clean_symbol = symbol.replace("^", "").replace(".", "_")
        filename = f"{clean_symbol}_weekly.csv"
        filepath = os.path.join(output_dir, filename)
        
        df.to_csv(filepath, index=False)
        print(f"Saved data for {symbol} to {filepath}")


def load_data_from_csv(symbol, data_dir="data"):
    """
    Load data from CSV file for a specific symbol.
    
    Args:
        symbol (str): Asset symbol
        data_dir (str): Directory containing CSV files
        
    Returns:
        pandas.DataFrame: Loaded data
    """
    clean_symbol = symbol.replace("^", "").replace(".", "_")
    filename = f"{clean_symbol}_weekly.csv"
    filepath = os.path.join(data_dir, filename)
    
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df['timestamps'] = pd.to_datetime(df['timestamps'])
        return df
    else:
        raise FileNotFoundError(f"Data file not found for {symbol}: {filepath}")