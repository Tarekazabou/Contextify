# Contextify Animation System

## Overview

The Contextify animation system has been reimplemented using a **Ghosttime-inspired frame-based architecture**. This provides smooth, elegant, and performant terminal animations with minimal CPU overhead.

## Architecture

### Core Components

#### 1. **Animation Class**
```powershell
class Animation {
    [hashtable] $frames = @{}      # Pre-calculated frame storage
    [int] $frameCount = 0           # Total number of frames
    [string] $highlightColor = ""   # ANSI color code
}
```

The `Animation` class manages:
- **Pre-calculated frames**: Array of string arrays representing each animation frame
- **Frame caching**: Efficient frame retrieval with hashtable indexing
- **Color customization**: Support for ANSI 256-color codes

#### 2. **Frame Structure**
Frames are stored as 3-line ASCII art sequences:
```powershell
$frame = @(
    "         ",    # Line 1 (padding)
    "   >>    ",    # Line 2 (animation content)
    "         "     # Line 3 (padding)
)
```

#### 3. **Rendering Pipeline**
The rendering system features:
- **ANSI terminal control**: Cursor positioning (`e[H`), line clearing (`e[2K`)
- **Terminal-aware centering**: Calculates padding based on terminal width
- **Output buffering**: Minimal write operations for performance
- **Smooth timing**: 30ms frame delay (33.3 FPS)

### Performance Characteristics

| Metric | Value |
|--------|-------|
| Frame Rate | 33.3 FPS (30ms per frame) |
| Total Frames | 12 (flowing context animation) |
| Color Support | ANSI 256-color (16-color palette used) |
| CPU Overhead | Minimal (frame-based, not computed) |
| Memory Usage | ~2KB for frame cache |

## API Reference

### Show-ContextAnimation

Main animation function with progress tracking.

