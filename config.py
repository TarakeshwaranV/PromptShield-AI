import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "promptshield.db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

# Security & Detector Thresholds
# Probabilities from Logistic Regression:
# < 0.40 -> LOW risk (Benign)
# 0.40 - 0.70 -> MEDIUM risk (Ambiguous / Suspicious / Needs Review)
# >= 0.70 -> HIGH risk (Malicious / Blocked)
RISK_THRESHOLD_LOW = 0.40
RISK_THRESHOLD_HIGH = 0.70

# Synthetic Canary & Secret Strings for Testing / Leak Detection
# (Educational research sandbox use only - never real secrets!)
SYNTHETIC_CANARY_TOKEN = "CANARY-SECRET-9982-XYZ"
SYNTHETIC_SYSTEM_KEY = "MOCK-GROQ-PROD-API-KEY-7741"
SYNTHETIC_PROMPT_INSTRUCTION = "CRITICAL_SYSTEM_FLAG: ALPHA_PROTECT_2026"

# Permitted Mock Tools and Allowed Arguments
ALLOWED_TOOLS = {
    "get_sales_summary": {
        "description": "Retrieve aggregate sales summary across all regions",
        "required_args": [],
        "optional_args": ["year"],
    },
    "get_sales_by_month": {
        "description": "Retrieve monthly sales breakdown for a specific year",
        "required_args": ["year"],
        "optional_args": ["quarter"],
    },
    "get_top_products": {
        "description": "Retrieve top-selling products by revenue",
        "required_args": [],
        "optional_args": ["limit"],
    },
    "get_sales_by_region": {
        "description": "Retrieve sales totals grouped by geographic region",
        "required_args": ["region"],
        "optional_args": ["year"],
    },
}

# UI Theme & Branding
APP_TITLE = "PromptShield AI"
APP_SUBTITLE = "Three-Layer Prompt Injection Detection and Prevention Framework"
DARK_NAVY_THEME = {
    "primary": "#4F46E5",
    "background": "#0F172A",
    "secondary_background": "#1E293B",
    "text": "#F8FAFC",
    "accent": "#06B6D4",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "success": "#10B981",
}
