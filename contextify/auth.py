#!/usr/bin/env python3
"""
Authentication storage for Contextify.
Handles secure credential storage via OS keyring with file fallback.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import keyring
    from keyring.errors import KeyringError
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False
    KeyringError = Exception


class AuthManager:
    """Manages authentication profiles and credential storage."""
    
    KEYRING_SERVICE_NAME = "contextify"
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.auth_index_file = config_dir / "auth.json"
        self.auth_index = self._load_auth_index()
    
    def _load_auth_index(self) -> Dict[str, Any]:
        """Load auth index from file (non-secret metadata)."""
        if self.auth_index_file.exists():
            try:
                with open(self.auth_index_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"profiles": {}}
        return {"profiles": {}}
    
    def _save_auth_index(self) -> bool:
        """Save auth index to file with restricted permissions."""
        try:
            with open(self.auth_index_file, 'w') as f:
                json.dump(self.auth_index, f, indent=2)
            self.auth_index_file.chmod(0o600)  # rw-------
            return True
        except IOError as e:
            print(f"[ERROR] Failed to save auth index: {e}")
            return False
    
    def save_credential(self, profile_name: str, secret_value: str) -> bool:
        """
        Save credential (token, API key, etc.) to keyring with file fallback.
        Returns True on success.
        """
        keyring_entry = f"{self.KEYRING_SERVICE_NAME}-{profile_name}"
        
        # Try keyring first
        if HAS_KEYRING:
            try:
                keyring.set_password(self.KEYRING_SERVICE_NAME, profile_name, secret_value)
                return True
            except (KeyringError, Exception) as e:
                print(f"[WARN] Keyring unavailable, falling back to file storage: {e}")
        
        # Fallback: store in auth file with restricted permissions
        if "credentials" not in self.auth_index:
            self.auth_index["credentials"] = {}
        
        # WARNING: This stores the secret in plaintext in a file!
        # Consider adding encryption if secrets are sensitive.
        self.auth_index["credentials"][profile_name] = secret_value
        return self._save_auth_index()
    
    def get_credential(self, profile_name: str) -> Optional[str]:
        """
        Retrieve credential from keyring with file fallback.
        Returns the secret value or None if not found.
        """
        # Try keyring first
        if HAS_KEYRING:
            try:
                secret = keyring.get_password(self.KEYRING_SERVICE_NAME, profile_name)
                if secret:
                    return secret
            except (KeyringError, Exception):
                pass
        
        # Fallback: try file storage
        credentials = self.auth_index.get("credentials", {})
        return credentials.get(profile_name)
    
    def delete_credential(self, profile_name: str) -> bool:
        """Delete credential from keyring and file fallback."""
        deleted = False
        
        # Try keyring
        if HAS_KEYRING:
            try:
                keyring.delete_password(self.KEYRING_SERVICE_NAME, profile_name)
                deleted = True
            except (KeyringError, Exception):
                pass
        
        # Try file
        if profile_name in self.auth_index.get("credentials", {}):
            del self.auth_index["credentials"][profile_name]
            self._save_auth_index()
            deleted = True
        
        return deleted
    
    def create_profile(
        self,
        profile_name: str,
        provider: str,
        profile_type: str,  # e.g., "api-key", "device-token", "oauth2"
        secret_value: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create an authentication profile with metadata and secret.
        Saves credential to secure storage and metadata to auth index.
        """
        # Save the secret
        if not self.save_credential(profile_name, secret_value):
            return False
        
        # Save metadata (non-secret)
        profile_data = {
            "provider": provider,
            "type": profile_type,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "keyringEntry": f"{self.KEYRING_SERVICE_NAME}-{profile_name}"
        }
        
        if metadata:
            profile_data.update(metadata)
        
        self.auth_index["profiles"][profile_name] = profile_data
        return self._save_auth_index()
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get profile metadata (does NOT include the secret)."""
        return self.auth_index.get("profiles", {}).get(profile_name)
    
    def list_profiles(self, provider: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        List all auth profiles, optionally filtered by provider.
        Returns profile name -> metadata mappings (secrets NOT included).
        """
        profiles = self.auth_index.get("profiles", {})
        
        if provider:
            return {
                name: data for name, data in profiles.items()
                if data.get("provider") == provider
            }
        
        return profiles
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete entire profile (both secret and metadata)."""
        # Delete credential
        self.delete_credential(profile_name)
        
        # Delete metadata
        if profile_name in self.auth_index.get("profiles", {}):
            del self.auth_index["profiles"][profile_name]
            return self._save_auth_index()
        
        return True
    
    def profile_exists(self, profile_name: str) -> bool:
        """Check if profile exists."""
        return profile_name in self.auth_index.get("profiles", {})


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager(config_dir: Optional[Path] = None) -> AuthManager:
    """Get or create the global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        if config_dir is None:
            from .config import get_config_dir
            config_dir = get_config_dir()
        _auth_manager = AuthManager(config_dir)
    return _auth_manager
