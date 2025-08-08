from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "test_db")
DATABASE_CONNECT_TIMEOUT = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", 5000))