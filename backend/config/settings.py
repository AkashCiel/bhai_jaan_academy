import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from .constants import AI_MODELS, GITHUB_CONFIG, FILE_EXTENSIONS, EMAIL_TEMPLATES, DELAYS

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., env='OPENAI_API_KEY')
    OPENAI_MODEL: str = Field(default=AI_MODELS['DEFAULT'], env='OPENAI_MODEL')
    OPENAI_TEMPERATURE: float = Field(default=AI_MODELS['TEMPERATURE'], env='OPENAI_TEMPERATURE')
    OPENAI_MAX_TOKENS_REPORT: int = Field(default=1800, env='OPENAI_MAX_TOKENS_REPORT')
    OPENAI_MAX_TOKENS_PLAN: int = Field(default=2000, env='OPENAI_MAX_TOKENS_PLAN')
    OPENAI_TIMEOUT: int = Field(default=AI_MODELS['TIMEOUT'], env='OPENAI_TIMEOUT')
    
    # Email Configuration
    MAILGUN_API_KEY: Optional[str] = Field(default=None, env='MAILGUN_API_KEY')
    MAILGUN_DOMAIN: Optional[str] = Field(default=None, env='MAILGUN_DOMAIN')
    
    # GitHub Configuration
    REPORTS_GITHUB_TOKEN: Optional[str] = Field(default=None, env='REPORTS_GITHUB_TOKEN')
    GITHUB_REPO_OWNER: str = Field(default=GITHUB_CONFIG['REPO_OWNER'], env='GITHUB_REPO_OWNER')
    GITHUB_REPO_NAME: str = Field(default=GITHUB_CONFIG['REPO_NAME'], env='GITHUB_REPO_NAME')
    GITHUB_BRANCH: str = Field(default=GITHUB_CONFIG['BRANCH'], env='GITHUB_BRANCH')
    
    # File Configuration
    USERS_FILE: str = Field(default=FILE_EXTENSIONS['USERS_FILE'], env='USERS_FILE')
    REPORT_DELAY_SECONDS: int = Field(default=DELAYS['EMAIL_DEPLOYMENT'], env='REPORT_DELAY_SECONDS')
    
    # Email Templates
    WELCOME_EMAIL_TEMPLATE: str = Field(default=EMAIL_TEMPLATES['WELCOME'], env='WELCOME_EMAIL_TEMPLATE')
    REPORT_EMAIL_TEMPLATE: str = Field(default=EMAIL_TEMPLATES['REPORT'], env='REPORT_EMAIL_TEMPLATE')
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Global settings instance
settings = Settings() 