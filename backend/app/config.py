import os
from dotenv import load_dotenv

load_dotenv()

# App Settings
PROJECT_NAME = "LegalContractAI"
VERSION = "1.0.0"

# AI Settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

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
INDEX_CASES = "case-law-summaries-v2"
INDEX_SYNTHETIC = "synthetic-jurisdictions" # Optional/Legacy
INDEX_COMMENTARY = "legal-commentary" # Optional/Legacy
