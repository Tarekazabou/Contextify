#!/usr/bin/env python3
"""
Interactive onboarding wizard for Contextify.
Guides users through provider setup and model selection.
"""

import sys
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from .config import ConfigManager, get_config_manager
from .auth import AuthManager, get_auth_manager
from .providers import ProviderRegistry, ProviderType


# Windows-safe print function to handle Unicode
def safe_print(text: str) -> None:
    """Print text with fallback for Windows encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters with ASCII equivalents
        replacements = {
            '📋': '[CONFIG]',
            '📦': '[STEP]',
            '🔐': '[AUTH]',
            '🔍': '[SEARCH]',
            '💾': '[SAVE]',
            '✓': '[OK]',
            '✗': '[X]',
        }
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
        try:
            print(text.encode('ascii', 'replace').decode('ascii'))
        except:
            print(text.encode('cp1252', 'replace').decode('cp1252'))


class OnboardingWizard:
    """Interactive onboarding wizard for setting up providers and models."""
    
    def __init__(self, config_manager: ConfigManager, auth_manager: AuthManager):
        self.config = config_manager
        self.auth = auth_manager
        self.selected_provider = None
        self.selected_model = None
        self.auth_token = None
    
    def run_interactive(self) -> bool:
        """
        Run the full interactive onboarding flow.
        Returns True on success, False on cancel/failure.
        """
        print("\n" + "="*70)
        print("  CONTEXTIFY ONBOARDING WIZARD")
        print("="*70)
        print("\nWelcome! Let's set up your AI provider and model.\n")
        
        # Step 1: Show existing config
        if self.config.has_valid_config():
            safe_print("📋 Current Configuration:")
            current_model = self.config.get_default_model()
            print(f"   Default Model: {current_model}")
            choice = self._prompt_choice(
                "Would you like to:",
                [
                    ("Keep current config", "keep"),
                    ("Configure a new provider", "new"),
                    ("Exit", "exit")
                ]
            )
            if choice == "keep":
                return True
            elif choice == "exit":
                return False
        
        # Step 2: Select provider
        if not self._select_provider():
            return False
        
        # Step 3: Authenticate with provider
        if not self._authenticate_provider():
            return False
        
        # Step 4: Discover and select model
        if not self._discover_and_select_model():
            return False
        
        # Step 5: Test connectivity
        if not self._test_connectivity():
            print("[WARN] Connectivity test failed, but continuing...")
        
        # Step 6: Save configuration
        if not self._save_configuration():
            return False
        
        # Step 7: Summary
        self._show_summary()
        return True
    
    def _select_provider(self) -> bool:
        """Step 2: Select a provider."""
        safe_print("\n📦 Step 1: Select Provider")
        print("-" * 70)
        
        providers = [
            ("GitHub Copilot", "github-copilot"),
            ("Google Gemini", "google-gemini"),
            ("OpenAI", "openai"),
            ("Anthropic Claude", "anthropic"),
            ("Local/Proxy Provider", "local-proxy"),
        ]
        
        choice = self._prompt_choice(
            "Which provider would you like to use?",
            providers
        )
        
        if not choice:
            return False
        
        self.selected_provider = choice
        provider_info = ProviderRegistry.PROVIDER_INFO.get(ProviderType(choice))
        
        if provider_info:
            safe_print(f"\n✓ Selected: {provider_info['name']}")
            print(f"  {provider_info['description']}")
        
        return True
    
    def _authenticate_provider(self) -> bool:
        """Step 3: Authenticate with the selected provider."""
        safe_print("\n🔐 Step 2: Authentication")
        print("-" * 70)
        
        provider = self.selected_provider
        
        if provider == "github-copilot":
            return self._auth_github_copilot()
        elif provider == "google-gemini":
            return self._auth_api_key("google-gemini", "GEMINI_API_KEY", "https://makersuite.google.com/app/apikey")
        elif provider == "openai":
            return self._auth_api_key("openai", "OPENAI_API_KEY", "https://platform.openai.com/api-keys")
        elif provider == "anthropic":
            return self._auth_api_key("anthropic", "ANTHROPIC_API_KEY", "https://console.anthropic.com/")
        elif provider == "local-proxy":
            return self._auth_local_proxy()
        
        return False
    
    def _auth_github_copilot(self) -> bool:
        """Authenticate with GitHub Copilot via device flow."""
        print("\nRunning GitHub device-flow authentication...")
        print("(You'll need to authorize this in your web browser)\n")
        
        from .main import GitHubCopilotProvider
        
        try:
            provider = GitHubCopilotProvider()
            self.auth_token = provider.github_token
            
            if self.auth_token:
                safe_print("\n✓ GitHub Copilot authentication successful!")
                
                # Save profile
                profile_name = "github-copilot:default"
                self.auth.create_profile(
                    profile_name,
                    "github-copilot",
                    "device-token",
                    self.auth_token,
                    {"expiresAt": None}  # Device tokens don't typically expire
                )
                print(f"  Profile saved: {profile_name}")
                return True
            else:
                safe_print("\n✗ GitHub authentication failed or was cancelled.")
                return False
        except Exception as e:
            safe_print(f"\n✗ Authentication error: {e}")
            return False
    
    def _auth_api_key(self, provider: str, env_var: str, get_key_url: str) -> bool:
        """Authenticate with an API key provider."""
        import os
        
        # Check if already in environment
        existing_key = os.environ.get(env_var)
        if existing_key:
            choice = self._prompt_choice(
                f"Found {env_var} in environment. Use it?",
                [("Yes", "yes"), ("Enter new key", "new"), ("Cancel", "cancel")]
            )
            
            if choice == "yes":
                self.auth_token = existing_key
            elif choice == "new":
                self.auth_token = self._prompt_for_api_key(provider, get_key_url)
            else:
                return False
        else:
            self.auth_token = self._prompt_for_api_key(provider, get_key_url)
        
        if not self.auth_token:
            return False
        
        # Save profile
        profile_name = f"{provider}:default"
        self.auth.create_profile(
            profile_name,
            provider,
            "api-key",
            self.auth_token
        )
        safe_print(f"✓ Profile saved: {profile_name}")
        return True
    
    def _auth_local_proxy(self) -> bool:
        """Authenticate with a local/proxy provider."""
        print("\nLocal/Proxy Provider Configuration:")
        
        endpoint = self._prompt_input(
            "Enter the endpoint URL (e.g., http://localhost:8000/v1)",
            validate=lambda x: x.startswith(("http://", "https://"))
        )
        
        if not endpoint:
            return False
        
        # Test endpoint
        api_key = self._prompt_input(
            "API key (optional, press Enter to skip)",
            default=""
        )
        
        print("\nTesting endpoint...")
        success, message = ProviderRegistry.test_endpoint(endpoint, api_key or None)
        print(f"  {message}")
        
        if not success:
            if self._prompt_yes_no("Continue anyway?"):
                self.auth_token = api_key or ""
            else:
                return False
        else:
            self.auth_token = api_key or ""
        
        # Save configuration (not in auth since it's just URL + optional key)
        # We'll store this in the provider config instead
        self.config.set_provider("local-proxy", {
            "type": "local-proxy",
            "baseUrl": endpoint,
            "apiKey": self.auth_token if self.auth_token else None
        })
        
        return True
    
    def _discover_and_select_model(self) -> bool:
        """Step 4: Discover and select a model."""
        safe_print("\n🤖 Step 3: Model Selection")
        print("-" * 70)
        
        print("Discovering available models...")
        
        # Discover models
        models = ProviderRegistry.discover_models(
            self.selected_provider,
            auth_token=self.auth_token
        )
        
        if not models:
            safe_print("✗ Could not discover models.")
            return False
        
        safe_print(f"✓ Found {len(models)} available models:\n")
        
        # Build choice list
        choices = [
            (f"{m['name']:30} ({m['id']})", m['id'])
            for m in models
        ]
        
        selected_id = self._prompt_choice(
            "Which model would you like to use as default?",
            choices
        )
        
        if not selected_id:
            return False
        
        self.selected_model = f"{self.selected_provider}/{selected_id}"
        safe_print(f"\n✓ Selected: {self.selected_model}")
        return True
    
    def _test_connectivity(self) -> bool:
        """Step 5: Test connectivity to the selected provider."""
        safe_print("\n🧪 Step 4: Testing Connectivity")
        print("-" * 70)
        
        # Simple connectivity test
        if self.selected_provider == "local-proxy":
            endpoint = self.config.get_provider("local-proxy").get("baseUrl")
            api_key = self.config.get_provider("local-proxy").get("apiKey")
            success, message = ProviderRegistry.test_endpoint(endpoint, api_key)
            print(f"  {message}")
            return success
        
        # For cloud providers, just verify token exists
        if self.auth_token:
            safe_print(f"  ✓ Authentication token is configured")
            return True
        
        return False
    
    def _save_configuration(self) -> bool:
        """Step 6: Save configuration."""
        safe_print("\n💾 Step 5: Saving Configuration")
        print("-" * 70)
        
        # Set model config
        self.config.set_model_config(self.selected_model, fallbacks=[])
        
        # Set provider config (already done for local-proxy)
        if self.selected_provider != "local-proxy":
            self.config.set_provider(self.selected_provider, {
                "type": self.selected_provider,
            })
        
        # Save config file
        if self.config.save_config():
            safe_print(f"✓ Config saved to: {self.config.config_file}")
            return True
        else:
            safe_print("✗ Failed to save config")
            return False
    
    def _show_summary(self) -> None:
        """Step 7: Show summary."""
        print("\n" + "="*70)
        safe_print("  ✓ ONBOARDING COMPLETE!")
        print("="*70)
        print(f"\nDefault Model: {self.selected_model}")
        print(f"Config Location: {self.config.config_file}")
        print(f"Auth Location: {self.auth.auth_index_file}")
        print("\nYou can now run:")
        print(f"  contextify \"your request\"")
        print("\nTo change settings later:")
        print(f"  contextify onboard")
        print()
    
    # Utility prompt methods
    
    @staticmethod
    def _prompt_choice(
        question: str,
        choices: List[tuple],
        default: Optional[int] = None
    ) -> Optional[str]:
        """Prompt for a choice from a list."""
        print(f"\n{question}")
        
        for i, (text, value) in enumerate(choices):
            marker = ">" if i == (default or 0) else " "
            print(f"  {marker} [{i+1}] {text}")
        
        while True:
            response = input("\nEnter number (or 'c' to cancel): ").strip().lower()
            
            if response == 'c':
                return None
            
            if response == '':
                return choices[default or 0][1] if default is not None else None
            
            try:
                idx = int(response) - 1
                if 0 <= idx < len(choices):
                    return choices[idx][1]
                print("Invalid choice, please try again.")
            except ValueError:
                print("Please enter a number.")
    
    @staticmethod
    def _prompt_input(
        question: str,
        default: Optional[str] = None,
        validate: Optional[callable] = None
    ) -> Optional[str]:
        """Prompt for text input."""
        default_text = f" [{default}]" if default else ""
        print(f"\n{question}{default_text}")
        
        while True:
            response = input("> ").strip()
            
            if not response:
                if default is not None:
                    return default
                print("Please enter a value.")
                continue
            
            if validate and not validate(response):
                print("Invalid input, please try again.")
                continue
            
            return response
    
    @staticmethod
    def _prompt_yes_no(question: str, default: bool = True) -> bool:
        """Prompt for yes/no."""
        default_str = "Y/n" if default else "y/N"
        print(f"\n{question} [{default_str}]")
        
        response = input("> ").strip().lower()
        
        if not response:
            return default
        
        return response in ('y', 'yes')
    
    @staticmethod
    def _prompt_for_api_key(provider: str, get_key_url: str) -> Optional[str]:
        """Prompt for API key with help text."""
        print(f"\nYou need an API key for {provider}.")
        print(f"Get one at: {get_key_url}\n")
        
        key = input("Paste your API key (or press Ctrl+C to cancel): ").strip()
        
        if not key:
            print("No key provided.")
            return None
        
        if len(key) < 10:
            if not OnboardingWizard._prompt_yes_no("Key seems short. Continue anyway?"):
                return None
        
        return key


def run_onboarding(non_interactive: bool = False) -> bool:
    """
    Run the onboarding wizard.
    Returns True if successful, False otherwise.
    """
    config = get_config_manager()
    auth = get_auth_manager(config.config_dir)
    
    wizard = OnboardingWizard(config, auth)
    
    if non_interactive:
        print("[ERROR] Non-interactive mode not yet implemented")
        return False
    
    return wizard.run_interactive()
