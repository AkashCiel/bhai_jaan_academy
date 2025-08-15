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
│   ├── users.json     # User data (auto-synced to reports repository)
│   └── .env          # Environment variables
└── README.md         # This file
```

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Python, FastAPI
- **Database**: Supabase (PostgreSQL)
- **Email**: SendGrid
- **Hosting**: Netlify (frontend), Render (backend)
- **Data Sync**: GitHub API (auto-syncs users.json to reports repository)

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

# GitHub Configuration for Reports Repository
REPORTS_GITHUB_TOKEN=your_github_token_for_reports_repo

# GitHub Configuration for Main Repository (users.json sync)
MAIN_GITHUB_TOKEN=your_github_token_for_main_repo
```

### Frontend (Netlify Environment Variables)
```bash
BACKEND_URL=https://your-api.onrender.com
```

## 🔄 GitHub Sync Feature

The system automatically syncs `users.json` changes from Render back to the reports repository. This ensures that:

- ✅ New user registrations are committed to the main branch
- ✅ User updates are reflected in the repository
- ✅ Data consistency between deployment and source code

### Setup GitHub Sync

See [backend/GITHUB_SYNC_SETUP.md](backend/GITHUB_SYNC_SETUP.md) for detailed setup instructions.

**Quick Setup:**
1. Create a GitHub Personal Access Token with `repo` scope
2. Add `MAIN_GITHUB_TOKEN=your_token` to your environment variables
3. Test with: `cd backend && python test_github_sync.py`

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

- [x] Set up Supabase database
- [x] Configure SendGrid email service
- [x] Implement AI content generation
- [x] Add daily scheduling system
- [x] Create HTML report generation
- [x] Add user progress tracking
- [x] Auto-sync users.json to reports repository

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
