import pandas as pd
import torch
import sys
import os

# Add project root directory to path to import Kronos modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import from model package
from model.kronos import Kronos, KronosTokenizer, KronosPredictor


class KronosPredictorWrapper:
    """
    Wrapper class for Kronos prediction functionality.
    """
    
    def __init__(self, model_name="NeoQuasar/Kronos-small", device="cuda:0" if torch.cuda.is_available() else "cpu"):
        """
        Initialize the Kronos predictor.
        
        Args:
            model_name (str): Name of the pre-trained Kronos model
            device (str): Device to run the model on
        """
        self.device = device
        self.model_name = model_name
        
        # Load tokenizer and model from HuggingFace Hub
        # Tokenizer and model are in separate repositories
        self.tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
        self.model = Kronos.from_pretrained(model_name)
        
        # Initialize predictor
        self.predictor = KronosPredictor(
            self.model, 
            self.tokenizer, 
            device=device, 
            max_context=512
        )
        
        print(f"Kronos predictor initialized with model: {model_name}")
        print(f"Using device: {device}")
    
    def prepare_prediction_data(self, df, lookback_weeks=50, pred_weeks=2):
        """
        Prepare data for prediction by selecting the lookback window.
        
        Args:
            df (pandas.DataFrame): Input data with timestamps and OHLCV data
            lookback_weeks (int): Number of weeks to use for lookback
            pred_weeks (int): Number of weeks to predict
            
        Returns:
            tuple: (x_df, x_timestamp, y_timestamp)
        """
        # Ensure we have enough data
        if len(df) < lookback_weeks + pred_weeks:
            raise ValueError(f"Not enough data. Need at least {lookback_weeks + pred_weeks} weeks, got {len(df)}")
        
        # Use the most recent data for prediction
        x_df = df.iloc[-lookback_weeks:].copy()
        
        # Extract timestamps for input and prediction periods
        x_timestamp = x_df['timestamps']
        
        # For y_timestamp, we need to use actual historical timestamps from the next period
        # KronosPredictor expects actual timestamps, not generated future ones
        y_timestamp = df['timestamps'].iloc[-pred_weeks:]
        
        return x_df[['open', 'high', 'low', 'close', 'volume', 'amount']], x_timestamp, y_timestamp
    
    def predict(self, df, lookback_weeks=50, pred_weeks=2, T=1.0, top_p=0.9, sample_count=1):
        """
        Make predictions using the Kronos model.
        
        Args:
            df (pandas.DataFrame): Input data
            lookback_weeks (int): Number of weeks to look back
            pred_weeks (int): Number of weeks to predict
            T (float): Temperature for sampling
            top_p (float): Top-p sampling parameter
            sample_count (int): Number of samples to generate
            
        Returns:
            pandas.DataFrame: Prediction results
        """
        # Prepare data for prediction
        x_df, x_timestamp, y_timestamp = self.prepare_prediction_data(df, lookback_weeks, pred_weeks)
        
        # Make prediction
        pred_df = self.predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_weeks,
            T=T,
            top_p=top_p,
            sample_count=sample_count,
            verbose=True
        )
        
        return pred_df
    
    def predict_multiple_assets(self, data_dict, lookback_weeks=50, pred_weeks=2):
        """
        Predict multiple assets.
        
        Args:
            data_dict (dict): Dictionary with asset symbols and DataFrames
            lookback_weeks (int): Number of weeks to look back
            pred_weeks (int): Number of weeks to predict
            
        Returns:
            dict: Dictionary with asset symbols and prediction DataFrames
        """
        predictions = {}
        
        for symbol, df in data_dict.items():
            try:
                print(f"\nPredicting for {symbol}...")
                pred_df = self.predict(df, lookback_weeks, pred_weeks)
                predictions[symbol] = pred_df
                print(f"Successfully predicted {pred_weeks} weeks for {symbol}")
                
            except Exception as e:
                print(f"Error predicting for {symbol}: {e}")
        
        return predictions