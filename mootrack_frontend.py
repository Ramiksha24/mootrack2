import streamlit as st

# CRITICAL: st.set_page_config() MUST be the very first Streamlit command
st.set_page_config(layout="wide", page_title="MooTrack Dashboard", page_icon="🐄")

# Now import everything else
from streamlit_folium import st_folium
import folium
import pymongo
import time
from geopy.distance import geodesic
import joblib
import numpy as np
from datetime import datetime
import os

# -----------------------
# Load ML Model + Encoder with better error handling
# -----------------------
@st.cache_resource
def load_ml_models():
    """Load ML model and encoder with proper error handling"""
    try:
        # Try multiple possible paths
        possible_paths = [
            ("risk_predictor_model.pkl", "time_of_day_encoder.pkl"),  # Same directory
            ("./risk_predictor_model.pkl", "./time_of_day_encoder.pkl"),  # Current directory
            (os.path.join(".", "risk_predictor_model.pkl"), os.path.join(".", "time_of_day_encoder.pkl")),
        ]
        
        model, encoder = None, None
        for model_path, encoder_path in possible_paths:
            try:
                if os.path.exists(model_path) and os.path.exists(encoder_path):
                    model = joblib.load(model_path)
                    encoder = joblib.load(encoder_path)
                    st.success(f"✅ Models loaded from: {model_path}")
                    return model, encoder, True
            except Exception as e:
                continue
        
        # If we get here, no models were found
        st.error("🚫 ML model files not found. Available files:")
        current_dir = os.listdir(".")
        st.write(current_dir)
        return None, None, False
        
    except Exception as e:
        st.error(f"🚫 Error loading ML models: {str(e)}")
        return None, None, False

# Load the models
model, encoder, model_loaded = load_ml_models()

# -----------------------
# MongoDB Connection with secrets support
# -----------------------
@st.cache_resource
def init_mongodb():
    """Initialize MongoDB connection"""
    try:
        # Try to use secrets first, fallback to hardcoded for now
        if "mongo" in st.secrets:
            mongo_uri = st.secrets["mongo"]["connection_string"]
        else:
            # Fallback to your existing connection (move to secrets later)
            mongo_uri = "mongodb+srv://RamikshaShetty:Rami%409632@mootrack.felumhi.mongodb.net/?retryWrites=true&w=majority&appName=mootrack"
        
        client = pymongo.MongoClient(mongo_uri)
        # Test the connection
        client.admin.command('ping')
        db = client["mootrack"]
        st.success("✅ Connected to MongoDB")
        return db, client, True
    except Exception as e:
        st.error(f"🚫 MongoDB connection failed: {str(e)}")
        return None, None, False

# Initialize MongoDB
db, client, db_connected = init_mongodb()

# FIX: Only access collections if database connection is successful
if db_connected and db is not None:
    cow_locations = db["cow_locations"]
    leopard_sightings = db["leopard_sightings"]
    forest_zones = db["forest_zones"]
else:
    cow_locations = None
    leopard_sightings = None
    forest_zones = None
    st.error("🚫 Cannot access database collections - MongoDB connection failed")
    st.stop()

