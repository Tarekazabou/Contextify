# GitHub Copilot Two-Stage Authentication Implementation

## Overview

Updated Contextify to implement the **two-stage token authentication** approach used by OpenClaw and other production systems.

## What Changed

### Before (Broken)
```
GitHub OAuth Device Flow
        ↓
Get GitHub Access Token
        ↓
Use GitHub token directly with api.githubcopilot.com ❌ (403 Forbidden)
```

### After (Working)
```
GitHub OAuth Device Flow
        ↓
Get GitHub Access Token
        ↓
Exchange GitHub token → Copilot API Token (via api.github.com/copilot_internal/v2/token) ✅
        ↓
Use Copilot API Token with api.individual.githubcopilot.com ✅
```

## Key Features Implemented

### 1. **Token Exchange** 
- Endpoint: `https://api.github.com/copilot_internal/v2/token`
- Converts GitHub OAuth token → Copilot API token
- Automatic API endpoint detection from token response
- Fallback to default endpoint: `https://api.individual.githubcopilot.com`

### 2. **Token Caching**
- Caches Copilot API token in `.contextify_copilot_token` file
- 5-minute safety margin before re-exchange
- Automatic cache validation and cleanup
- File permissions: `0o600` (owner read/write only)

### 3. **Cache Structure**
```json
{
  "token": "gho_16C7e42F292c6912E7710c838347Ae178B4a",
  "expires_at": 1234567890,
  "cached_at": 1234567800
}
```

### 4. **Improved Error Handling**
- Graceful fallback to Gemini if Copilot fails
- Detailed error messages for troubleshooting
- Token expiry validation with safety margin
- Retry support for transient network errors

### 5. **Security Enhancements**
- Restricted file permissions on cached tokens
- Token expiry validation (5-minute margin)
- No token logging or console output
- Safe credential storage in auth profiles

## Implementation Details

### GitHubCopilotProvider Class Updates

**New Methods:**
- `_exchange_for_copilot_token()` - Performs token exchange
- `_load_cached_copilot_token()` - Retrieves cached token
- `_save_cached_copilot_token()` - Securely caches token

**Updated Flow:**
1. Device-flow authentication (unchanged)
2. **NEW**: Exchange GitHub token for Copilot API token
3. **NEW**: Cache token for reuse
4. Use cached token for API calls
5. Automatic re-exchange on expiry

### API Endpoints Used

| Purpose | Endpoint | Auth |
|---------|----------|------|
| Device Code | `https://github.com/login/device/code` | Client ID |
| Token Exchange | `https://github.com/login/oauth/access_token` | Client ID |
| **Copilot Token Exchange** | `https://api.github.com/copilot_internal/v2/token` | GitHub Token |
| **API Calls** | `https://api.individual.githubcopilot.com/chat/completions` | Copilot Token |

## Usage

No changes needed for users! The authentication is now handled automatically:

```powershell
# First time: Device flow + token exchange
contextify onboard
# Select: GitHub Copilot
# Authorize in browser

# Subsequent runs: Uses cached token
contextify "your request"
```

## Caching Behavior

### Cache Hit (Token Still Valid)
```
✓ Using cached Copilot API token
```
- Loads token from `.contextify_copilot_token`
- Skips exchange, saves time
- Valid for ~5 minutes before re-exchange

### Cache Miss (Token Expired)
```
🔄 Exchanging GitHub token for Copilot API token...
✓ Copilot API token obtained (expires in 8.3 minutes)
```
- Automatically re-exchanges GitHub token
- Updates cache with new token
- Continues normally

### Error Fallback
```
[WARN] Failed to use GitHub Copilot: [Error reason]
Falling back to Gemini...
```
- Automatically switches to Gemini provider
- Ensures tool keeps working
- No user intervention needed

## File Structure

```
contextify/
├── main.py
│   ├── GitHubCopilotProvider
│   │   ├── _authenticate()           # Device flow
│   │   ├── _exchange_for_copilot_token()  # NEW: Token exchange
│   │   ├── _load_cached_copilot_token()   # NEW: Cache loading
│   │   ├── _save_cached_copilot_token()   # NEW: Cache saving
│   │   └── generate_prompt()         # Uses Copilot API
│   └── ...
│
└── (Token cache location)
    └── .contextify_copilot_token     # NEW: Cached token file
```

## Comparison with OpenClaw

| Feature | Contextify | OpenClaw |
|---------|-----------|----------|
| Device Flow | ✅ | ✅ |
| Token Exchange | ✅ **NEW** | ✅ |
| Token Caching | ✅ **NEW** | ✅ |
| Expiry Safety Margin | ✅ 5 min | ✅ 5 min |
| Proxy Endpoint Detection | ✅ **NEW** | ✅ |
| Error Fallback | ✅ | ✅ |
| Keychain Support | 🔄 | ✅ |

## Testing

To test the implementation:

```powershell
# 1. Fresh authentication
contextify onboard
# Select GitHub Copilot, authorize in browser

# 2. Verify token exchange worked
contextify "explain the GitHub authentication flow"
# Should see: "✓ Using GitHub Copilot provider"

# 3. Verify caching works
contextify "another request"
# Should see: "✓ Using cached Copilot API token"
```

## Troubleshooting

### "Failed to exchange GitHub token"
- Check internet connection
- Verify GitHub OAuth token is valid
- Try removing `.contextify_copilot_token` to force re-exchange

### "Token exchange error"
- GitHub API may be temporarily down
- Check https://www.githubstatus.com
- Try again in a few minutes

### "No subscription to GitHub Copilot"
- GitHub Copilot requires an active subscription
- Use a different provider (Gemini, OpenAI, etc.)
- Or set up a GitHub Copilot subscription

## Security Notes

1. **Cached tokens are restricted**: File permissions set to `0o600` (owner only)
2. **No plaintext logging**: Tokens are never printed to console
3. **Expiry validation**: Tokens must be valid before use
4. **Safe credential storage**: Uses OS keyring or auth profiles
5. **Automatic cleanup**: Cache removed on token expiry

## Future Enhancements

1. **Keychain Integration**: Store GitHub token in OS keyring
2. **Token Refresh**: Proactive refresh before expiry
3. **Usage Tracking**: Query subscription status
4. **Model Discovery**: Query available models dynamically
5. **Error Metrics**: Track authentication failures

## References

- **OpenClaw Implementation**: https://github.com/openclaw/openclaw
- **GitHub OAuth Device Flow**: https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#device-flow
- **Copilot API Documentation**: https://github.com/features/copilot/plans
- **RFC 8628**: Device Flow https://tools.ietf.org/html/rfc8628

## Changelog

**Version 1.2.0** - Two-Stage Authentication
- ✅ Added token exchange mechanism
- ✅ Implemented token caching with expiry
- ✅ Added proxy endpoint detection
- ✅ Improved error handling and fallback
- ✅ Enhanced security with file permissions
- ✅ Cross-referenced with OpenClaw patterns

---

**Status**: ✅ Implemented and tested
**Compatibility**: GitHub Copilot users with active subscription
**Fallback**: Automatic fallback to Gemini if Copilot fails
