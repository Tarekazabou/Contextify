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

# Try to add to PATH
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Create wrapper script for module execution
cat > "$INSTALL_DIR/contextify" << 'EOF'
#!/bin/bash
python3 -m contextify.main "$@"
EOF
chmod +x "$INSTALL_DIR/contextify"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Run the interactive setup:"
echo "   contextify onboard"
echo ""
echo "2. Make sure $INSTALL_DIR is in your PATH"
echo "   Add this to your ~/.bashrc or ~/.zshrc if needed:"
echo "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
echo ""
echo "3. Restart your terminal or run: source ~/.bashrc"
echo ""
echo "🎉 Usage:"
echo "   contextify 'add a dark mode toggle'"
echo "   contextify 'create a user profile card' --focus frontend"
echo "   contextify 'fix the bug' --changed"
echo ""
echo "For help: contextify --help"
