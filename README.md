## 🚨 Smart Accident Response & Management System (SARMS)

SARMS is a **real-time emergency coordination platform** designed to significantly reduce medical response time during road accidents. It bridges the gap between accident occurrence and hospital action with a minimal, fast, and life-saving solution.

***

## 💡 Project Idea & Problem

### Problem Statement
Delay in emergency response is a major cause of death in road accidents. This delay is primarily caused by a lack of immediate and accurate reporting by witnesses, poor coordination between citizens, ambulances, and hospitals, and hospitals not knowing the severity of an incident early enough.

### Solution Overview
SARMS provides a **single-tap reporting platform** where any nearby witness can quickly report an accident.

The system automatically performs the following actions:
1.  Captures **GPS coordinates** and **timestamp**.
2.  Lets the reporter choose the **severity** (Minor / Moderate / Severe).
3.  Automatically finds and alerts **nearby hospitals or ambulance services** using the Google Maps API.
4.  Provides a **Responder Dashboard** for real-time tracking of the accident status: `Reported` → `Alerted` → `En Route` → `Resolved`.

***

## ⚙️ Technology Stack

| Component | Technology / Service | Details |
| :--- | :--- | :--- |
| **Backend** | **Python (Django REST Framework)** | Used for the core application logic and API endpoints. |
| **Frontend** | **HTML/CSS/JS (Responsive Web App)** | User interface for both Reporter and Responder roles. |
| **Real-time Data** | **Google Firestore** | Used for real-time status updates and data synchronization (e.g., in the tracking and responder dashboards). |
| **Mapping/Location** | **Google Maps API** | Utilized for **Nearby Search** and **Distance Matrix** features to find and route emergency services. |


***

## 🚀 Getting Started

These instructions will get you the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.12
* Django 
* Google Maps API Key
* Firebase/Firestore Service Account Key (`serviceAccountKey.json`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd SARMS
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    *(Assuming a standard Django project structure and dependencies)*
    ```bash
    pip install django djangorestframework firebase-admin python-dotenv
    ```
    *Note: You may need to create a `requirements.txt` file based on your exact setup.*

4.  **Configure Environment Variables:**
    Create a `.env` file or update your Django `settings.py` with the necessary API keys.
    * **GOOGLE\_MAPS\_API\_KEY**: Your Google Maps API key.
    * **SECRET\_KEY**: Django Secret Key.
    * **FIREBASE\_CONFIG**: Ensure your `serviceAccountKey.json` is correctly placed and configured for Firebase Admin SDK initialization.

5.  **Run Migrations:**
    ```bash
    python manage.py makemigrations core
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.

***

## 🗺️ Key Functionality & Roles

The system is split into two primary roles, accessible from the home page:

### 1. Reporter (Citizen)
* **Login:** Reporter logs in with their name and phone number (session-based).
* **Report Accident:** Fills a form including description, selects severity (Minor/Moderate/Severe), and pinpoints the location on a map.
* **Tracking:** Views a real-time status page (`/reporter/tracking/<id>/`) showing the progress of their report (Reported, Alerted, En Route, Resolved), hospital assignment, live distance, and estimated time of arrival (ETA).
