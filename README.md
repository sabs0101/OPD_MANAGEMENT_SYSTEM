# OPD Management System

A Flask + MySQL web app for running a hospital or clinic's outpatient department (OPD) — patient records, doctor/nurse directories, and appointment scheduling, behind an admin login.

## Overview

Staff log in to a single dashboard to register patients, maintain the doctor and nurse lists, and book, edit, or cancel appointments. Each appointment can be downloaded as a PDF confirmation slip.

## Features

- **Admin authentication** — session-based login/logout protecting the dashboard and core management pages
- **Dashboard** — live counts of registered patients, doctors, and nurses
- **Patient management** — add, edit, delete, and list patients, with server-side validation (letters-only name, age 1–120, 10-digit phone number)
- **Doctor & nurse directory** — add and remove doctors/nurses, used when registering patients and booking appointments
- **Appointment scheduling** — book, edit, and cancel appointments; booking in the past is blocked
- **PDF appointment slip** — downloadable PDF confirmation (patient, doctor, date, time) generated with ReportLab
- **JSON APIs** — `/api/counts` and `/api/patients` for dashboard widgets or external use

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** MySQL via `mysql-connector-python`
- **PDF generation:** ReportLab
- **WSGI server:** Gunicorn
- **Deployment:** configured for Vercel (`vercel.json`, `@vercel/python`); also runnable anywhere Gunicorn works
- **Frontend:** server-rendered Jinja2 templates with static CSS/JS

## Project Structure

```
OPD_MANAGEMENT_SYSTEM/
├── app.py              # Flask app — routes, auth, DB queries, PDF generation
├── schema.sql           # Creates hospital_db and all tables, seeds a default admin
├── setup_db.py           # Standalone script to (re)create the appointments table locally
├── requirements.txt      # Python dependencies
├── vercel.json            # Vercel deployment config
├── templates/               # Jinja2 HTML templates (login, dashboard, forms, lists)
├── static/                     # CSS/JS/assets
└── .gitignore
```

## Database Schema

The app expects a MySQL database called `hospital_db` (see `schema.sql`):

- **admins** — `id`, `username`, `password`; seeded with a default `admin` / `admin123` account
- **doctors** — `doctor_id`, `name`
- **nurses** — `nurse_id`, `name`, `admin_id` (optional FK → `admins`)
- **patients** — `patient_id`, `name`, `age`, `gender`, `phone`, `family`, `disease`, `doctor`, `nurse` — the assigned doctor/nurse are stored as plain text, chosen from the doctor/nurse lists at registration
- **appointments** — `appointment_id`, `patient_id` (FK), `doctor_id` (FK), `appointment_date`, `appointment_time`, `created_at` — cascades on delete from patients/doctors

## Getting Started

### Prerequisites

- Python 3.9+
- A MySQL server (local or hosted)

### Installation

```bash
git clone https://github.com/sabs0101/OPD_MANAGEMENT_SYSTEM.git
cd OPD_MANAGEMENT_SYSTEM
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database setup

Run `schema.sql` against your MySQL server to create the database, tables, and default admin account:

```bash
mysql -u root -p < schema.sql
```

### Environment variables

`app.py` reads its DB connection from environment variables — set these before running the app:

- `MYSQLHOST` – MySQL server host
- `MYSQLUSER` – MySQL username
- `MYSQLPASSWORD` – MySQL password
- `MYSQLDATABASE` – database name (`hospital_db`)
- `MYSQLPORT` – MySQL port (usually `3306`)
- `PORT` *(optional)* – port the Flask app listens on locally (defaults to `5000`)

> These match the variable names Railway's MySQL plugin auto-generates, if that's where the database is hosted.

### Run locally

```bash
python app.py
```

Visit `http://localhost:5000` and sign in with the seeded credentials:

- **Username:** `admin`
- **Password:** `admin123`

## API Endpoints

- `GET /api/counts` — JSON counts of total patients, doctors, and nurses
- `GET /api/patients` — JSON list of all patient records

## Deployment

`vercel.json` is already set up to build `app.py` with `@vercel/python` and route all traffic to it — connect the repo on Vercel and add the environment variables above under project settings. Since `gunicorn` is also a dependency, the same app can run on any conventional Python host (Railway, Render, etc.) via `gunicorn app:app`.

## Notes & Possible Improvements

- `app.secret_key` is hardcoded and the admin password is stored in plain text — fine for coursework, but move the secret key to an environment variable and hash passwords (e.g. `werkzeug.security`) before using this beyond that
- `/api/counts`, `/api/patients`, `/doctors`, and `/nurses` aren't gated behind the admin-session check that protects the patient and appointment routes — worth aligning
- Possible additions: patient search/filtering, appointment reminders, role-based access for doctors and nurses

## Author

Built by [sabs0101](https://github.com/sabs0101).
