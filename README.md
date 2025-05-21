# 🛰️ ISS It Above?
### ISS Tracker & Notification System

---

A Python program that tracks the International Space Station (ISS) and sends email notifications when it is overhead — but only if the conditions are right: the sky is clear, and the sun has set.

> *“Somewhere, something incredible is waiting to be known.”*  
> — *Carl Sagan*

---

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/d/d8/ISS_illustration.png" alt="ISS Tracker Banner" width="400" />
</div>

---

<details>
  <summary>📚 Table of Contents</summary>
  <ol>
    <li><a href="#about-this-project">📖 About This Project</a></li>
    <li><a href="#features">🚀 Features</a></li>
    <li><a href="#getting-started">🔧 Getting Started</a></li>
    <li><a href="#roadmap">🛣️ Roadmap</a></li>
    <li><a href="#built-with">🧪 Built With</a></li>
    <li><a href="#license">📜 License</a></li>
    <li><a href="#author">👤 Author</a></li>
  </ol>
</details>

---

## 📖 About This Project

As someone deeply fascinated by space and aspiring to become a hobbyist astrophotographer, I’ve long dreamed of capturing a photograph of the ISS streaking across the night sky.

This project began as a simple API learning exercise in a Python course, which quickly evolved into a personal passion project. I saw an opportunity to turn the program into a practical utility — something that could assist not only in honing my programming skills, but also support my future efforts in astrophotography.

The ISS Tracker checks a series of real-world conditions to determine whether the space station is visible from your location. Specifically, it:

- Pulls the live location of the ISS.
- Determines if the station is currently overhead (within a configurable margin of error).
- Uses local sunrise/sunset data to check if it's dark enough to see the stars.
- Checks weather forecasts to determine if cloud coverage is low enough for visibility.
- Runs all of the above checks for multiple users at simultaneously using multithreading.
- Sends automated email notifications when all the conditions are ideal.
- Logs all tracking and notification events in a structured report.

The program is designed for extensibility and is especially useful for space enthusiasts, or anyone who wants to be notified of ISS visibility in real-time.

---

## 🚀 Features

- Real-time ISS position tracking.
- Configurable location and visibility parameters.
- Multithreaded user checks for speed and efficiency.
- Email alerts with contextual messages and timestamps.
- Weather-based filtering (cloud cover thresholds).
- CSV logging of all events and actions.
- Modular and scalable design.

---

## 🔧 Getting Started

### 1️⃣ Clone the Repository

```bash
  git clone https://github.com/MapNotIncluded/ISS-it-above 
  cd ISS-it-above
```

### 2️⃣ Install Required Dependencies

```bash
  pip install -r requirements.txt
```

### 3️⃣ Create a .env File
Inside your project root, create a `.env` file and add the following:
```
ISS_API=https://api.open-notify.org/iss-now.json
SUNRISE_SUNSET_API=https://api.sunrise-sunset.org/json
CLOUD_COVER_API=https://api.open-meteo.com/v1/forecast
GEOLOCATION_API=https://api.geoapify.com/v1/geocode/search
GEOAPIFY_KEY=your_api_key_here
MY_EMAIL=youremail@example.com
APP_PASSWORD=your_email_app_password
```

### 4️⃣ Create a `users.json` File

Each user entry must include:
- A `Name`
- An `Email` address
- A full `Address` in the format: `Suburb, City, Country`

Example:
```json
[
  {
    "Name": "Alice",
    "Email": "alice@example.com",
    "Address": "Sea Point, Cape Town, South Africa"
  },
  {
    "Name": "Bob",
    "Email": "bob@example.com",
    "Address": "Wynberg, Cape Town, South Africa"
  }
]
```
📌 Ensure the address has exactly three components.

### 5️⃣ Run the Tracker
```bash
python3 iss_track.py
```
The tracker will periodically assess each user's sky visibility and notify them via email when the ISS is observable.

---

## 🛣️ Roadmap

- Allow dynamic user registration.
- Add live map visualization of ISS path.
- Secure personal data through encryption.
- Cache geolocation results for performance.
- Export log data into structured multi-sheet Excel reports.
- Track ideal viewing windows over time for analytics.

---

## 🧪 Built With

<p align="center">
  <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://requests.readthedocs.io"><img src="https://img.shields.io/badge/Requests-HTTP%20Client-6A5ACD?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://docs.python.org/3/library/smtplib.html"><img src="https://img.shields.io/badge/SMTP-Email%20Alerts-DC143C?style=for-the-badge&logo=gmail&logoColor=white"></a>
  <a href="https://pandas.pydata.org/"><img src="https://img.shields.io/badge/Pandas-Data%20Handling-000000?style=for-the-badge&logo=pandas&logoColor=white"></a>
  <a href="https://pypi.org/project/python-dotenv/"><img src="https://img.shields.io/badge/dotenv-Env%20Variables-228B22?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://git-scm.com"><img src="https://img.shields.io/badge/Git-Version%20Control-F1502F?style=for-the-badge&logo=git&logoColor=white"></a>
  <a href="https://github.com"><img src="https://img.shields.io/badge/GitHub-Repo%20Hosting-181717?style=for-the-badge&logo=github"></a>
</p>

<p align="right">(<a href="#top">back to top</a>)</p>

---

## 📜 License

This project is licensed under the MIT License.

---

## 👤 Author

**Jason Anderson**  
_Computer Science Student_  
_Interests: Programming • Cybersecurity • Data Science_  
GitHub: [@MapNotIncluded](https://github.com/MapNotIncluded)

<p align="right">(<a href="#top">back to top</a>)</p>
