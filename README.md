# College Information AI Chatbot

## Features
- Student / Parent / Visitor registration
- Login / Logout
- Password hashing
- Session-based authentication
- College Q&A
- Course information
- Admission information
- Fees
- Departments
- Academic calendar
- Timetable
- Announcements
- Library
- Hostel
- Canteen
- Transport
- Campus navigation
- Contact information
- Text input
- Browser microphone input
- Text-to-speech
- SQLite database
- Flask backend

## Run in VS Code

### 1. Open this folder
Open `college_information_chatbot` in VS Code.

### 2. Create virtual environment
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install packages
```bash
pip install -r requirements.txt
```

### 4. Run
```bash
python app.py
```

### 5. Open browser
Go to:
http://127.0.0.1:5000

The SQLite database `college.db` will be created automatically.

## Important
The sample college information in `app.py` is demo data. Replace it with your actual college's:
- course list
- eligibility
- fees
- faculty/department details
- academic calendar
- timetable
- announcements
- library timings
- hostel rules/fees
- canteen timings
- bus routes
- campus building locations
- office/admission contacts

For production, move database administration to a protected admin panel and store SECRET_KEY in `.env`.
