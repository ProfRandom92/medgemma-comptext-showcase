#!/bin/bash
# Development Setup Script for MedGemma x CompText
# This script installs development dependencies including terminalizer for recording demos

set -e  # Exit on error

echo "🏥 MedGemma x CompText - Development Setup"
echo "=========================================="
echo ""

# Check for Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.12+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Check for Node.js and npm
echo "Checking Node.js and npm installation..."
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "⚠️  Node.js or npm is not installed."
    echo "Terminalizer requires Node.js and npm for recording terminal demos."
    echo ""
    echo "To install Node.js:"
    echo "  - Ubuntu/Debian: sudo apt-get install nodejs npm"
    echo "  - macOS: brew install node"
    echo "  - Windows: Download from https://nodejs.org/"
    echo ""
    echo "Skipping terminalizer installation..."
else
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo "✅ Found Node.js $NODE_VERSION"
    echo "✅ Found npm $NPM_VERSION"
    echo ""
    
    # Install terminalizer
    echo "Installing terminalizer for terminal recording..."
    echo "(Note: terminalizer may have compatibility issues with Node.js 18+)"
    echo ""
    if npm install -g terminalizer 2>&1; then
        echo "✅ Terminalizer installed successfully"
        echo ""
        echo "You can now record terminal demos with:"
        echo "  terminalizer record demo_name"
        echo "  terminalizer render demo_name"
    else
        echo ""
        echo "⚠️  Terminalizer installation failed."
        echo "This is often due to Node.js version compatibility (requires Node 16)."
        echo ""
        echo "Alternative: Install asciinema (Python-based):"
        echo "  pip install asciinema"
        echo "  asciinema rec demo.cast"
        echo ""
        echo "You can continue without terminalizer. Python dependencies are installed."
    fi
fi

echo ""
echo "=========================================="
echo "✅ Development setup complete!"
echo ""
echo "Quick start commands:"
echo "  python demo_cli.py              # Run CLI demo"
echo "  streamlit run dashboard.py      # Run dashboard"
echo "  python -m pytest tests/unit/    # Run tests"
echo ""
echo "For recording demos:"
echo "  terminalizer record my_demo     # Start recording"
echo "  terminalizer render my_demo     # Create GIF"
echo "=========================================="
