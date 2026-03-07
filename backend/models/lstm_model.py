"""
LSTM (Long Short-Term Memory) Neural Network Model
Deep learning approach for complex time series patterns.
Captures long-term dependencies and non-linear relationships.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class LSTMModel:
    """
    LSTM neural network for time series forecasting.
    Deep learning model capturing complex temporal patterns.
    
    Features:
    - Multi-layer LSTM architecture
    - Dropout regularization to prevent overfitting
    - Normalized input features
    - Sequence-to-sequence learning
    - Flexible sequence length
    """
    
    def __init__(self, sequence_length: int = 7):
        """
        Initialize LSTM model.
        
        Args:
            sequence_length: Number of time steps for LSTM input
        """
        self.model = None
        self.sequence_length = sequence_length
        self.scaler_mean = None
        self.scaler_std = None
        self.history = []
        self.metadata = {}
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit LSTM model on time series data.
        
        Args:
            dates: List of date strings
            values: List of sales values
        """
        if not TENSORFLOW_AVAILABLE:
            self.metadata = {
                "status": "tensorflow_not_available",
                "message": "TensorFlow/Keras not installed"
            }
            return
        
        values_array = np.array(values, dtype=float)
        
        if len(values_array) < self.sequence_length + 1:
            self.metadata = {
                "status": "insufficient_data",
                "message": f"Need at least {self.sequence_length + 1} data points for LSTM"
            }
            return
        
        # Normalize data
        self.scaler_mean = np.mean(values_array)
        self.scaler_std = np.std(values_array)
        if self.scaler_std == 0:
            self.scaler_std = 1
        
        normalized = (values_array - self.scaler_mean) / self.scaler_std
        self.history = normalized.tolist()
        
        # Create sequences
        X, y = self._create_sequences(normalized)
        
        if len(X) < 2:
            self.metadata = {
                "status": "insufficient_sequences",
                "message": "Could not create enough sequences for training"
            }
            return
        
        # Build LSTM model
        self.model = Sequential([
            LSTM(64, activation='relu', input_shape=(self.sequence_length, 1), return_sequences=True),
            Dropout(0.2),
            LSTM(32, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
        
        # Train model
        self.model.fit(
            X, y,
            epochs=50,
            batch_size=8,
            verbose=0,
            validation_split=0.2
        )
        
        self.metadata = {
            "type": "LSTM",
            "architecture": "2-layer LSTM with dropout",
            "sequence_length": self.sequence_length,
            "data_points_used": len(values_array),
            "sequences_trained": len(X),
            "message": "Deep learning model capturing temporal dependencies"
        }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast using LSTM.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Tuple of (forecast, lower_bound, upper_bound)
        """
        if self.model is None or not self.history:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "lstm",
                "trend": "stable",
                "seasonality": "none"
            }
        
        forecast_values = []
        current_sequence = np.array(self.history[-self.sequence_length:])
        
        for _ in range(horizon):
            # Predict next value
            input_seq = current_sequence.reshape(1, self.sequence_length, 1)
            pred_normalized = self.model.predict(input_seq, verbose=0)[0, 0]
            
            # Denormalize
            pred = pred_normalized * self.scaler_std + self.scaler_mean
            forecast_values.append(pred)
            
            # Update sequence
            current_sequence = np.concatenate([current_sequence[1:], [pred_normalized]])
        
        # Confidence intervals (±20% for neural networks)
        lower_bounds = [v * 0.80 for v in forecast_values]
        upper_bounds = [v * 1.20 for v in forecast_values]
        
        return {
            "forecast": forecast_values,
            "lower": lower_bounds,
            "upper": upper_bounds,
            "model_name": "lstm",
            "trend": "stable",
            "seasonality": "none"
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i+self.sequence_length])
            y.append(data[i+self.sequence_length])
        
        return np.array(X).reshape(-1, self.sequence_length, 1), np.array(y)
