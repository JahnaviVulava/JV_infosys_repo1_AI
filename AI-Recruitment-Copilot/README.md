# AI Recruitment & Talent Management Copilot

A production-ready starter for an AI-powered recruiting workflow built with FastAPI, Streamlit, SQLAlchemy, MySQL, JWT, bcrypt, and resume parsing.

## Features

- Recruiter signup and login
- JWT-based authentication
- Password hashing with bcrypt
- OAuth 2.0 Google login support
- Resume upload for PDF and DOCX
- Resume parsing with pdfplumber and python-docx
- Candidate entity extraction with regex and spaCy-compatible pipelines
- MySQL persistence with SQLAlchemy
- Streamlit recruiter dashboard

## Project Structure

- backend/app: FastAPI application, auth, routers, services, models, schemas
- frontend/app.py: Streamlit frontend
- database/init.sql: MySQL initialization script
- uploads: uploaded resumes

## Setup

1. Create and activate a Python 3.12 virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up MySQL and create the `recruitment_ai` database.
4. Copy `.env.example` to `.env` and update values.
5. Start the API:
   ```bash
   python backend/main.py
   ```
6. Start the Streamlit UI:
   ```bash
   streamlit run frontend/app.py
   ```

## Environment Variables

```env
APP_NAME=AI Recruitment Copilot
APP_ENV=development
SECRET_KEY=change-me-to-a-long-secure-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/recruitment_ai
UPLOAD_DIR=uploads
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

## Docker

```bash
docker compose up --build
```

The backend will be available at http://localhost:8000 and the frontend at http://localhost:8501.
