#!/bin/bash

# GitHub Sync Setup Script for Bhai Jaan Academy
# This script helps you set up the GitHub sync functionality

echo "🔧 GitHub Sync Setup for Bhai Jaan Academy"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env first:"
    echo "cp .env.example .env"
    exit 1
fi

echo "📋 Current Configuration:"
echo "------------------------"

# Check if MAIN_GITHUB_TOKEN is set
if grep -q "MAIN_GITHUB_TOKEN" .env; then
    echo "✅ MAIN_GITHUB_TOKEN is configured"
else
    echo "❌ MAIN_GITHUB_TOKEN is not configured"
fi

# Check if REPORTS_GITHUB_TOKEN is set
if grep -q "REPORTS_GITHUB_TOKEN" .env; then
    echo "✅ REPORTS_GITHUB_TOKEN is configured"
else
    echo "❌ REPORTS_GITHUB_TOKEN is not configured"
fi

echo ""
echo "🔑 Setup Instructions:"
echo "====================="
echo ""
echo "1. Create a GitHub Personal Access Token:"
echo "   - Go to GitHub Settings → Developer settings → Personal access tokens"
echo "   - Click 'Generate new token (classic)'"
echo "   - Name: 'Bhai Jaan Academy Auto-Sync'"
echo "   - Select scopes: repo, workflow"
echo "   - Copy the token"
echo ""
echo "2. Add the token to your .env file:"
echo "   MAIN_GITHUB_TOKEN=your_token_here"
echo ""
echo "3. For Render deployment, add the environment variable:"
echo "   - Go to your Render dashboard"
echo "   - Select your backend service"
echo "   - Go to Environment tab"
echo "   - Add MAIN_GITHUB_TOKEN with your token value"
echo "   - Redeploy the service"
echo ""
echo "4. Test the setup:"
echo "   python test_github_sync.py"
echo ""
echo "📖 For detailed instructions, see: GITHUB_SYNC_SETUP.md"
echo ""
echo "🎯 What this does:"
echo "- Automatically syncs users.json to reports repository when users register"
echo "- Commits changes to the main branch with timestamps"
echo "- Works with both local development and Render deployment"
echo "- Gracefully handles errors without breaking the main application"
echo ""
echo "✅ Ready to set up GitHub sync!" 