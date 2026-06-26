import abc
from typing import Any, Dict, Optional

class ClimateModel(abc.ABC):
    """
    Abstract Base Class for all Machine Learning models in the Digital Twin.
    Enforces a standard interface for training, prediction, and serialization.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model = None

    @abc.abstractmethod
    def train(self, X_train: Any, y_train: Any, X_val: Optional[Any] = None, y_val: Optional[Any] = None) -> Dict[str, Any]:
        """
        Train the model on the provided dataset.
        Returns training metrics (e.g. loss history).
        """
        pass

    @abc.abstractmethod
    def predict(self, X: Any) -> Any:
        """
        Generate predictions for the given input features.
        """
        pass

    @abc.abstractmethod
    def save(self, file_path: str) -> None:
        """
        Serialize and save the model to disk.
        """
        pass

    @abc.abstractmethod
    def load(self, file_path: str) -> None:
        """
        Load a serialized model from disk.
        """
        pass
