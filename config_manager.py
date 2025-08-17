import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_default_config()
        self.load()
    
    def _load_default_config(self):
        return {
            "actions": {
                "up": {"type": "folder", "name": "Manybe"},
                "down": {"type": "recycle", "name": "Delete"},
                "left": {"type": "folder", "name": "Core"},
                "right": {"type": "folder", "name": "Scraps"}
            },
            "window": {
                "fullscreen": False,
                "background_color": "#000000",
                "width": 1200,
                "height": 800
            },
            "search_subfolders": False
        }
    
    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
    
    def save(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get_action(self, direction):
        return self.config["actions"].get(direction, {"type": "folder", "name": "Unknown"})
    
    def set_action(self, direction, action_type, name):
        self.config["actions"][direction] = {"type": action_type, "name": name}
        self.save()
    
    def set_action_name(self, direction, name):
        if name.lower() == "delete":
            action_type = "recycle"
        else:
            action_type = "folder"
        self.set_action(direction, action_type, name)
    
    def get_window_config(self):
        return self.config["window"]
    
    def get_search_subfolders(self):
        return self.config.get("search_subfolders", False)
    
    def set_search_subfolders(self, value):
        self.config["search_subfolders"] = value
        self.save()