import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

FILES_DIR = BASE_DIR / "files"

# Configuration Object
class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "openai/gpt-oss-120b"
    PROMPT_PATH = FILES_DIR / "cover_letter_prompt.txt"
    TEMPLATE_FR = FILES_DIR / "template_fr.docx"
    TEMPLATE_EN = FILES_DIR / "template_en.docx"


settings = Settings()
