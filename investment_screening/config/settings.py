"""
Configuration settings for the Investment Screening System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
LIGHTON_API_KEY = os.getenv("LIGHTON_API_KEY", "your_api_key_here")
LIGHTON_BASE_URL = os.getenv("LIGHTON_BASE_URL", "https://api.lighton.ai")


# Workflow Configuration
MAX_WAIT_TIME = 300  # 5 minutes for polling
POLL_INTERVAL = 5  # 5 seconds between polls
MAX_DOCUMENTS_PER_BATCH = 5

# Investment Criteria Thresholds
MIN_INVESTMENT_SIZE = 5.0  # Million USD
PREFERRED_INVESTMENT_SIZE = 7.9  # Million USD
MIN_IRR_THRESHOLD = 15.0  # Percentage
MIN_DIVIDEND_YIELD = 4.0  # Percentage
MIN_TIMELINE_WEEKS = 8  # Standard deal timeline
MIN_KGI_TIMELINE_WEEKS = 3  # KGI co-investment timeline

# Target Sectors
TARGET_SECTORS = [
    "healthcare",
    "education", 
    "data economy",
    "energy transition",
    "industrials"
]

# Excluded Sectors
EXCLUDED_SECTORS = [
    "consumer",
    "traditional infrastructure"
]

# Fund Types (excluded)
FUND_TYPES = [
    "venture fund",
    "pe fund", 
    "hedge fund",
    "fund investment",
    "pooled investment"
]

# Evaluation Status
class EvaluationStatus:
    MET = "MET"
    NOT_MET = "NOT MET"

# Colors for status indication
STATUS_COLORS = {
    EvaluationStatus.MET: "🟢",
    EvaluationStatus.NOT_MET: "🔴"
}