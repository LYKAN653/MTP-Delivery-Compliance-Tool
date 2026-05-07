#!/bin/bash
# Installation & Setup Helper Script for Mac

echo "========================================"
echo "Sales Order Analyzer - Setup Helper"
echo "========================================"
echo ""

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "⚠️  Git is not installed"
    echo "Install with: brew install git"
    echo "Or download from: https://git-scm.com/download/mac"
    exit 1
fi

echo "✅ Git found: $(git --version)"
echo ""

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📁 Project directory: $SCRIPT_DIR"
echo ""

# Check if git is already initialized
if [ -d "$SCRIPT_DIR/.git" ]; then
    echo "✅ Git repository already initialized"
    echo ""
    echo "Current Git status:"
    git -C "$SCRIPT_DIR" status
else
    echo "❓ Git repository not initialized"
    echo ""
    echo "To initialize and push to GitHub:"
    echo ""
    echo "1. Create a repository on GitHub.com"
    echo ""
    echo "2. Run these commands:"
    echo "   cd \"$SCRIPT_DIR\""
    echo "   git init"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/SalesOrderAnalyzer.git"
    echo "   git config --global user.name \"Your Name\""
    echo "   git config --global user.email \"your@email.com\""
    echo "   git add ."
    echo "   git commit -m \"Initial commit: Sales Order Analyzer with GUI v2.1\""
    echo "   git push -u origin main"
    echo ""
fi

echo ""
echo "📖 Next steps:"
echo "1. Read: INDEX.md (quick overview)"
echo "2. Read: COMPLETE_SETUP_GUIDE.md (detailed walkthrough)"
echo "3. Read: QUICKSTART.md (quick reference)"
echo ""
echo "✨ All documentation files start with capital letters and end in .md"
echo ""
echo "========================================"
