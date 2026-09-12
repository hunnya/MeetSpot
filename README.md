# MeetSpot — The Fair Meeting Point Finder

> **"Stop arguing about where to meet."**
> 
> MeetSpot finds the fairest meeting point based on how long everyone actually has to travel.

---

## Overview

Groups of friends, colleagues, or students frequently struggle to agree on a fair place to meet. Standard mapping solutions calculate a simple geometric midpoint (geographic centroid), which completely ignores road networks, one-way bridges, rivers, and traffic congestion. As a result, one friend drives 45 minutes while another walks 5 minutes.

**MeetSpot** solves this by balancing **actual road travel times** across all group members using **OSRM**. It then retrieves nearby restaurants, cafes, or hotels via **OpenStreetMap Overpass**, ranks them against group preferences with **Groq AI (Llama 3.3)**, checks the meetup weather using **Open-Meteo**, and displays everything on a polished, interactive **Folium map**.

---

## Features

-  **Multi-Participant Input**: Supports 2 to 8 participants with custom starting addresses or landmarks.
-  **Real Travel-Time Fairness Algorithm**: Evaluates candidate road network nodes around the geographic centroid and selects the location that minimizes travel time disparity (`Max - Min`).
-  **Interactive Map**: Centered on the fair meeting point with color-coded pins for each participant, recommended venues, and travel routes.
-  **Nearby Place Suggestions**: Curates nearby cafes, restaurants, fast food, and hotels directly from OpenStreetMap.
-  **AI Preference Ranking & Explanations**: Uses Groq LLM inference (`llama-3.3-70b-versatile`) to rank places by cuisine, atmosphere, budget, and free-text queries, with an intelligent deterministic fallback if no API key is provided.
-  **Meeting Date Weather Forecast**: Fetches high/low temperature, rain chance, and outdoor dining advice via Open-Meteo.
-  **User Accounts & Authentication**: Secure registration and login powered by bcrypt password hashing and SQLAlchemy.
-  **Saved Meetings & Favorites**: Authenticated users can save meetings and bookmark recommended venues to SQLite.
-  **Fail-Safe Demo Mode**: Built-in toggle and preset Islamabad test case so the demo never fails during hackathon judging.

---

##  Tech Stack & Architecture

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend / UI** | Streamlit 1.58 + Folium | Web application, forms, charts, and interactive map |
| **Backend & Logic** | Python 3.10+ | Algorithm engine, API integrations, data processing |
| **Geocoding** | OpenStreetMap Nominatim | Free address-to-coordinate translation (with caching & throttling) |
| **Routing / Distance** | OSRM Table API | Driving travel times across actual road networks |
| **Nearby Places** | OpenStreetMap Overpass API | Restaurants, cafes, fast food, and hotels |
| **Weather** | Open-Meteo API | Daily temperature and precipitation forecasts |
| **AI / LLM** | Groq API (`llama-3.3-70b-versatile`) | Group preference matching and human-readable explanation |
| **Database** | SQLite + SQLAlchemy 2.0 | User accounts, saved meetings, and favorites |
| **Security** | bcrypt | Password hashing with cryptographic salts |

---

##  Fairness Algorithm Explained

MeetSpot avoids the geometric midpoint fallacy by optimizing for **travel-time parity**:

1. **Centroid Calculation**: Computes the geographic centroid of all participant coordinates:
   $$\bar{\phi} = \frac{1}{N}\sum_{i=1}^{N} \phi_i, \quad \bar{\lambda} = \frac{1}{N}\sum_{i=1}^{N} \lambda_i$$
2. **Adaptive Candidate Generation**: Generates concentric rings of candidate road coordinates around the centroid, scaled dynamically to the group's geographic spread, plus pairwise midpoints between participants.
3. **Matrix Travel-Time Query**: Queries the **OSRM Table API** in a single batch request to compute the driving duration $T_{i, k}$ for each participant $i$ to each candidate point $k$.
4. **Objective Optimization**:
   $$\text{Travel Time Gap}_k = \max_i(T_{i, k}) - \min_i(T_{i, k})$$
   $$\text{Average Time}_k = \frac{1}{N}\sum_{i=1}^{N} T_{i, k}$$
   $$\text{Fairness Score}_k = 2.0 \times \text{Travel Time Gap}_k + 0.5 \times \text{Average Time}_k$$
