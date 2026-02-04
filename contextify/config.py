#!/usr/bin/env python3
"""
Configuration management for Contextify.
Handles XDG paths, config loading/saving, and defaults.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages Contextify configuration with XDG directory support."""
    
    DEFAULT_CONFIG = {
        "agents": {
            "defaults": {
                "model": {
                    "primary": None,  # Will be set during onboarding
                    "fallbacks": []
                }
            }
        },
        "models": {
            "mode": "merge",  # "merge" = local + cloud providers, "replace" = only configured providers
            "providers": {}
        },
        "paths": {
            "configDir": None,  # Filled in dynamically
            "dataDir": None
        }
    }
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.data_dir = self._get_data_dir()
        self.config_file = self.config_dir / "config.json"
        self.auth_index_file = self.config_dir / "auth.json"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create default
        self.config = self._load_config()
    
    @staticmethod
    def _get_config_dir() -> Path:
        """Get config directory following XDG conventions."""
        # Primary: $XDG_CONFIG_HOME/contextify
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            return Path(xdg_config) / "contextify"
        
        # Secondary: ~/.config/contextify (XDG default)
        home = Path.home()
        xdg_default = home / ".config" / "contextify"
        if xdg_default.exists() or not (home / ".contextify").exists():
            return xdg_default
        
        # Fallback: ~/.contextify (backward compatibility)
        return home / ".contextify"
    
    @staticmethod
    def _get_data_dir() -> Path:
        """Get data directory following XDG conventions."""
        # Primary: $XDG_DATA_HOME/contextify
        xdg_data = os.environ.get('XDG_DATA_HOME')
        if xdg_data:
            return Path(xdg_data) / "contextify"
        
        # Fallback: ~/.local/share/contextify (XDG default)
        return Path.home() / ".local" / "share" / "contextify"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load config from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all required keys exist
                    return self._merge_configs(self.DEFAULT_CONFIG, config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARN] Failed to load config: {e}, using defaults")
                return self.DEFAULT_CONFIG.copy()
        
        return self.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def _merge_configs(defaults: Dict, overrides: Dict) -> Dict:
        """Deep merge overrides into defaults, preserving all default keys."""
        result = defaults.copy()
        for key, value in overrides.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self) -> bool:
        """Save current config to file."""
        try:
            # Update path info
            self.config["paths"]["configDir"] = str(self.config_dir)
            self.config["paths"]["dataDir"] = str(self.data_dir)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Ensure config file has restricted permissions (owner read/write only)
            self.config_file.chmod(0o600)
            return True
        except IOError as e:
            print(f"[ERROR] Failed to save config: {e}")
            return False
    
    def get_model_config(self) -> Optional[Dict[str, Any]]:
        """Get current model configuration."""
        return self.config.get("agents", {}).get("defaults", {}).get("model")
    
    def set_model_config(self, primary: str, fallbacks: Optional[list] = None) -> None:
        """Set default model configuration."""
        if "agents" not in self.config:
            self.config["agents"] = {}
        if "defaults" not in self.config["agents"]:
            self.config["agents"]["defaults"] = {}
        if "model" not in self.config["agents"]["defaults"]:
            self.config["agents"]["defaults"]["model"] = {}
        
        self.config["agents"]["defaults"]["model"]["primary"] = primary
        self.config["agents"]["defaults"]["model"]["fallbacks"] = fallbacks or []
    
    def get_providers(self) -> Dict[str, Any]:
        """Get configured providers."""
        return self.config.get("models", {}).get("providers", {})
    
    def set_provider(self, provider_name: str, provider_config: Dict[str, Any]) -> None:
        """Add or update provider configuration."""
        if "models" not in self.config:
            self.config["models"] = {"mode": "merge", "providers": {}}
        if "providers" not in self.config["models"]:
            self.config["models"]["providers"] = {}
        
        self.config["models"]["providers"][provider_name] = provider_config
    
    def get_provider(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get specific provider configuration."""
        return self.config.get("models", {}).get("providers", {}).get(provider_name)
    
    def get_default_model(self) -> Optional[str]:
        """Get the configured default model."""
        return self.get_model_config().get("primary") if self.get_model_config() else None
    
    def has_valid_config(self) -> bool:
        """Check if config has a valid default model set."""
        return bool(self.get_default_model())


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config_dir() -> Path:
    """Get the Contextify config directory path."""
    return get_config_manager().config_dir


def get_data_dir() -> Path:
    """Get the Contextify data directory path."""
    return get_config_manager().data_dir
