# ============================================
# STORAGE CONFIGURATION
# ============================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "storage", "uploads")
DATABASE_PATH = os.path.join(BASE_DIR, "storage", "database.db")

MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


# ============================================
# LLM CONFIGURATION
# ============================================

# Choose LLM provider: "ollama", "openai", "custom"
LLM_PROVIDER = "ollama"

# -------- OpenAI --------
OPENAI_API_KEY = "your-openai-api-key-here"
OPENAI_MODEL = "gpt-4"
OPENAI_BASE_URL = "https://api.openai.com/v1"

# -------- Ollama --------
OLLAMA_BASE_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"

# -------- Custom --------
CUSTOM_BASE_URL = "http://localhost:8000/v1"
CUSTOM_MODEL = "custom-model"
CUSTOM_API_KEY = "your-custom-key"

# -------- Active LLM (auto-selected) --------
if LLM_PROVIDER == "openai":
    LLM_BASE_URL = OPENAI_BASE_URL
    LLM_MODEL = OPENAI_MODEL
    LLM_API_KEY = OPENAI_API_KEY

elif LLM_PROVIDER == "ollama":
    LLM_BASE_URL = OLLAMA_BASE_URL
    LLM_MODEL = OLLAMA_MODEL
    LLM_API_KEY = None  # Ollama doesn't need a key

else:  # custom
    LLM_BASE_URL = CUSTOM_BASE_URL
    LLM_MODEL = CUSTOM_MODEL
    LLM_API_KEY = CUSTOM_API_KEY


# ============================================
# FLASK CONFIGURATION
# ============================================

SECRET_KEY = "insighto-secret-key-change-in-production"
DEBUG = True


# ============================================
# ANALYSIS CONFIGURATION
# ============================================

# Number of rows to show in data preview
PREVIEW_ROWS = 10

# Maximum number of charts allowed
MAX_CHARTS = 6

# Chart rendering settings
CHART_WIDTH = 10
CHART_HEIGHT = 6
CHART_DPI = 100



