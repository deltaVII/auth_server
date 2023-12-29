from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.environ.get("DB_URL")

TEST_DB_URL = os.environ.get("TEST_DB_URL")


SECRET_KEY = os.environ.get("SECRET_KEY")