#!/bin/bash

# Bhai Jaan Academy Development Script

echo "🚀 Starting Bhai Jaan Academy Development Environment"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📦 Setting up backend..."

# Install dependencies using uv
echo "Installing backend dependencies with uv..."
cd backend
uv sync
cd ..

echo "✅ Backend setup complete!"

echo ""
echo "🌐 Starting services..."
echo ""

# Start backend in background
echo "Starting backend server on http://localhost:8000"
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server on http://localhost:3000"
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Development environment is running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait 