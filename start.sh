#!/usr/bin/env bash
# Startup script for Votra.io API

set -e

echo "🚀 Starting Votra.io API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your configuration."
    echo ""
    echo "🔑 Generating a secure SECRET_KEY..."
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update SECRET_KEY in .env file (macOS compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    echo "✅ SECRET_KEY has been generated and saved to .env"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Only install development dependencies in non-production environments
if [ "${ENV:-}" != "production" ] && [ "${APP_ENV:-}" != "production" ] && [ "${ENVIRONMENT:-}" != "production" ]; then
    echo "📦 Installing development dependencies (non-production environment detected)..."
    pip install -r requirements-dev.txt
else
    echo "⏭️  Skipping development dependencies installation in production environment."
fi
# Run database migrations (when implemented)
# echo "🗄️  Running database migrations..."
# alembic upgrade head

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server on http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo ""

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
