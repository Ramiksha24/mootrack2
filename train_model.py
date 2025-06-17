import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import joblib
import os

def generate_synthetic_data(n=1000):  # Increased dataset size
    """Generate synthetic data for cow risk prediction"""
    data = []
    time_options = ['morning', 'afternoon', 'evening', 'night']
    
    print(f" Generating {n} synthetic data points...")
    
    for _ in range(n):
        distance_to_forest = np.random.uniform(10, 1500)  # 10m to 1.5km
        distance_to_leopard = np.random.uniform(0, 2000)   # 0 to 2km
        time_of_day = np.random.choice(time_options)
        
        # Enhanced Risk Logic (more realistic)
        if distance_to_leopard < 50:
            risk = 'very high'
        elif distance_to_leopard < 100:
            risk = 'high' if np.random.random() > 0.2 else 'very high'
        elif distance_to_leopard < 200:
            risk = 'medium' if np.random.random() > 0.3 else 'high'
        elif distance_to_leopard < 500:
            risk = 'low' if np.random.random() > 0.4 else 'medium'
        else:
            risk = 'low'
        
        # Time-based risk adjustment
        if time_of_day in ['evening', 'night']:
            risk_levels = ['low', 'medium', 'high', 'very high']
            current_idx = risk_levels.index(risk)
            if current_idx < len(risk_levels) - 1 and np.random.random() > 0.6:
                risk = risk_levels[current_idx + 1]  # Increase risk at night
        
        # Forest proximity risk adjustment
        if distance_to_forest < 100:  # Very close to forest
            risk_levels = ['low', 'medium', 'high', 'very high']
            current_idx = risk_levels.index(risk)
            if current_idx < len(risk_levels) - 1 and np.random.random() > 0.7:
                risk = risk_levels[current_idx + 1]
        
        data.append({
            'distance_to_forest': round(distance_to_forest, 2),
            'distance_to_leopard': round(distance_to_leopard, 2),
            'time_of_day': time_of_day,
            'risk_level': risk
        })
    
    return pd.DataFrame(data)

# Generate the dataset
df = generate_synthetic_data(1000)
print(" Dataset generated successfully!")
print(f" Dataset shape: {df.shape}")
print(f" Risk level distribution:\n{df['risk_level'].value_counts()}")


print("\n Preprocessing data...")

# Prepare features and target
X = df[['distance_to_forest', 'distance_to_leopard', 'time_of_day']].copy()
y = df['risk_level']

# Encode time_of_day
time_encoder = LabelEncoder()
X['time_of_day_encoded'] = time_encoder.fit_transform(X['time_of_day'])

# Drop the original categorical column
X_processed = X[['distance_to_forest', 'distance_to_leopard', 'time_of_day_encoded']]

print(" Data preprocessing completed!")
print(f" Features: {list(X_processed.columns)}")
print(f" Classes: {list(time_encoder.classes_)}")


X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n Training set size: {X_train.shape[0]}")
print(f" Test set size: {X_test.shape[0]}")


print("\n Training Random Forest model...")

model = RandomForestClassifier(
    n_estimators=200,  # More trees for better performance
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced'  # Handle class imbalance
)

model.fit(X_train, y_train)
print(" Model training completed!")


print("\n Evaluating model performance...")

# Predictions
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# Training accuracy
train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f" Training Accuracy: {train_accuracy:.3f}")
print(f"Test Accuracy: {test_accuracy:.3f}")

print("\n Detailed Classification Report (Test Set):")
print(classification_report(y_test, y_test_pred))

# Feature importance
feature_names = ['Distance to Forest', 'Distance to Leopard', 'Time of Day']
importances = model.feature_importances_
print("\n🔍 Feature Importance:")
for name, importance in zip(feature_names, importances):
    print(f"  {name}: {importance:.3f}")


print("\n Saving models and data...")

try:
    # Save the trained model
    joblib.dump(model, "risk_predictor_model.pkl")
    print(" Model saved as 'risk_predictor_model.pkl'")
    
    # Save the time encoder
    joblib.dump(time_encoder, "time_of_day_encoder.pkl")
    print(" Encoder saved as 'time_of_day_encoder.pkl'")
    
    # Save the dataset
    df.to_csv("mootrack_risk_dataset.csv", index=False)
    print("Dataset saved as 'mootrack_risk_dataset.csv'")
    
    # Verify files were created
    files_created = []
    for filename in ["risk_predictor_model.pkl", "time_of_day_encoder.pkl", "mootrack_risk_dataset.csv"]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            files_created.append(f"{filename} ({size} bytes)")
        else:
            print(f"❌ Warning: {filename} was not created!")
    
    print(f"\n Files created: {files_created}")
    
except Exception as e:
    print(f"Error saving files: {e}")


print("\n Testing model loading...")

try:
    # Test loading the saved model
    loaded_model = joblib.load("risk_predictor_model.pkl")
    loaded_encoder = joblib.load("time_of_day_encoder.pkl")
    
    # Test prediction
    test_input = np.array([[500, 150, loaded_encoder.transform(['evening'])[0]]])
    test_prediction = loaded_model.predict(test_input)[0]
    
    print(f" Model loading test successful!")
    print(f" Test prediction: Distance to forest=500m, Distance to leopard=150m, Time=evening → Risk: {test_prediction}")
    
except Exception as e:
    print(f" Error testing model loading: {e}")

print("\n🎉 Model training pipeline completed successfully!")
print("\n📋 Next steps:")
print("1. Add the .pkl files to your Git repository")
print("2. Commit and push to GitHub")
print("3. Deploy your Streamlit app")
print("4. The app should now find the model files!")