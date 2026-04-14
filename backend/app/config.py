import os
from dotenv import load_dotenv

load_dotenv()

# App Settings
PROJECT_NAME = "LegalContractAI"
VERSION = "1.0.0"

# AI Settings
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_MODEL_SMART = os.getenv("NVIDIA_MODEL_SMART", "meta/llama-3.3-70b-instruct")
NVIDIA_MODEL_FAST = os.getenv("NVIDIA_MODEL_FAST", "mistralai/mistral-small-24b-instruct-2503")

# Pipeline Settings
TIMEOUT_PIPELINE = int(os.getenv("TIMEOUT_PIPELINE", "420"))
TIMEOUT_STANDARD = int(os.getenv("TIMEOUT_STANDARD", "120"))

# LLM Retry Settings
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "5"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120.0"))

# Pinecone Settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")

# Supabase Settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHAT_ENCRYPTION_KEY_V1 = os.getenv("CHAT_ENCRYPTION_KEY_V1")

# CORS Settings
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8080,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:8080,http://127.0.0.1:3000"
).split(",")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS]

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


# Pinecone Indexes
# Pinecone Indexes
INDEX_STATUTES = "indian-statutes-v2"
INDEX_REGULATIONS = "indian-regulations-v2"
INDEX_CLAUSES = "contract-clauses-v2"
# INDEX_CASES = "case-law-summaries-v2" # Removed as per user request
INDEX_SYNTHETIC = "synthetic-jurisdictions" # Optional/Legacy
INDEX_COMMENTARY = "legal-commentary" # Optional/Legacy
