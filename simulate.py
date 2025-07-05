# cow_simulator.py

import pymongo
import random
from datetime import datetime
import time
import streamlit as st

# --- Load secrets (Mongo URI) ---
mongo_uri = st.secrets["mongo"]["connection_string"]

# Connect to MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client["mootrack"]
collection = db["cow_locations"]

# Base location for cows
base_lat, base_lon = 13.0000, 74.8000  # You can change this to your actual farm area
num_cows = 5

# List of cow IDs
cow_ids = [f"COW{i+1}" for i in range(num_cows)]

# Track cow positions
cow_positions = {
    cow_id: {
        "lat": base_lat + random.uniform(-0.005, 0.005),
        "lon": base_lon + random.uniform(-0.005, 0.005)
    } for cow_id in cow_ids
}

print("🚜 Starting MooTrack cow simulator (MongoDB edition)...")

while True:
    for cow_id, pos in cow_positions.items():
        # Random small movement
        pos["lat"] += random.uniform(-0.0001, 0.0001)
        pos["lon"] += random.uniform(-0.0001, 0.0001)

        # Construct MongoDB document
        doc = {
            "cow_id": cow_id,
            "timestamp": datetime.utcnow(),
            "location": {
                "type": "Point",
                "coordinates": [pos["lon"], pos["lat"]]
            }
        }

        # Insert updated cow position into MongoDB
        collection.insert_one(doc)
        print(f"🐄 Updated {cow_id} → ({pos['lat']:.6f}, {pos['lon']:.6f})")

    # Sleep before next update
    time.sleep(5)

