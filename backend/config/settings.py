import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from .constants import AI_MODELS, GITHUB_CONFIG, FILE_EXTENSIONS, EMAIL_TEMPLATES, DELAYS

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., validation_alias='OPENAI_API_KEY')
    OPENAI_MODEL: str = Field(default=AI_MODELS['DEFAULT'], validation_alias='OPENAI_MODEL')
    OPENAI_TEMPERATURE: float = Field(default=AI_MODELS['TEMPERATURE'], validation_alias='OPENAI_TEMPERATURE')
    OPENAI_MAX_TOKENS_REPORT: int = Field(default=4000, validation_alias='OPENAI_MAX_TOKENS_REPORT')
    OPENAI_MAX_TOKENS_PLAN: int = Field(default=3000, validation_alias='OPENAI_MAX_TOKENS_PLAN')
    OPENAI_TIMEOUT: int = Field(default=AI_MODELS['TIMEOUT'], validation_alias='OPENAI_TIMEOUT')
    
    # Email Configuration
    MAILGUN_API_KEY: Optional[str] = Field(default=None, validation_alias='MAILGUN_API_KEY')
    MAILGUN_DOMAIN: Optional[str] = Field(default=None, validation_alias='MAILGUN_DOMAIN')
    
    # GitHub Configuration
    REPORTS_GITHUB_TOKEN: Optional[str] = Field(default=None, validation_alias='REPORTS_GITHUB_TOKEN')
    GITHUB_REPO_OWNER: str = Field(default=GITHUB_CONFIG['REPO_OWNER'], validation_alias='GITHUB_REPO_OWNER')
    GITHUB_REPO_NAME: str = Field(default=GITHUB_CONFIG['REPO_NAME'], validation_alias='GITHUB_REPO_NAME')
    GITHUB_BRANCH: str = Field(default=GITHUB_CONFIG['BRANCH'], validation_alias='GITHUB_BRANCH')
    
    # File Configuration
    USERS_FILE: str = Field(default=FILE_EXTENSIONS['USERS_FILE'], validation_alias='USERS_FILE')
    REPORT_DELAY_SECONDS: int = Field(default=DELAYS['EMAIL_DEPLOYMENT'], validation_alias='REPORT_DELAY_SECONDS')
    
    # Email Templates
    WELCOME_EMAIL_TEMPLATE: str = Field(default=EMAIL_TEMPLATES['WELCOME'], validation_alias='WELCOME_EMAIL_TEMPLATE')
    REPORT_EMAIL_TEMPLATE: str = Field(default=EMAIL_TEMPLATES['REPORT'], validation_alias='REPORT_EMAIL_TEMPLATE')
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Global settings instance
settings = Settings(_env_file=".env") 