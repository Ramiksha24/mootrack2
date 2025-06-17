from pymongo import MongoClient
from geopy.distance import geodesic
from twilio.rest import Client
import datetime
import time
import random

# Twilio SMS Alert Setup
def send_sms_alert(body, to):
    account_sid = st.secrets["twilio"]["account_sid"]
    auth_token = st.secrets["twilio"]["auth_token"]
    from_number = st.secrets["twilio"]["from_number"]


    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_=from_number,
        to=to
    )
    print(f"📲 SMS sent! SID: {message.sid}")


# MongoDB Setup
client = MongoClient("mongodb+srv://RamikshaShetty:Rami%409632@mootrack.felumhi.mongodb.net/?retryWrites=true&w=majority&appName=mootrack")
db = client["mootrack"]
cow_locations = db["cow_locations"]
forest_zones = db["forest_zones"]
leopard_sightings = db["leopard_sightings"]

# Insert a synthetic leopard marker (only once)
leopard_exists = leopard_sightings.find_one({"leopard_id": "LEO_SYNTH001"})
if not leopard_exists:
    leopard_doc = {
        "leopard_id": "LEO_SYNTH001",
        "timestamp": datetime.datetime.utcnow(),
        "location": {
            "type": "Point",
            "coordinates": [74.8465, 13.6355]  # Near cow zone
        },
        "risk_level": "HIGH",
        "notes": "Test leopard inserted"
    }
    leopard_sightings.insert_one(leopard_doc)
    print("✅ Synthetic leopard marker inserted.")

# Simulated 10 cows at random starting points
base_lat = 13.635
base_lon = 74.846
cow_positions = {
    f"COW{i+1:03}": [base_lon + random.uniform(-0.002, 0.002), base_lat + random.uniform(-0.002, 0.002)]
    for i in range(10)
}

# Cooldown timer to avoid SMS spam
last_alert_time = {}

def should_alert(cow_id):
    now = datetime.datetime.utcnow()
    if cow_id not in last_alert_time or (now - last_alert_time[cow_id]).seconds > 600:
        last_alert_time[cow_id] = now
        return True
    return False

# Forest zone check
def is_inside_forest(coord):
    forest = forest_zones.find_one({})
    if not forest:
        print("⚠️ No forest zone found in DB.")
        return False

    poly = forest['area']['coordinates'][0]
    longitudes = [p[0] for p in poly]
    latitudes = [p[1] for p in poly]

    return (min(longitudes) <= coord[0] <= max(longitudes)) and \
           (min(latitudes) <= coord[1] <= max(latitudes))

# Leopard proximity check
def check_leopard_proximity(coord):
    sightings = leopard_sightings.find({})
    for sighting in sightings:
        leo_coord = sighting['location']['coordinates']
        dist = geodesic((coord[1], coord[0]), (leo_coord[1], leo_coord[0])).meters
        if dist < 300:
            return "HIGH"
    return "LOW"

# Cow simulation logic
def simulate_cow_movements(iterations=20):
    for step in range(iterations):
        print(f"\n🚶‍♀️ STEP {step + 1}")
        for cow_id, position in cow_positions.items():
            # Random movement
            lon_shift = random.uniform(-0.0003, 0.0003)
            lat_shift = random.uniform(-0.0003, 0.0003)
            position[0] += lon_shift
            position[1] += lat_shift

            cow_doc = {
                "cow_id": cow_id,
                "timestamp": datetime.datetime.utcnow(),
                "location": {
                    "type": "Point",
                    "coordinates": [position[0], position[1]]
                }
            }
            cow_locations.insert_one(cow_doc)
            print(f"🐄 {cow_id} at location: {[position[1], position[0]]}")

            # Danger checks
            in_forest = is_inside_forest(position)
            leopard_risk = check_leopard_proximity(position)

            if in_forest:
                print("🌲 Cow is INSIDE forest zone!")
            else:
                print("✅ Cow is outside forest zone.")

            print(f"🐆 Leopard Risk: {leopard_risk}")

            # Alert logic
            if (in_forest or leopard_risk == "HIGH") and should_alert(cow_id):
                msg = f"🚨 ALERT!\nCow: {cow_id}\nLocation: {position}\nForest: {'Yes' if in_forest else 'No'}\nLeopard Risk: {leopard_risk}"
                recipient = st.secrets["alert"]["recipient_number"]
                send_sms_alert(msg, recipient)

        time.sleep(5)

# Run it!
simulate_cow_movements()
