#!/usr/bin/env python3
"""
Main script for Kronos asset price prediction system.
Fetches data from Yahoo Finance, makes predictions using Kronos model,
and visualizes results for one or multiple assets.
"""

import argparse
import sys
import os

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import fetch_yahoo_data, save_data_to_csv, load_data_from_csv
from predictor import KronosPredictorWrapper
from visualizer import plot_predictions, create_comparison_plot, generate_prediction_report


def load_assets_from_file(file_path):
    """Load asset symbols from a text file, one symbol per line."""
    assets = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    assets.append(line)
        return assets
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


def main():
    """Main function to run the prediction pipeline."""
    parser = argparse.ArgumentParser(description='Kronos Asset Price Prediction System')
    parser.add_argument('assets', nargs='*', help='Asset symbols (e.g., AAPL BTC-USD) or .txt file')
    parser.add_argument('--file', '-f', help='Text file containing asset symbols (one per line)')
    parser.add_argument('--period', default='52wk', help='Time period to fetch (default: 52wk)')
    parser.add_argument('--interval', default='1wk', help='Data interval (default: 1wk)')
    parser.add_argument('--lookback', type=int, default=50, help='Weeks to look back (default: 50)')
    parser.add_argument('--predict', type=int, default=2, help='Weeks to predict (default: 2)')
    parser.add_argument('--fetch', action='store_true', help='Force fetch new data')
    parser.add_argument('--model', default='NeoQuasar/Kronos-small', help='Kronos model name')
    parser.add_argument('--device', default='auto', help='Device to use (cuda/cpu/auto)')
    
    args = parser.parse_args()
    
    # Load assets from command line or file
    asset_symbols = []
    
    if args.file:
        asset_symbols = load_assets_from_file(args.file)
        if not asset_symbols:
            print("No assets loaded from file. Exiting.")
            return
    
    # Add assets from command line arguments
    if args.assets:
        asset_symbols.extend(args.assets)
    
    if not asset_symbols:
        print("Error: No assets specified. Provide symbols or use --file option.")
        parser.print_help()
        return
    
    # Set device
    if args.device == 'auto':
        import torch
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    
    print(f"Kronos Asset Prediction System")
    print(f"=" * 50)
    print(f"Assets: {asset_symbols}")
    print(f"Lookback: {args.lookback} weeks")
    print(f"Prediction: {args.predict} weeks")
    print(f"Device: {device}")
    print(f"=" * 50)
    
    # Step 1: Fetch or load data
    data_dict = {}
    
    if args.fetch:
        print("\n1. Fetching data from Yahoo Finance...")
        # Calculate needed period: lookback + predict weeks, converted to years with buffer
        total_weeks_needed = args.lookback + args.predict
        period_years = max(2, (total_weeks_needed + 26) // 52)  # At least 2 years, add buffer
        fetch_period = f"{period_years}y"
        data_dict = fetch_yahoo_data(asset_symbols, fetch_period, args.interval)
        if not data_dict or len(data_dict) == 0:
            print("No data fetched. Exiting.")
            return
        
        # Save the fetched data
        save_data_to_csv(data_dict)
        print("Data saved successfully.")
        
        # Use the already fetched data for prediction, no need to reload
        print("Using fetched data for prediction...")
        for asset, df in data_dict.items():
            print(f"Using data for {asset}: {len(df)} records")
    else:
        print("\n1. Loading data from local files...")
        for asset in asset_symbols:
            try:
                df = load_data_from_csv(asset)
                data_dict[asset] = df
                print(f"Loaded data for {asset}: {len(df)} records")
            except FileNotFoundError:
                print(f"No local data found for {asset}. Use --fetch to download new data.")
                return
    
    if not data_dict:
        print("No data available. Exiting.")
        return
    
    # Step 2: Initialize predictor
    print("\n2. Initializing Kronos predictor...")
    try:
        predictor = KronosPredictorWrapper(model_name=args.model, device=device)
    except Exception as e:
        print(f"Error initializing predictor: {e}")
        return
    
    # Step 3: Make predictions
    print("\n3. Making predictions...")
    predictions = {}
    validation_data = {}
    
    for asset, df in data_dict.items():
        try:
            print(f"\nPredicting for {asset}...")
            
            # Always use validation mode: train on t0-4w之前的数据，预测t0-4w到t0+4w
            pred_df, actual_validation = predictor.predict(
                df=df,
                lookback_weeks=args.lookback,
                pred_weeks=args.predict
            )
            predictions[asset] = pred_df
            validation_data[asset] = actual_validation
            
            # Display prediction summary
            last_price = df['close'].iloc[-1]
            pred_price = pred_df['close'].iloc[-1]
            change_pct = (pred_price - last_price) / last_price * 100
            
            print(f"  Last price: ${last_price:.2f}")
            print(f"  Predicted price: ${pred_price:.2f}")
            print(f"  Expected change: {change_pct:+.2f}%")
            
        except Exception as e:
            print(f"Error predicting for {asset}: {e}")
    
    if not predictions:
        print("No predictions made. Exiting.")
        return
    
    # Step 4: Visualize results
    print("\n4. Generating visualizations...")
    
    # Individual asset plots
    for asset, pred_df in predictions.items():
        try:
            historical_df = data_dict[asset]
            actual_validation = validation_data[asset]
            plot_predictions(historical_df, pred_df, asset, args.predict)
            generate_prediction_report(historical_df, pred_df, asset)
        except Exception as e:
            print(f"Error visualizing {asset}: {e}")
    
    # Comparison plot if multiple assets
    if len(predictions) > 1:
        try:
            create_comparison_plot(predictions)
        except Exception as e:
            print(f"Error creating comparison plot: {e}")
    
    print("\n5. Prediction pipeline completed successfully!")
    print("Check the output directory for results and visualizations.")


if __name__ == "__main__":
    main()