5. **Selection**: Selects the candidate that minimizes the Fairness Score, ensuring the spread between the longest and shortest journeys is minimized without sending everyone unreasonably far away.
6. **Robust Fallback**: If OSRM is temporarily unreachable, the algorithm falls back to Haversine distance with urban winding correction and clearly alerts the user.

---

##  Project Structure

```
meetspot/
├── app.py                     # Main Streamlit application entry point
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
├── .env.example               # Environment variables template
├── .gitignore                 # Standard Python/Streamlit gitignore
│
├── database/
│   ├── __init__.py
│   ├── database.py            # SQLite connection, session factory, init_db()
│   └── models.py              # User, SavedMeeting, MeetingMember, Favorite
│
├── auth/
│   ├── __init__.py
│   └── authentication.py      # Registration, bcrypt hashing, session auth
│
├── services/
│   ├── __init__.py
│   ├── geocoding.py           # Nominatim geocoding & reverse geocoding
│   ├── routing.py             # OSRM Table API integration + Haversine fallback
│   ├── places.py              # Overpass API nearby venue retrieval
│   ├── weather.py             # Open-Meteo forecast service
│   └── ai.py                  # Groq LLM ranking + deterministic fallback
│
├── algorithms/
│   ├── __init__.py
│   └── fairness.py            # Multi-candidate travel-time optimization
│
├── ui/
│   ├── __init__.py
│   ├── styles.py              # Executive Map-Blue CSS and hero styling
│   ├── auth_ui.py             # Sign in, Sign up, Profile views
│   ├── meeting_ui.py          # Input form, participant controls, presets
│   ├── results_ui.py          # Winner card, Folium map, bar chart, places
│   ├── history_ui.py          # Saved meetings management
│   └── favorites_ui.py        # Saved favorite places browser
│
├── utils/
│   ├── __init__.py
│   ├── caching.py             # Thread-safe TTL cache for API responses
│   ├── validation.py          # Participant input and coordinate sanity checks
│   └── demo_data.py           # Realistic Islamabad demo data
│
└── data/
    └── .gitkeep               # Directory for local SQLite database (meetspot.db)
```

---

## Quickstart Guide

### Prerequisites
- Python 3.10+ installed.

### 1. Clone or Open Project
Navigate to the project directory:
```bash
cd meetspot
```

### 2. Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

To enable Groq AI features:
1. Create a free account at [console.groq.com](https://console.groq.com/).
2. Create an API key.
3. Add it to `.env`:
```env
GROQ_API_KEY=gsk_your_actual_key_here
DEMO_MODE=false
```
*(Note: If you do not have a Groq key, MeetSpot works completely out-of-the-box using its deterministic rule-based ranking engine).*

### 5. Launch the Application
```bash
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`.

---

## Offline Demo Mode

For live judging presentations, network drops or public API rate-limits can be disastrous. MeetSpot includes a **Fail-Safe Demo Mode**:
- In the sidebar, toggle **"Enable Offline Demo Mode"**.
- Or click **"🚀 Load Islamabad Demo"** in the main form.
- The app will instantly display a realistic scenario with 4 participants across Islamabad (Hunnya in H-11, Ali in F-10, Sara in I-8, Bilal in Blue Area), balancing travel times around Centaurus/F-8 junction within a 4-minute gap.

---

## Future Roadmap

-  **Multi-Modal Transit Toggles**: Separate fairness calculations for driving, public transit, and walking.
-  **Shareable Meetup Links**: Unique invite URLs allowing each group member to enter their location without logging in.
-  **Group Voting System**: In-app voting between top 3 candidate venues.
-  **Ride Fare Estimator**: Integrated Careem/Uber/Indrive fare approximations for each member.

---

## License
MIT License. Built with passion for hackathon innovation.
