"""
LSTM (Long Short-Term Memory) Neural Network Model
Deep learning approach for complex time series patterns.
Captures long-term dependencies and non-linear relationships.
Improved with better architecture, early stopping, and regularization.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    from tensorflow.keras.regularizers import l1_l2
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class LSTMModel:
    """
    LSTM neural network for time series forecasting.
    Deep learning model capturing complex temporal patterns.
    
    Features:
    - Multi-layer LSTM architecture with batch normalization
    - Dropout and L1/L2 regularization to prevent overfitting
    - Early stopping to avoid training beyond optimal point
    - Normalized input features
    - Sequence-to-sequence learning
    - Adaptive sequence length based on data
    - Robust confidence interval estimation
    """
    
    def __init__(self, sequence_length: int = None):
        """
        Initialize LSTM model.
        
        Args:
            sequence_length: Number of time steps for LSTM input (auto-selected if None)
        """
        self.model = None
        self.sequence_length = sequence_length
        self.scaler_mean = None
        self.scaler_std = None
        self.history = []
        self.metadata = {}
        self.training_std = None
    
    def _select_sequence_length(self, data_length: int) -> int:
        """
        Auto-select optimal sequence length based on data length.
        
        Args:
            data_length: Number of data points
            
        Returns:
            Optimal sequence length
        """
        if data_length < 10:
            return min(3, data_length - 1)
        elif data_length < 30:
            return 5
        elif data_length < 50:
            return 7
        else:
            return min(14, data_length // 5)
    
    def fit(self, dates: List[str], values: List[float]) -> None:
        """
        Fit LSTM model on time series data with robust error handling.
        
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
        
        # Validate and clean input
        try:
            values_array = np.array([v for v in values if isinstance(v, (int, float)) and np.isfinite(v)], dtype=float)
            
            if len(values_array) < 3:
                self.metadata = {
                    "status": "insufficient_data",
                    "message": f"Need at least 3 valid data points for LSTM (have {len(values_array)})"
                }
                return
            
            # Auto-select sequence length if not specified
            if self.sequence_length is None:
                self.sequence_length = self._select_sequence_length(len(values_array))
            
            if len(values_array) < self.sequence_length + 1:
                self.sequence_length = max(1, len(values_array) - 2)
            
            # Normalize data with robust scaling
            self.scaler_mean = np.mean(values_array)
            self.scaler_std = np.std(values_array)
            if self.scaler_std == 0:
                self.scaler_std = 1
            
            normalized = (values_array - self.scaler_mean) / self.scaler_std
            self.history = normalized.tolist()
            self.training_std = np.std(values_array)
            
            # Create sequences
            X, y = self._create_sequences(normalized)
            
            if len(X) < 2:
                self.metadata = {
                    "status": "insufficient_sequences",
                    "message": f"Could not create enough sequences for training (created {len(X)})"
                }
                return
            
            # Determine architecture based on data size
            n_units_layer1 = min(64, max(16, len(X)))
            n_units_layer2 = min(32, max(8, len(X) // 2))
            
            # Build LSTM model with batch normalization
            self.model = Sequential([
                LSTM(n_units_layer1, activation='relu', input_shape=(self.sequence_length, 1), 
                     return_sequences=True, kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
                BatchNormalization(),
                Dropout(0.2),
                LSTM(n_units_layer2, activation='relu', return_sequences=False,
                     kernel_regularizer=l1_l2(l1=1e-5, l2=1e-4)),
                BatchNormalization(),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dense(1)
            ])
            
            # Compile with optimized settings
            self.model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mse',
                metrics=['mae']
            )
            
            # Train model with early stopping
            early_stop = EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            )
            
            epochs = min(100, max(30, len(X) * 2))
            batch_size = max(1, len(X) // 8)
            
            self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                verbose=0,
                validation_split=0.2,
                callbacks=[early_stop]
            )
            
            self.metadata = {
                "type": "LSTM",
                "architecture": "2-layer LSTM with batch normalization and dropout",
                "sequence_length": self.sequence_length,
                "data_points_used": len(values_array),
                "sequences_trained": len(X),
                "status": "trained",
                "message": "Deep learning model capturing complex temporal dependencies"
            }
        except Exception as e:
            self.metadata = {
                "status": "training_failed",
                "message": f"Failed to train LSTM: {str(e)}"
            }
    
    def forecast(self, horizon: int) -> Dict[str, Any]:
        """
        Generate forecast using LSTM with estimated confidence intervals.
        
        Args:
            horizon: Number of days to forecast
            
        Returns:
            Dictionary with forecast data and metadata
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
        
        try:
            forecast_values = []
            current_sequence = np.array(self.history[-self.sequence_length:])
            
            for _ in range(horizon):
                # Predict next value
                input_seq = current_sequence.reshape(1, self.sequence_length, 1)
                pred_normalized = self.model.predict(input_seq, verbose=0)[0, 0]
                
                # Denormalize
                pred = float(pred_normalized * self.scaler_std + self.scaler_mean)
                forecast_values.append(max(0, pred))
                
                # Update sequence for next prediction
                current_sequence = np.concatenate([current_sequence[1:], [pred_normalized]])
            
            # Estimate confidence intervals based on training data variability
            # Use proportional bounds that increase with forecast horizon
            std_dev = self.training_std if self.training_std else np.std(forecast_values) if forecast_values else 1
            
            lower_bounds = []
            upper_bounds = []
            
            for i, pred in enumerate(forecast_values):
                # Confidence interval widens with horizon
                horizon_factor = 1 + (i / horizon * 0.5)
                margin = 1.96 * std_dev * horizon_factor * 0.1  # ~20% at start, ~30% at end
                lower_bounds.append(max(0, pred - margin))
                upper_bounds.append(pred + margin)
            
            return {
                "forecast": forecast_values,
                "lower": lower_bounds,
                "upper": upper_bounds,
                "model_name": "lstm",
                "trend": self._detect_trend(forecast_values),
                "seasonality": "none"
            }
        except Exception as e:
            return {
                "forecast": [np.nan] * horizon,
                "lower": [np.nan] * horizon,
                "upper": [np.nan] * horizon,
                "model_name": "lstm",
                "error": str(e)
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get model metadata and analysis."""
        return self.metadata
    
    def _detect_trend(self, forecast_values: List[float]) -> str:
        """Detect trend from forecast values."""
        if len(forecast_values) < 2:
            return "stable"
        
        # Compare first third and last third
        third = len(forecast_values) // 3
        first_avg = np.mean(forecast_values[:third]) if third > 0 else forecast_values[0]
        last_avg = np.mean(forecast_values[-third:]) if third > 0 else forecast_values[-1]
        
        if first_avg == 0:
            return "stable"
        
        change_pct = (last_avg - first_avg) / first_avg
        
        if change_pct > 0.05:
            return "upward"
        elif change_pct < -0.05:
            return "downward"
        else:
            return "stable"
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training."""
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i+self.sequence_length])
            y.append(data[i+self.sequence_length])
        
        return np.array(X).reshape(-1, self.sequence_length, 1), np.array(y)
