from dotenv import load_dotenv
import os

load_dotenv()

# put global constants here

# also get environment variables here
# ex:
API_KEY = os.getenv("API_KEY") 
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
CORS_ORIGIN = os.getenv("CORS_ORIGINS", "")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGIN.split(",") if origin.strip()]
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "test_db")
DATABASE_CONNECT_TIMEOUT = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", 5000))