# -----------------------
# Helper Functions
# -----------------------
def get_time_of_day():
    """Get current time of day category"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 20:
        return 'evening'
    else:
        return 'night'

def predict_risk(dist_forest, dist_leopard, time_of_day):
    """Predict risk level using ML model"""
    if not model_loaded or model is None or encoder is None:
        return "N/A"
    
    try:
        time_encoded = encoder.transform([time_of_day])[0]
        X = np.array([[dist_forest, dist_leopard, time_encoded]])
        prediction = model.predict(X)[0]
        return prediction
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        return "Error"

# -----------------------
# Streamlit UI
# -----------------------
st.title("🐄 MooTrack Dashboard")
st.markdown("### Real-time Cow Tracking + AI Leopard Risk Prediction")

# Status dashboard
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🤖 ML Model", "✅ Loaded" if model_loaded else "❌ Not Found")
with col2:
    st.metric("🗄️ Database", "✅ Connected" if db_connected else "❌ Failed")
with col3:
    current_time = get_time_of_day()
    st.metric("🕐 Time", current_time.title())
with col4:
    if st.button("🔄 Refresh"):
        st.cache_resource.clear()
        st.rerun()

# Show current directory contents for debugging (remove in production)
with st.expander("🔍 Debug Info (Current Directory Contents)"):
    try:
        files = os.listdir(".")
        st.write("Files in current directory:", files)
        st.write("Current working directory:", os.getcwd())
    except Exception as e:
        st.write(f"Error listing files: {e}")

# Auto-update info
st.info("⏳ Map updates in real-time. Click refresh to manually update data.")

# -----------------------
# Fetch Data from MongoDB with error handling
# -----------------------
cows = []
leopards = []
forest = None

if db_connected and db is not None:
    try:
        cows_cursor = cow_locations.find().sort("timestamp", -1).limit(10)
        cows = list(cows_cursor)
        leopards = list(leopard_sightings.find())
        forest = forest_zones.find_one()
        
        # Data summary
        st.write(f"📊 **Data Summary**: {len(cows)} cows tracked, {len(leopards)} leopard sightings")
        
    except Exception as e:
        st.error(f"❌ Error fetching data from MongoDB: {str(e)}")
        cows, leopards, forest = [], [], None
else:
    st.warning("⚠️ Database not connected - cannot fetch tracking data")

# -----------------------
# Draw Map
# -----------------------
if cows:
    try:
        # Center map on the first cow
        first_cow = cows[0]
        cow_lat = first_cow["location"]["coordinates"][1]
        cow_lon = first_cow["location"]["coordinates"][0]
        
        # Create the map
        map_obj = folium.Map(
            location=[cow_lat, cow_lon], 
            zoom_start=15,
            tiles='OpenStreetMap'
        )

        # Add forest zone polygon if available
        if forest and "area" in forest:
            try:
                forest_coords = [(pt[1], pt[0]) for pt in forest["area"]["coordinates"][0]]
                folium.Polygon(
                    locations=forest_coords,
                    color="green",
                    weight=2,
                    fill=True,
                    fill_opacity=0.2,
                    popup="🌲 Forest Zone"
                ).add_to(map_obj)
            except Exception as e:
                st.warning(f"Could not draw forest zone: {e}")

        # Add leopard markers first (so they appear below cow markers)
        leopard_positions = []
        for leo in leopards:
            try:
                leo_coords = leo["location"]["coordinates"]
                leo_lat, leo_lon = leo_coords[1], leo_coords[0]
                leopard_positions.append((leo_lat, leo_lon))
                
                # Leopard marker
                folium.Marker(
                    [leo_lat, leo_lon],
                    icon=folium.Icon(color='red', icon='info-sign'),
                    popup=f"🐆 Leopard Sighting<br>Time: {leo.get('timestamp', 'Unknown')}"
                ).add_to(map_obj)

                # Danger zone circle
                folium.Circle(
                    radius=300,
                    location=[leo_lat, leo_lon],
                    color="red",
                    weight=2,
                    fill=True,
                    fill_opacity=0.1,
                    popup="⚠️ Danger Zone (300m radius)"
                ).add_to(map_obj)
            except Exception as e:
                st.warning(f"Error adding leopard marker: {e}")

        # Add cow markers
        risk_summary = {"low": 0, "medium": 0, "high": 0, "very high": 0, "N/A": 0}
        
        for cow in cows:
            try:
                coords = cow["location"]["coordinates"]
                lat, lon = coords[1], coords[0]
                cow_id = cow.get("cow_id", "Unknown")
                timestamp = cow.get("timestamp", "Unknown")

                # Calculate distance to forest center
                if forest and "area" in forest:
                    try:
                        poly_coords = forest["area"]["coordinates"][0]
                        avg_lat = sum([pt[1] for pt in poly_coords]) / len(poly_coords)
                        avg_lon = sum([pt[0] for pt in poly_coords]) / len(poly_coords)
                        dist_to_forest = geodesic((lat, lon), (avg_lat, avg_lon)).meters
                    except:
                        dist_to_forest = 999
                else:
                    dist_to_forest = 999

                # Calculate distance to nearest leopard
                nearest_leopard_dist = 9999
                if leopard_positions:
                    for leo_lat, leo_lon in leopard_positions:
                        dist = geodesic((lat, lon), (leo_lat, leo_lon)).meters
                        nearest_leopard_dist = min(nearest_leopard_dist, dist)

                # Predict risk level
                current_time = get_time_of_day()
                risk = predict_risk(dist_to_forest, nearest_leopard_dist, current_time)
                risk_summary[risk] = risk_summary.get(risk, 0) + 1

                # Choose marker color based on risk
                if risk in ["high", "very high"]:
                    color = "red"
                elif risk == "medium":
                    color = "orange"
                elif risk == "low":
                    color = "green"
                else:
                    color = "blue"  # For N/A or errors

                # Create popup with cow information
                popup_text = f"""
                🐄 <b>Cow ID:</b> {cow_id}<br>
                🕐 <b>Last Update:</b> {timestamp}<br>
                🌲 <b>Distance to Forest:</b> {dist_to_forest:.0f}m<br>
                🐆 <b>Distance to Leopard:</b> {nearest_leopard_dist:.0f}m<br>
                🧠 <b>AI Risk Level:</b> <b style="color: {color};">{risk.upper()}</b>
                """

                # Add cow marker
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(map_obj)

            except Exception as e:
                st.warning(f"Error processing cow {cow.get('cow_id', 'Unknown')}: {e}")

        # Display the map
        st.subheader("🗺️ Live Tracking Map")
        map_data = st_folium(map_obj, width=1200, height=600, returned_objects=["last_clicked"])

        # Risk summary
        st.subheader("📊 Risk Level Summary")
        risk_cols = st.columns(len([k for k, v in risk_summary.items() if v > 0]))
        for i, (risk_level, count) in enumerate([(k, v) for k, v in risk_summary.items() if v > 0]):
            if i < len(risk_cols):
                with risk_cols[i]:
                    color_map = {"low": "🟢", "medium": "🟡", "high": "🟠", "very high": "🔴", "N/A": "⚪"}
                    st.metric(f"{color_map.get(risk_level, '⚪')} {risk_level.title()}", count)

    except Exception as e:
        st.error(f"❌ Error creating map: {str(e)}")
        st.write("Debug info:", str(e))

else:
    st.warning("📍 No cow location data found in the database.")
    st.info("💡 **Tip**: Run your cow simulator script to generate sample tracking data.")
    
    # Show sample data structure for debugging
    st.subheader("Expected Data Structure")
    st.code("""
    Cow Document:
    {
        "cow_id": "COW001",
        "timestamp": datetime,
        "location": {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
    }
    """)

# -----------------------
# Connection Troubleshooting Section
# -----------------------
if not db_connected:
    st.error("🔧 **Troubleshooting MongoDB Connection**")
    st.markdown("""
    **Common issues and solutions:**
    
    1. **Network Access**: Check if your IP address is whitelisted in MongoDB Atlas
    2. **Credentials**: Verify username/password are correct
    3. **Connection String**: Ensure the connection string is properly formatted
    4. **Firewall**: Check if your firewall is blocking MongoDB connections (port 27017)
    
    **Quick fixes to try:**
    - Restart your internet connection
    - Check MongoDB Atlas dashboard for connection issues
    - Try connecting from a different network
    - Update your IP whitelist in MongoDB Atlas
    """)

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.markdown("**MooTrack** - AI-Powered Livestock Protection System | Built with ❤️ using Streamlit")