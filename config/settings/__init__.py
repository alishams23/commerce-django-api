from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


for file_name in [".env.development", ".env"]:
    dotenv_path = BASE_DIR / file_name

    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print(f"*** Environment variables loaded from: '{file_name}' ***")
        break
