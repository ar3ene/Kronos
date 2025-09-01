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
        print("Loading tokenizer...")
        self.tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
        print("Loading model...")
        self.model = Kronos.from_pretrained(model_name)
        
        # Initialize predictor
        print("Initializing predictor...")
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
            tuple: (x_df, x_timestamp, y_timestamp, actual_validation_data)
        """
        # Always use validation mode: train on t0-4w之前的数据，预测t0-4w到t0+4w
        total_weeks_needed = lookback_weeks + pred_weeks
        if len(df) < total_weeks_needed:
            raise ValueError(f"Not enough data. Need at least {total_weeks_needed} weeks, got {len(df)}")
        
        # Training data: t0-4w之前的所有数据（比如t0-56w到t0-4w）
        x_df = df.iloc[-total_weeks_needed:-pred_weeks//2].copy()
        
        # Prediction period: t0-4w to t0+4w (8 weeks)
        # We need future timestamps for the prediction period
        # Use available data for first half, generate future dates for second half
        available_future = df['timestamps'].iloc[-pred_weeks//2:].copy()
        
        # Generate future dates for the prediction beyond available data
        if len(available_future) < pred_weeks:
            last_timestamp = available_future.iloc[-1] if len(available_future) > 0 else df['timestamps'].iloc[-1]
            future_weeks = pred_weeks - len(available_future)
            future_dates = pd.date_range(start=last_timestamp + pd.Timedelta(weeks=1), 
                                       periods=future_weeks, 
                                       freq='W')
            y_timestamp = pd.concat([available_future, pd.Series(future_dates)])
        else:
            y_timestamp = available_future.iloc[:pred_weeks]
        
        # Actual data for validation: t0-4w to t0 (4 weeks)
        actual_validation_data = df.iloc[-pred_weeks//2:].copy()
        
        # Extract timestamps for input period
        x_timestamp = x_df['timestamps']
        
        return x_df[['open', 'high', 'low', 'close', 'volume', 'amount']], x_timestamp, y_timestamp, actual_validation_data
    
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
            tuple: (pred_df, actual_validation_data)
        """
        # Prepare data for prediction
        x_df, x_timestamp, y_timestamp, actual_validation_data = self.prepare_prediction_data(
            df, lookback_weeks, pred_weeks
        )
        
        # Make prediction using the original KronosPredictor
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
        
        return pred_df, actual_validation_data