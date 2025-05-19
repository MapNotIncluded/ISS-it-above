# 🛰️ ISS It Above?
### ISS Tracker & Notification System

---

A Python program that tracks the International Space Station (ISS) and sends email notifications when it is overhead — but only if the conditions are right: the sky is clear, and it’s dark enough to see the stars.


> *“Somewhere, something incredible is waiting to be known.”*  
> — *Carl Sagan*

---


## 📖 About This Project

As someone deeply fascinated by space and aspiring to become a hobbyist astrophotographer, I’ve long dreamed of capturing a photograph of the ISS streaking across the night sky.

What began as a simple Python learning exercise during a course, quickly evolved into a personal passion project. I saw an opportunity to turn the program into a practical utility — something that could assist not only in honing my programming skills, but also support my future efforts in astrophotography.

This ISS Tracker is designed to provide timely, condition-aware notifications by checking when the ISS is overhead, verifying local darkness, and assessing cloud cover — all essential factors for a clear viewing or photography session.

Through continued refinement, this project has grown into a robust and extensible tool that bridges my interest in space with my enthusiasm for programming and automation.

---

## 🚀 Features

- 🌍 Real-time ISS position tracking via API
- 🌙 Detection of darkness using solar data
- ☁️ Cloud cover filtering for visibility
- 📬 Email alerts to configured recipients
- 🧠 Configurable thresholds (error margin, pass count, etc.)
- 📊 CSV report logging for runtime status
- 🔐 Secure use of environment variables with `.env`

---
## 🔧 Getting Started

### 1️⃣ Clone the Repository

```bash
  git clone https://github.com/your-username/iss-tracker.git
  cd iss-tracker
```

### 2️⃣ Install Required Dependencies

```bash
  pip install -r requirements.txt
```

### 3️⃣ Create a .env File
Inside your project root, create a .env file and add the following:
```
ISS_API=https://api.open-notify.org/iss-now.json
SUNRISE_SUNSET_API=https://api.sunrise-sunset.org/json
CLOUD_COVER_API=https://api.open-meteo.com/v1/forecast

MY_EMAIL=youremail@example.com
APP_PASSWORD=your_email_app_password
```
⚠️ Important: Make sure .env and ISS_Report.csv are listed in your .gitignore so they are never committed to GitHub.

### 4️⃣ Run the Tracker
```
python3 iss_track.py
```
The program will periodically check conditions and send notifications if the ISS is visible from your location.

---

## 🛣️ Roadmap

- ✉️ Add user-friendly input system for email and location
- 📤 Integrate a scalable email service like SendGrid or Mailgun
- 🖥️ Build a simple web dashboard or GUI for viewing ISS data
- 🗺️ Add map-based visualization of ISS passes
- 🌐 Include configurable location/timezone support
- 🧠 Improve error logging and API retry diagnostic

---
## 🧪 Built With

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-HTTP%20Client-purple?logo=python&logoColor=white)
![SMTP](https://img.shields.io/badge/SMTP-Email%20Protocol-red?logo=gmail&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Handling-black?logo=pandas&logoColor=white)
![dotenv](https://img.shields.io/badge/dotenv-Environment%20Config-green?logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-Version%20Control-orange?logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-Repo%20Hosting-181717?logo=github)

---


## 📜 License
This project is licensed under the MIT License.

---

## 👤 Author

**Jason Anderson**  
_Computer Science Student_  
_Interests: Programming • Cybersecurity • Data Science_  
GitHub: @MapNotIncluded

---