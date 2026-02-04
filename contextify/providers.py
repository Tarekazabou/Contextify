#!/usr/bin/env python3
"""
Provider registry for Contextify.
Defines available providers and model discovery.
"""

import subprocess
import requests
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class ProviderType(Enum):
    """Available provider types."""
    GITHUB_COPILOT = "github-copilot"
    GOOGLE_GEMINI = "google-gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL_PROXY = "local-proxy"


class ProviderRegistry:
    """Registry of available AI providers with model discovery."""
    
    # Curated model lists for providers (fallback when API discovery fails)
    CURATED_MODELS = {
        "github-copilot": [
            {"id": "gpt-4o", "name": "GPT-4o (Latest)", "contextWindow": 128000},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "contextWindow": 128000},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "contextWindow": 16384},
        ],
        "google-gemini": [
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "contextWindow": 1000000},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "contextWindow": 1000000},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "contextWindow": 1000000},
        ],
        "openai": [
            {"id": "gpt-4", "name": "GPT-4", "contextWindow": 8192},
            {"id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo", "contextWindow": 128000},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "contextWindow": 4096},
        ],
        "anthropic": [
            {"id": "claude-3-opus", "name": "Claude 3 Opus", "contextWindow": 200000},
            {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "contextWindow": 200000},
            {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "contextWindow": 200000},
        ],
    }
    
    PROVIDER_INFO = {
        ProviderType.GITHUB_COPILOT: {
            "name": "GitHub Copilot",
            "description": "Use GitHub Copilot models via device-flow authentication",
            "authType": "device-flow",
            "models": CURATED_MODELS["github-copilot"],
        },
        ProviderType.GOOGLE_GEMINI: {
            "name": "Google Gemini",
            "description": "Use Google Gemini models with API key",
            "authType": "api-key",
            "apiKeyEnvVar": "GEMINI_API_KEY",
            "getKeyUrl": "https://makersuite.google.com/app/apikey",
            "models": CURATED_MODELS["google-gemini"],
        },
        ProviderType.OPENAI: {
            "name": "OpenAI",
            "description": "Use OpenAI GPT models with API key",
            "authType": "api-key",
            "apiKeyEnvVar": "OPENAI_API_KEY",
            "getKeyUrl": "https://platform.openai.com/api-keys",
            "models": CURATED_MODELS["openai"],
        },
        ProviderType.ANTHROPIC: {
            "name": "Anthropic Claude",
            "description": "Use Anthropic Claude models with API key",
            "authType": "api-key",
            "apiKeyEnvVar": "ANTHROPIC_API_KEY",
            "getKeyUrl": "https://console.anthropic.com/",
            "models": CURATED_MODELS["anthropic"],
        },
        ProviderType.LOCAL_PROXY: {
            "name": "Local/Proxy Provider",
            "description": "Use local LLM or proxy endpoint (OpenAI-compatible /v1 API)",
            "authType": "optional",
            "models": [],
        },
    }
    
    @classmethod
    def get_available_providers(cls) -> List[Tuple[str, Dict[str, Any]]]:
        """Get list of available providers with info."""
        return [
            (provider_type.value, cls.PROVIDER_INFO[provider_type])
            for provider_type in ProviderType
        ]
    
    @classmethod
    def get_provider_info(cls, provider_type: ProviderType) -> Dict[str, Any]:
        """Get info for a specific provider."""
        return cls.PROVIDER_INFO.get(provider_type)
    
    @classmethod
    def discover_models(
        cls,
        provider: str,
        auth_token: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover available models for a provider.
        Falls back to curated list if discovery fails.
        
        Args:
            provider: Provider type (e.g., "github-copilot", "google-gemini")
            auth_token: Authentication token/API key
            endpoint_url: For local providers, the endpoint URL
        
        Returns:
            List of model dicts with 'id', 'name', and optional 'contextWindow'
        """
        
        # Try provider-specific discovery
        if provider == "github-copilot" and auth_token:
            models = cls._discover_copilot_models(auth_token)
            if models:
                return models
        
        elif provider == "google-gemini" and auth_token:
            models = cls._discover_gemini_models(auth_token)
            if models:
                return models
        
        elif provider == "local-proxy" and endpoint_url:
            models = cls._discover_openai_compat_models(endpoint_url, auth_token)
            if models:
                return models
        
        # Fall back to curated list
        return cls.CURATED_MODELS.get(provider, [])
    
    @staticmethod
    def _discover_copilot_models(auth_token: str) -> Optional[List[Dict[str, Any]]]:
        """Discover GitHub Copilot models available to the user."""
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            # Note: Actual Copilot API endpoint for model discovery might differ
            # This is a placeholder - adjust based on actual Copilot API
            response = requests.get(
                "https://api.githubcopilot.com/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                # Transform to standard format
                return [
                    {
                        "id": m.get("id", m.get("model")),
                        "name": m.get("name", m.get("id")),
                        "contextWindow": m.get("contextWindow", m.get("max_tokens", 128000))
                    }
                    for m in models
                ]
        except (requests.RequestException, ValueError, KeyError):
            pass
        
        return None
    
    @staticmethod
    def _discover_gemini_models(api_key: str) -> Optional[List[Dict[str, Any]]]:
        """Discover Google Gemini models available to the user."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # List available models
            models_gen = genai.list_models()
            models = []
            
            for model in models_gen:
                if "generateContent" in model.supported_generation_methods:
                    models.append({
                        "id": model.name.replace("models/", ""),
                        "name": model.name.replace("models/", "").title(),
                        "contextWindow": getattr(model, "input_token_limit", 32000)
                    })
            
            return models if models else None
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def _discover_openai_compat_models(
        endpoint_url: str,
        api_key: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Discover models from OpenAI-compatible endpoint."""
        try:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # Ensure endpoint_url ends with /v1
            if not endpoint_url.endswith("/v1"):
                endpoint_url = endpoint_url.rstrip("/") + "/v1"
            
            response = requests.get(
                f"{endpoint_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                
                return [
                    {
                        "id": m.get("id"),
                        "name": m.get("id", "Unknown"),
                        "contextWindow": m.get("context_window", 4096)
                    }
                    for m in models
                    if m.get("id")
                ]
        except (requests.RequestException, ValueError, KeyError):
            pass
        
        return None
    
    @staticmethod
    def test_endpoint(endpoint_url: str, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """
        Test connectivity to an endpoint.
        Returns (success, message).
        """
        try:
            # Ensure endpoint_url ends with /v1
            if not endpoint_url.endswith("/v1"):
                endpoint_url = endpoint_url.rstrip("/") + "/v1"
            
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.get(
                f"{endpoint_url}/models",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return True, f"✓ Endpoint is reachable"
            else:
                return False, f"✗ Endpoint returned status {response.status_code}"
        
        except requests.ConnectionError:
            return False, f"✗ Cannot connect to {endpoint_url} (connection refused)"
        except requests.Timeout:
            return False, f"✗ Endpoint request timed out"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"


def get_provider_choice_text() -> str:
    """Get formatted text for provider selection."""
    lines = ["Select an authentication provider:\n"]
    for provider_type, info in ProviderRegistry.get_available_providers():
        lines.append(f"  {provider_type:20} - {info['description']}")
    return "\n".join(lines)
