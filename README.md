# Bhai Jaan Academy

An automated learning system that generates personalized learning plans and delivers daily educational content via email.

## 🚀 Project Structure

```
bhai_jaan_academy/
├── frontend/           # Static website (deploys to Netlify)
│   ├── index.html     # Landing page
│   ├── styles.css     # Styling
│   └── script.js      # Frontend logic
├── backend/           # FastAPI server (deploys to Render)
│   ├── main.py        # API endpoints
│   ├── requirements.txt # Python dependencies
│   └── .env          # Environment variables
└── README.md         # This file
```

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python, FastAPI
- **Database**: Supabase (PostgreSQL)
- **Email**: SendGrid
- **Hosting**: Netlify (frontend), Render (backend)

## 🚀 Quick Start

### Prerequisites
- uv (Python package manager)
- Git

**Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd bhai_jaan_academy
   ```

2. **Set up backend**
   ```bash
   cd backend
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file in backend/
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. **Run backend**
   ```bash
   cd backend
   uv run uvicorn main:app --reload
   ```

5. **Open frontend**
   ```bash
   # Open frontend/index.html in your browser
   # Or serve with a local server
   python -m http.server 8000
   ```

## 🌐 Deployment

### Frontend (Netlify)
- Connect your GitHub repository to Netlify
- Set build directory to `frontend/`
- Deploy automatically on push

### Backend (Render)
- Connect your GitHub repository to Render
- Set build command: `cd backend && uv sync`
- Set start command: `cd backend && uv run uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set root directory to `.` (project root)

## 📧 Environment Variables

### Backend (.env)
```bash
# Email Service
MAILGUN_API_KEY=your_mailgun_api_key
MAILGUN_DOMAIN=your_mailgun_domain

# AI Service
OPENAI_API_KEY=your_openai_api_key

# Data Storage (Supabase)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
SUPABASE_BUCKET=reports
SUPABASE_PROJECT_REF=your_project_reference_id

# HTML Hosting (Netlify)
NETLIFY_ACCESS_TOKEN=your_netlify_access_token
NETLIFY_SITE_ID=your_netlify_site_id

# Frontend URL (for CORS)
FRONTEND_URL=https://your-app.netlify.app
```

### Frontend (Netlify Environment Variables)
```bash
BACKEND_URL=https://your-api.onrender.com
```

## 🔧 Development

### Backend API Endpoints
- `GET /` - Health check
- `POST /submit` - Submit user email and topic

### Frontend Features
- Email and topic input form
- Form validation
- API communication
- Success/error messaging

## 📝 TODO

- [ ] Set up Supabase database
- [ ] Configure SendGrid email service
- [ ] Implement AI content generation
- [ ] Add daily scheduling system
- [ ] Create HTML report generation
- [ ] Add user progress tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
