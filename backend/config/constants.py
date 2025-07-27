# File extensions
FILE_EXTENSIONS = {
    'HTML': '.html',
    'JSON': '.json',
    'USERS_FILE': 'users.json'
}

# Email template paths
EMAIL_TEMPLATES = {
    'WELCOME': 'templates/welcome_email.html',
    'REPORT': 'templates/report_email.html'
}

# AI model configurations
AI_MODELS = {
    'DEFAULT': 'gpt-4o-mini',
    'TEMPERATURE': 0.7,
    'TIMEOUT': 120
}

# Time delays (in seconds)
DELAYS = {
    'EMAIL_DEPLOYMENT': 300,  # Testing delay: 1 second between reports
}

# GitHub configuration for reports repository
GITHUB_CONFIG = {
    'REPO_OWNER': 'AkashCiel',
    'REPO_NAME': 'bhai_jaan_academy_reports',
    'BRANCH': 'main'
}

# GitHub configuration for main repository (for users.json sync)
MAIN_REPO_CONFIG = {
    'REPO_OWNER': 'AkashCiel',
    'REPO_NAME': 'bhai_jaan_academy',
    'BRANCH': 'main'
} 