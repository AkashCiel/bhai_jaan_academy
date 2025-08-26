import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from .constants import AI_MODELS, GITHUB_CONFIG, MAIN_REPO_CONFIG, FILE_EXTENSIONS, EMAIL_TEMPLATES, DELAYS, PAYMENT_CONFIG

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., validation_alias='OPENAI_API_KEY')
    OPENAI_MODEL: str = Field(default=AI_MODELS['DEFAULT'], validation_alias='OPENAI_MODEL')
    OPENAI_TEMPERATURE: float = Field(default=AI_MODELS['TEMPERATURE'], validation_alias='OPENAI_TEMPERATURE')
    OPENAI_MAX_TOKENS_REPORT: int = Field(default=10000, validation_alias='OPENAI_MAX_TOKENS_REPORT')
    OPENAI_MAX_TOKENS_PLAN: int = Field(default=3000, validation_alias='OPENAI_MAX_TOKENS_PLAN')
    OPENAI_TIMEOUT: int = Field(default=AI_MODELS['TIMEOUT'], validation_alias='OPENAI_TIMEOUT')
    
    # Email Configuration
    MAILGUN_API_KEY: Optional[str] = Field(default=None, validation_alias='MAILGUN_API_KEY')
    MAILGUN_DOMAIN: Optional[str] = Field(default=None, validation_alias='MAILGUN_DOMAIN')
    
    # GitHub Configuration for Reports Repository
    REPORTS_GITHUB_TOKEN: Optional[str] = Field(default=None, validation_alias='REPORTS_GITHUB_TOKEN')
    GITHUB_REPO_OWNER: str = Field(default=GITHUB_CONFIG['REPO_OWNER'], validation_alias='GITHUB_REPO_OWNER')
    GITHUB_REPO_NAME: str = Field(default=GITHUB_CONFIG['REPO_NAME'], validation_alias='GITHUB_REPO_NAME')
    GITHUB_BRANCH: str = Field(default=GITHUB_CONFIG['BRANCH'], validation_alias='GITHUB_BRANCH')
    
    # GitHub Configuration for Main Repository (users.json sync)
    MAIN_GITHUB_TOKEN: Optional[str] = Field(default=None, validation_alias='MAIN_GITHUB_TOKEN')
    MAIN_REPO_OWNER: str = Field(default=MAIN_REPO_CONFIG['REPO_OWNER'], validation_alias='MAIN_REPO_OWNER')
    MAIN_REPO_NAME: str = Field(default=MAIN_REPO_CONFIG['REPO_NAME'], validation_alias='MAIN_REPO_NAME')
    MAIN_REPO_BRANCH: str = Field(default=MAIN_REPO_CONFIG['BRANCH'], validation_alias='MAIN_REPO_BRANCH')
    
    # File Configuration
    USERS_FILE: str = Field(default=FILE_EXTENSIONS['USERS_FILE'], validation_alias='USERS_FILE')
    REPORT_DELAY_SECONDS: int = Field(default=DELAYS['EMAIL_DEPLOYMENT'], validation_alias='REPORT_DELAY_SECONDS')
    
    # Email Templates
    WELCOME_EMAIL_TEMPLATE: str = Field(default=EMAIL_TEMPLATES['WELCOME'], validation_alias='WELCOME_EMAIL_TEMPLATE')
    REPORT_EMAIL_TEMPLATE: str = Field(default=EMAIL_TEMPLATES['REPORT'], validation_alias='REPORT_EMAIL_TEMPLATE')
    
    # Discord Configuration
    DISCORD_WEBHOOK_URL: Optional[str] = Field(default=None, validation_alias='DISCORD_WEBHOOK_URL')
    
    # PayPal Configuration
    PAYPAL_CLIENT_ID: Optional[str] = Field(default=None, validation_alias='PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET: Optional[str] = Field(default=None, validation_alias='PAYPAL_CLIENT_SECRET')
    
    # Payment Configuration
    PAYMENT_AMOUNT: str = Field(default=PAYMENT_CONFIG['AMOUNT'], validation_alias='PAYMENT_AMOUNT')
    PAYMENT_CURRENCY: str = Field(default=PAYMENT_CONFIG['CURRENCY'], validation_alias='PAYMENT_CURRENCY')
    PAYMENT_DESCRIPTION: str = Field(default=PAYMENT_CONFIG['DESCRIPTION'], validation_alias='PAYMENT_DESCRIPTION')
    PAYMENT_MODE: str = Field(default=PAYMENT_CONFIG['MODE'], validation_alias='PAYMENT_MODE')
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Global settings instance
settings = Settings(_env_file=".env") 