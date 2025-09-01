import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import numpy as np
from datetime import datetime


def calculate_prediction_accuracy(pred_df, actual_df):
    """
    Calculate prediction accuracy between predicted and actual prices.
    
    Args:
        pred_df (pandas.DataFrame): Predicted data
        actual_df (pandas.DataFrame): Actual data
        
    Returns:
        float: Accuracy percentage (100% = perfect prediction)
    """
    if len(pred_df) != len(actual_df):
        raise ValueError("Predicted and actual data must have the same length")
    
    # Calculate mean absolute percentage error
    pred_prices = pred_df['close'].values
    actual_prices = actual_df['close'].values
    
    mape = np.mean(np.abs((actual_prices - pred_prices) / actual_prices)) * 100
    accuracy = 100 - mape
    
    return max(0, accuracy)  # Ensure accuracy doesn't go below 0%


def plot_predictions(historical_df, pred_df, asset_name, pred_weeks=8, output_dir="output", show_plot=False):
    """
    Create and save visualization of predictions with Ground Truth vs Prediction comparison.
    
    Args:
        historical_df (pandas.DataFrame): Historical data
        pred_df (pandas.DataFrame): Prediction data
        asset_name (str): Name of the asset
        output_dir (str): Directory to save plots
        show_plot (bool): Whether to display the plot
    """
    # Create output directory
    asset_output_dir = os.path.join(output_dir, asset_name)
    os.makedirs(asset_output_dir, exist_ok=True)
    
    # Prepare data for plotting
    pred_df.index = historical_df.index[-pred_df.shape[0]:]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Combine historical and prediction data for clear Ground Truth vs Prediction comparison
    # Use timestamps for x-axis - historical has 'timestamps' column
    historical_timestamps = historical_df['timestamps']
    
    # Prediction starts at t0-4 weeks (2025-08-04), not at the end of historical data
    # Use the prediction DataFrame index which should contain the correct timestamps
    if hasattr(pred_df.index, 'iloc') and len(pred_df.index) > 0:
        pred_timestamps = pred_df.index
        prediction_start = pred_timestamps.iloc[0] if hasattr(pred_timestamps, 'iloc') else pred_timestamps[0]
    else:
        # Fallback: prediction starts 4 weeks before the end of historical data
        prediction_start = historical_timestamps.iloc[-pred_weeks//2]
        pred_timestamps = pd.date_range(start=prediction_start, periods=len(pred_df), freq='W-MON')
    
    # Plot close prices - Ground Truth vs Prediction
    ax1.plot(historical_timestamps, historical_df['close'], 
             label='Ground Truth', color='blue', linewidth=2)
    ax1.plot(pred_timestamps, pred_df['close'], 
             label='Prediction', color='red', linewidth=2, linestyle='--')
    
    # Add vertical line at the prediction start point
    ax1.axvline(x=prediction_start, color='gray', linestyle=':', alpha=0.7, label='Prediction Start')
    
    # Format x-axis with proper dates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    
    ax1.set_ylabel('Close Price', fontsize=12)
    ax1.set_title(f'{asset_name} - P & V prediction', fontsize=14)
    ax1.legend(loc='lower left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot volume as bar charts with red/green color based on price movement
    # Historical volume bars - green for up days, red for down days
    historical_volume_colors = ['green' if close > open else 'red' for close, open in 
                               zip(historical_df['close'], historical_df['open'])]
    for i, (timestamp, volume) in enumerate(zip(historical_timestamps, historical_df['volume'])):
        ax2.bar(timestamp, volume, width=5, color=historical_volume_colors[i], alpha=0.7)
    
    # Prediction volume bars - keep orange for predictions
    ax2.bar(pred_timestamps, pred_df['volume'], 
            width=5, label='Prediction Volume', color='orange', alpha=0.7)
    
    # Add legend for volume
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Ground Truth Volume (Up)'),
        Patch(facecolor='red', label='Ground Truth Volume (Down)'),
        Patch(facecolor='orange', label='Prediction Volume')
    ]
    ax2.legend(handles=legend_elements, loc='upper left', fontsize=10)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis dates
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{asset_name}_prediction_{timestamp}.png"
    filepath = os.path.join(asset_output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    print(f"Plot saved to: {filepath}")
    return filepath


def create_comparison_plot(predictions_dict, output_dir="output", show_plot=False):
    """
    Create comparison plot for multiple assets.
    
    Args:
        predictions_dict (dict): Dictionary with asset predictions
        output_dir (str): Output directory
        show_plot (bool): Whether to display the plot
    """
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    for (asset_name, pred_df), color in zip(predictions_dict.items(), colors):
        # Get the last predicted close price
        last_pred = pred_df['close'].iloc[-1]
        
        # Plot as a bar or point
        ax.bar(asset_name, last_pred, color=color, alpha=0.7, label=asset_name)
    
    ax.set_ylabel('Predicted Close Price', fontsize=12)
    ax.set_title('Comparison of 2-Week Price Predictions', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save comparison plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comparison_predictions_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    print(f"Comparison plot saved to: {filepath}")
    return filepath


def generate_prediction_report(historical_df, pred_df, asset_name, output_dir="output"):
    """
    Generate a detailed prediction report.
    
    Args:
        historical_df (pandas.DataFrame): Historical data
        pred_df (pandas.DataFrame): Prediction data
        asset_name (str): Asset name
        output_dir (str): Output directory
    """
    asset_output_dir = os.path.join(output_dir, asset_name)
    os.makedirs(asset_output_dir, exist_ok=True)
    
    # Calculate basic statistics
    last_historical = historical_df['close'].iloc[-1]
    pred_prices = pred_df['close']
    
    report = {
        'asset_name': asset_name,
        'last_historical_price': last_historical,
        'prediction_period': len(pred_df),
        'predicted_prices': [float(price) for price in pred_prices.tolist()],
        'prediction_dates': [f"Week {i+1}" for i in range(len(pred_df))],
        'price_change_pct': float((pred_prices.iloc[-1] - last_historical) / last_historical * 100),
        'avg_predicted_price': float(pred_prices.mean()),
        'min_predicted_price': float(pred_prices.min()),
        'max_predicted_price': float(pred_prices.max())
    }
    
    # Save report as JSON
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{asset_name}_report_{timestamp}.json"
    report_filepath = os.path.join(asset_output_dir, report_filename)
    
    with open(report_filepath, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to: {report_filepath}")
    return report_filepath