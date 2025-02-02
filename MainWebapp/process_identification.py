from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import subprocess
import base64

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Database connection
client = MongoClient(MONGO_URI)
db = client.latent_fingerprint
identification_requests_collection = db.identification_requests
latent_fingerprints_collection = db.latent_fingerprints_images

def process_identification_request(request_id):
    request = identification_requests_collection.find_one({"_id": ObjectId(request_id)})
    if not request:
        return

    fingerprint1_id = request["fingerprint1_id"]
    fingerprint1_type = request["fingerprint1_type"]
    fingerprint1_path = os.path.join("static/uploads", f"{fingerprint1_id}_{fingerprint1_type}.jpg")

    latent_fingerprints = list(latent_fingerprints_collection.find())
    results = []

    try:
        for latent_fingerprint in latent_fingerprints:
            fingerprint2_id = latent_fingerprint["_id"]
            fingerprint2_path = os.path.join("static/uploads", f"{fingerprint2_id}.jpg")

            with open(fingerprint2_path, "wb") as f2:
                f2.write(base64.b64decode(latent_fingerprint["image_data"]))

            result = subprocess.run(
                ["java", "-cp", "D:/Work/Project/WebApp/sourceafis-project/target/sourceafis-project-1.0-SNAPSHOT-jar-with-dependencies.jar", "com.example.FingerprintMatching", fingerprint1_path, fingerprint2_path],
                capture_output=True,
                text=True,
                shell=True
            )

            for line in result.stdout.splitlines():
                if "Similarity score:" in line:
                    similarity_score = float(line.split(":")[1].strip())
                    results.append((latent_fingerprint["filename"], similarity_score, latent_fingerprint["image_data"]))
                    break

            if os.path.exists(fingerprint2_path):
                os.remove(fingerprint2_path)

        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:20]

        identification_requests_collection.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "Completed", "results": results}}
        )

    finally:
        if os.path.exists(fingerprint1_path):
            os.remove(fingerprint1_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python process_identification.py <request_id>")
    else:
        process_identification_request(sys.argv[1])
