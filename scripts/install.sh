#!/bin/bash

echo "🚀 Installing Contextify - The Context Bridge for AI Coders"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --break-system-packages

# Make the script executable
chmod +x contextify.py

# Try to add to PATH
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Create symlink - note: scripts/ directory is in the parent
ln -sf "$(cd .. && pwd)/contextify.py" "$INSTALL_DIR/contextify"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Get your Gemini API key from: https://makersuite.google.com/app/apikey"
echo "2. Set the environment variable:"
echo "   export GEMINI_API_KEY='your-api-key-here'"
echo ""
echo "   Add this to your ~/.bashrc or ~/.zshrc to make it permanent:"
echo "   echo 'export GEMINI_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
echo ""
echo "3. Make sure $INSTALL_DIR is in your PATH"
echo "   Add this to your ~/.bashrc or ~/.zshrc if needed:"
echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
echo ""
echo "4. Restart your terminal or run: source ~/.bashrc"
echo ""
echo "🎉 Usage:"
echo "   contextify 'add a dark mode toggle'"
echo "   contextify 'create a user profile card' --focus frontend"
echo "   contextify 'fix the bug' --changed"
echo ""
echo "For help: contextify --help"
