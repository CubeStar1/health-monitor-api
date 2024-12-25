import os
from dotenv import load_dotenv

load_dotenv()

ORIGINS = ["http://localhost:3000"]

# LLM API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:1234")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# LLM Models
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-1.5-flash"

# Cohere API Key for Embeddings
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Supabase Configuration for database
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_ADMIN = os.getenv("SUPABASE_ADMIN")
