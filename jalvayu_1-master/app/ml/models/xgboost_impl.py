from typing import Any, Dict, Optional
import os
from loguru import logger

from app.ml.models.base import ClimateModel

class XGBoostModel(ClimateModel):
    """
    XGBoost implementation for gridded climate prediction.
    Uses lazy loading for heavy dependencies.
    """

    def train(self, X_train: Any, y_train: Any, X_val: Optional[Any] = None, y_val: Optional[Any] = None) -> Dict[str, Any]:
        import xgboost as xgb # Lazy load
        
        logger.info("Initializing XGBoost training...")
        
        dtrain = xgb.DMatrix(X_train, label=y_train)
        evals = [(dtrain, 'train')]
        
        if X_val is not None and y_val is not None:
            dval = xgb.DMatrix(X_val, label=y_val)
            evals.append((dval, 'eval'))

        params = self.config.get("params", {
            "objective": "reg:squarederror",
            "eval_metric": "rmse",
            "max_depth": 6,
            "learning_rate": 0.1
        })
        num_boost_round = self.config.get("num_boost_round", 100)
        
        evals_result = {}
        self.model = xgb.train(
            params,
            dtrain,
            num_boost_round=num_boost_round,
            evals=evals,
            evals_result=evals_result,
            verbose_eval=False
        )
        
        logger.info("XGBoost training completed.")
        return {"evals_result": evals_result}

    def predict(self, X: Any) -> Any:
        import xgboost as xgb # Lazy load
        if not self.model:
            raise ValueError("Model is not loaded or trained.")
            
        dtest = xgb.DMatrix(X)
        return self.model.predict(dtest)

    def save(self, file_path: str) -> None:
        if not self.model:
            raise ValueError("No model to save.")
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # XGBoost natively supports saving to json/bin
        self.model.save_model(file_path)
        logger.info(f"Model saved to {file_path}")

    def load(self, file_path: str) -> None:
        import xgboost as xgb # Lazy load
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Model file not found: {file_path}")
            
        self.model = xgb.Booster()
        self.model.load_model(file_path)
        logger.info(f"Model loaded from {file_path}")
