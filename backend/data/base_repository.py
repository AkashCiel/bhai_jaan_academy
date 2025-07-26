from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os

class BaseRepository(ABC):
    """Base repository class providing common data access patterns"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def _ensure_file_exists(self) -> None:
        """Ensure the data file exists with proper structure"""
        if not os.path.exists(self.file_path):
            self._create_initial_file()
    
    def _create_initial_file(self) -> None:
        """Create initial file with default structure"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self._get_default_data(), f, indent=2)
    
    @abstractmethod
    def _get_default_data(self) -> Any:
        """Return default data structure for the repository"""
        pass
    
    def _load_data(self) -> Any:
        """Load data from file"""
        self._ensure_file_exists()
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def _save_data(self, data: Any) -> None:
        """Save data to file"""
        self._ensure_file_exists()
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2) 