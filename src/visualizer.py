import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta


def plot_predictions(historical_df, pred_df, asset_name, output_dir="output", show_plot=False):
    """
    Create and save visualization of predictions.
    
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
    
    # Plot close prices
    ax1.plot(historical_df.index, historical_df['close'], 
             label='Historical', color='blue', linewidth=2, alpha=0.8)
    ax1.plot(pred_df.index, pred_df['close'], 
             label='Predicted', color='red', linewidth=2, linestyle='--')
    ax1.set_ylabel('Close Price', fontsize=12)
    ax1.set_title(f'{asset_name} - Price Prediction (Next 2 Weeks)', fontsize=14)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot volume
    ax2.plot(historical_df.index, historical_df['volume'], 
             label='Historical Volume', color='green', linewidth=1, alpha=0.7)
    ax2.plot(pred_df.index, pred_df['volume'], 
             label='Predicted Volume', color='orange', linewidth=1, linestyle='--')
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.legend(fontsize=10)
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
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(predictions_dict)))
    
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