```powershell
Show-ContextAnimation -Message <string> [-Duration <int>] [-Color <string>]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Message | string | "Contextify" | Operation description |
| Duration | int | 3000 | Animation duration in milliseconds |
| Color | string | "`e[38;5;33m" | ANSI color code for animation |

#### Examples

```powershell
# Basic usage (3 seconds)
Show-ContextAnimation -Message "Building context bridge"

# Custom duration and color (red)
Show-ContextAnimation -Message "Processing files" -Duration 5000 -Color "`e[38;5;196m"

# Quick animation (500ms)
Show-ContextAnimation -Message "Finalizing" -Duration 500
```

#### Features

- ✅ Animated flowing context visualization
- ✅ Real-time progress percentage (0-100%)
- ✅ Automatic cursor hiding/restoration
- ✅ Terminal dimension awareness
- ✅ ANSI color support with fallback
- ✅ Graceful error handling for cursor operations

### Show-ProcessingAnimation

Fast lightweight spinner for quick operations.

```powershell
Show-ProcessingAnimation -Message <string> [-Duration <int>]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Message | string | (required) | Operation description |
| Duration | int | 1000 | Animation duration in milliseconds |

#### Examples

```powershell
# Fast spinner (default 1 second)
Show-ProcessingAnimation -Message "Auto-loading configuration"

# Longer operation
Show-ProcessingAnimation -Message "Installing dependencies" -Duration 5000
```

#### Features

- ✅ Fast spinner animation (*+*+)
- ✅ Color transition (blue → green on completion)
- ✅ Compact single-line output
- ✅ Progress-aware coloring

### Show-Spinner (Backward Compatibility)

Alias for `Show-ProcessingAnimation` for backward compatibility.

```powershell
Show-Spinner -Message <string> [-Duration <int>]
```

## Color Palette

### Available Colors

The system uses ANSI 256-color codes:

```powershell
$highlightColor = "`e[38;5;33m"   # Blue (animation color)
$reset         = "`e[0m"          # Reset
$cyan          = "`e[38;5;80m"    # Cyan (message text)
$blue          = "`e[38;5;33m"    # Blue (accent)
$gray          = "`e[38;5;242m"   # Gray (borders)
$green         = "`e[38;5;76m"    # Green (completion)
```

### ANSI Color Code Format

- `\e[38;5;<num>m` - 256-color foreground
- `\e[0m` - Reset all formatting

### Customization Example

```powershell
# Red animation
Show-ContextAnimation -Message "Critical operation" -Color "`e[38;5;196m"

# Magenta animation
Show-ContextAnimation -Message "Special operation" -Color "`e[38;5;127m"

# Yellow animation
Show-ContextAnimation -Message "Warning" -Color "`e[38;5;226m"
```

## Integration with setup.ps1

The animation module is automatically loaded by `setup.ps1`:

```powershell
# Dot-source animation functions
. "$PSScriptRoot\contextify-animation.ps1"

# Use in setup
Show-Spinner "Creating virtual environment" 1000
Show-ProcessingAnimation "Installing dependencies" 1500
```

## Frame Data

### Animation Frames (12 total)

The flowing context animation uses 12 frames representing a rightward-moving pattern:

```
Frame 0:  >         (position 1)
Frame 1:  >>        (position 2)
Frame 2:  >>>       (position 3)
...
Frame 11: >         (position 1, reset)
```

This creates a smooth looping animation of flowing context data.

### Adding Custom Frames

To customize animations, modify the `$animationFrames` array in the `Animation` class:

```powershell
hidden [string[][]] $animationFrames = @(
    @("Frame 0 Line 1", "Frame 0 Line 2", "Frame 0 Line 3"),
    @("Frame 1 Line 1", "Frame 1 Line 2", "Frame 1 Line 3"),
    # Add more frames...
)
```

## Terminal Compatibility

### Supported Terminals

- ✅ Windows Terminal (recommended)
- ✅ Windows PowerShell 5.1+
- ✅ PowerShell Core 7+
- ✅ ConEmu
- ✅ VS Code Integrated Terminal
- ✅ Third-party terminals with ANSI support

### Fallback Behavior

- Terminals without ANSI support: Plain text output (no colors)
- Cursor operations: Wrapped in try-catch for compatibility
- Terminal width detection: Defaults to 80 columns

### Terminal Variables

```powershell
$supportsAnsi = $Host.UI.SupportsVirtualTerminal -eq $true -or $env:WT_SESSION
```

## Performance Notes

### Frame-Based Approach Benefits

1. **Pre-calculation**: All frames computed once during initialization
2. **Minimal computation**: Runtime only selects frames by index
3. **Low memory**: 2KB footprint for 12 frames
4. **CPU efficient**: No drawing calculations per frame
5. **Smooth rendering**: Consistent 30ms frame intervals

### Optimization Techniques

- **Hashtable caching**: O(1) frame lookup
- **Output buffering**: Grouped write operations
- **Cursor control**: Absolute positioning with escape sequences
- **Padding optimization**: Pre-calculated padding strings

## Troubleshooting

### Animation Not Displaying

**Problem**: Animation frames not showing or appear corrupted

**Solutions**:
1. Verify terminal supports ANSI codes: `$Host.UI.SupportsVirtualTerminal`
2. Check terminal width: `$Host.UI.RawUI.WindowSize.Width`
3. Ensure PowerShell version ≥ 5.1: `$PSVersionTable.PSVersion`

### Colors Not Working

**Problem**: Colors appear as escape sequences

**Solutions**:
1. Enable ANSI support in Windows Terminal settings
2. Check if running in incompatible terminal
3. Use fallback: Terminal without color support still shows animation

### Cursor Visibility Issues

**Problem**: Cursor doesn't hide/show

**Solutions**:
1. Try-catch blocks handle compatibility
2. Verify `Host.UI.RawUI.CursorVisible` is writable
3. Check PowerShell execution policy

## Examples

### Complete Setup Workflow

```powershell
. "$PSScriptRoot\contextify-animation.ps1"

Write-Host "CONTEXTIFY SETUP" -ForegroundColor Cyan

Show-ContextAnimation -Message "Building context bridge" -Duration 2500
Start-Sleep -Milliseconds 500

Show-ProcessingAnimation -Message "Loading configuration" -Duration 1000
Show-ProcessingAnimation -Message "Filtering files" -Duration 800
Show-ProcessingAnimation -Message "Analyzing patterns" -Duration 1200

Write-Host "[OK] Setup complete" -ForegroundColor Green
```

### Custom Animation Duration

```powershell
# Quick feedback (500ms)
Show-ContextAnimation -Message "Quick operation" -Duration 500

# Standard operation (3s)
Show-ContextAnimation -Message "Standard operation" -Duration 3000

# Long operation (10s)
Show-ContextAnimation -Message "Long operation" -Duration 10000
```

## Architecture Comparison

### Old System (Multi-Stage Pipeline)
- Sequential stage visualization
- Static progress bars
- Separate spinner frames
- Higher CPU overhead

### New System (Frame-Based Ghosttime)
- Pre-calculated animation frames
- Smooth flowing visualization
- Integrated progress tracking
- Minimal CPU overhead
- Better visual consistency

## Future Enhancements

Potential improvements:
- [ ] Configurable animation speed
- [ ] Custom frame definitions via file
- [ ] Terminal resize detection
- [ ] Unicode art support
- [ ] Multi-color animation cycling

## References

- **Ghosttime**: Frame-based terminal animation library
- **ANSI Escape Codes**: Terminal control sequences
- **PowerShell VT100 Support**: Virtual terminal support in PS

---

**Last Updated**: 2024
**Version**: 1.0 (Frame-Based Ghosttime Architecture)
