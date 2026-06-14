#!/bin/bash
echo "🚀 Starting Twitter Agent AWS Deployment Setup..."

echo "📦 Updating apt-get..."
sudo apt-get update -y

echo "🐍 Installing Python 3, pip, and virtual environment modules..."
sudo apt-get install -y python3 python3-pip python3-venv

echo "🌐 Setting up a virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📚 Installing Python packages from requirements.txt..."
pip install -r requirements.txt

echo "🎭 Installing Playwright Chromium browser and Linux dependencies..."
playwright install chromium --with-deps

echo "✅ Setup Complete!"
echo "To start the bot in the background, run:"
echo "tmux"
echo "source venv/bin/activate"
echo "python auto.py"
echo "Then press Ctrl+b, then d to detach!"
