# 🐄 MooTrack: Real-Time Leopard Risk Alert System for Cattle 🐆

**Built for the AES Hackathon 2025 | Powered by ML, Twilio & GPS**

---

## 🚀 Overview

Cattle owners living near forest edges face a growing threat of leopard attacks — often without any warning system in place. **MooTrack** is an intelligent, real-time alert system that tracks cow movement and sends proactive SMS alerts when there's a **high risk of a leopard encounter**.

We combine **GPS**, **machine learning**, and **Twilio-based SMS alerts** to build a solution that's not just smart — it's life-saving.

---

## 🌱 Inspiration

Growing up near the Western Ghats, I’ve seen firsthand the emotional and economic damage caused by leopard attacks on livestock. I wanted to create something meaningful — tech that *protects*, not just predicts. MooTrack is my ode to nature and engineering.

---

## 🛠️ Tech Stack

| Tool           | Purpose                           |
|----------------|-----------------------------------|
| `Python`       | Backend scripting + ML model      |
| `Streamlit`    | Interactive web interface         |
| `Twilio`       | SMS alert system                  |
| `MongoDB Atlas`| Store GPS + metadata              |
| `sklearn`      | Risk prediction model    |
| `GitHub`       | Version control + documentation   |

---

## 🧠 How It Works

1. **Cow GPS data** is simulated or live-fed into the system.
2. ML model (`risk_predictor_model.pkl`) predicts **leopard attack risk** (LOW, MEDIUM, HIGH).
3. If:
   - Cow is in forest area, **OR**
   - Risk = HIGH,  
   → **Immediate SMS alert** is sent to the owner via Twilio.
4. Dashboard shows live location + status updates.

---

## 📊 ML Model Details

- Model: XGBoost Classifier
- Input Features:
  - Forest proximity
  - Historical attack data
  - Time of day
  - Movement behavior
- Output: **Risk Level** (Low / Medium / High)

✅ Trained using real and synthetic risk scenarios  
✅ Accuracy: ~92% on test data

---

## 🔒 Security

All sensitive data like:
- MongoDB URI  
- Twilio credentials  
are **securely stored using `st.secrets`**, ensuring zero secrets leak on GitHub.

---

## 📦 Features

- 🗺️ Live cow location tracking  
- 🔔 Real-time leopard risk alerts  
- 📤 Twilio SMS integration  
- 📈 Risk prediction using ML  
- 💾 MongoDB backend

---

## 🧪 Challenges Faced

- Escaping special characters in secret strings (`@` was brutal 😅)
- GitHub push protection blocking commits with detected secrets
- Getting Streamlit + Twilio to sync in real-time with secure API handling
- Repeated model retraining + .pkl regeneration cycles

But hey — we made it!

---

## 🎉 Accomplishments

- ⏱️ Deployed an end-to-end working MVP in under 3 days
- 💌 Built a functional, non-spammy Twilio SMS alert system
- 🎯 Hit 90%+ ML accuracy with minimal features
- 🌍 Built something that matters to rural communities

---

## 🧭 Future Roadmap

- 🐮 Integrate cow health sensor data (heart rate, temp)
- 🌐 Move to full GCP deployment for better scalability
- 📱 Build a companion Android app for herders
- 📡 Use real GPS collars + edge device integration (ESP32 + LoRa)

---

## 📽️ Demo

🎥 **Watch the full demo:** [YouTube Link Here](https://youtu.be/47vgPwIWSWw?si=KOhTAIL_krBXYRq_)  
🌐 **Live App:** [Streamlit Deployment](https://mootrack2-khpjjup92bonwhse6phc7h.streamlit.app/)

---

## 🤍 Made With

Love for nature, code, and a deep respect for farmers.

> _“Let’s make technology walk alongside animals, not just humans.”_ — **Ramiksha C. Shetty**

---

## 📫 Contact

Connect with me on [LinkedIn](https://www.linkedin.com/in/ramiksha-shetty/) | [GitHub](https://github.com/Ramiksha24)  
