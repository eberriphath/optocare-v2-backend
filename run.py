import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("DATABASE_URL:", os.getenv("DATABASE_URL"))
    app.run(debug=True)