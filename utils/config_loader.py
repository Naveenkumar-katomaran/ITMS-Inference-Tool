import json
import os
from utils.paths import resolve_path

class ConfigLoader:
    def __init__(self, config_name="config.json"):
        # Resolve config path relative to application root
        self.config_path = resolve_path(config_name)
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            # Fallback to local if not found in root (unlikely but safe)
            if os.path.exists("config.json"):
                self.config_path = os.path.abspath("config.json")
            else:
                raise FileNotFoundError(f"Config file not found at: {self.config_path}")
        
        with open(self.config_path, "r") as f:
            return json.load(f)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

# Singleton instance
_instance = None

def get_config(reload=False):
    global _instance
    if _instance is None or reload:
        _instance = ConfigLoader()
    return _instance
