from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Database connection
client = MongoClient(MONGO_URI)
db = client.latent_fingerprint

# Create an index on the timestamp field
db.identification_results.create_index([("timestamp", -1)])
print("Index created on the timestamp field.")
