# 🚨 Incident Tracker API (Backend)

A production-style incident tracking backend built with Flask, designed to simulate real-world support systems for logging, managing, and auditing incidents.

---

## 📌 Overview

This project models how operational teams handle incidents — including creation, updates, severity tracking, and audit logging — within a secure, API-driven system.

It emphasizes **clean architecture**, **security**, and **real-world backend practices**.

---

## ⚙️ Features

* 🔐 JWT Authentication (PyJWT)
* 👤 Role-based Authorization
* 📝 Incident CRUD (Create, Read, Update, Delete)
* ♻️ Soft Delete & Restore
* 🚫 Rate Limiting & Lockout Protection
* 📜 Request Logging & Audit Trail
* 📘 Swagger API Documentation
* 🧱 Repository + Service Layer Architecture
* 🧪 Integration Testing (pytest)
* 🐳 Dockerized Deployment

---

## 🧰 Tech Stack

### Language

* Python

### Framework & Libraries

* Flask
* Flasgger (Swagger Docs)
* Flask-Limiter
* PyJWT
* pytest
* python-dotenv
* gunicorn

### Infrastructure

* Docker
* Docker Compose
* PostgreSQL (Production)
* SQLite (Development)

---

## 🏗️ Project Structure

```
incident-tracker-api/
│
├── app.py
├── config.py
├── database.py
├── extensions.py
│
├── routes/
├── services/
├── repositories/
├── validators/
├── utils/
│
├── scripts/
│   └── init_db.py
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── schema.sql
├── pytest.ini
│
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone Repository

```
git clone https://github.com/your-username/incident-tracker-api
cd incident-tracker-api
```

---

### 2. Create Environment File

```
cp .env.example .env
```

Update `.env` with:

```
DATABASE_URL=your_database_url
JWT_SECRET=your_secret
```

---

### 3. Run with Docker

```
docker compose up --build
```

---

### 4. Access API

```
http://localhost:5000
```

Swagger docs available at:

```
/apidocs
```

---

## 🌐 Deployment

The API is deployed using Docker on Render.

---

## 🔮 Future Improvements

* Full PostgreSQL migration (production scaling)
* Frontend integration (React dashboard)
* Advanced analytics & reporting
* Role-based UI system

---

## 👤 Author

**Japhet Jeremiah**
Associate Degree in Computer Science

Interested in:

* Data Analytics
* Data Engineering
* Python Development
* Technical Support & Operations

---

## 📄 License

MIT License
