Incident Tracker Backend Project
=================================

This is a SaaS production-style incident tracking backend, it serves as a production service for logging incidents with full functioning user registry, authorization and authentication, using PyJWT to secure processing. It is built in Python , Flask, Sqlite and implements most real SaaS functions.

Project overview
================


I developed a backend incident tracking application using Python, Flask and SQLite, focusing on request lifecycle handling and data persistence. The application uses parameterized SQL queries to prevent injection risks and leverages Flask’s application and request contexts for safe database connection management. I separated schema initialization into an external SQL file for maintainability and structured routes to simulate a basic incident lifecycle workflow. The project models how support teams log, track, and close incidents in operational systems.

I chose Flask intentionally because I wanted greater control over the architecture and to better understand request handling and database lifecycle management at a lower level. Flask’s minimal design allowed me to focus on core backend mechanics like routing, context management, and SQL operations without the abstraction layers Django provides. For a small-scale incident tracker, Flask offered the right balance of simplicity and flexibility. If I had had the thought that the project would grow from a simple CRUD and require more built-in features like ORM support, admin panels, or rapid scaling to a larger application, Django would have been a strong alternative.

My focus was on modeling how real suport teams handle incidents, status changes, severity, and accountability,to demonstrate how real production systems would handle concerns by logging into a system and logging incidents by title, with description, with a measure of the severity of the incidence, and the app would then capture the user and loggers user_id, the time the incident is logged, and also keep track by audit, who and when an update, delete or restore is done.

In my first week, I started of with a basic flask application, a small system with API key authorization, html rendering, basically a simple system. After realizing the finilization of the CRUD app, I move d on to persistent moemory, and turned it to an API. Focus was on the backend and as it grew and more pieces and logical steps turned it into the product we see today.

Key Features
============
JWT authentication
role authorization
Soft Delete and restore
rate limiting
Lockout protection
request logging
Swagger docs
repository pattern
service layer
integration tests
Docker support

Tech Stack
==========

languages:
----------

Python

Libraries:
----------

Flask
Flasgger
Flask-Limiter
PyJWT
pytest
python-dotenv
gunicorn

Infrustructure
==============
Docker
Docker compose

Other Tools
===========

Git
GitHub

Project Architecture
====================

incident-tracker-api
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
├── .gitignore
├── .env.example
└── README.md

Installation
============

1. Clone the repository

git clone https://github.com/jaazbogati/incident_tracker

2. Create environment file

cp .env.example .env

3. Add your API keys to .env

4. Start services

docker compose up --build

Future Improvements
===================
Migration from SQLite to production grade PostgreSQL
Develop UI/UX
Refactoring to support frontend and mobile intergration

Author
======

Japhet Jeremiah
Associate Degree in Computer Science

Interested in opportunities in:
- Data Analytics
- Data Engineering
- Python Development
- IT Support & Technical Operations

License
=======

This Project is licenced under the MIT License.
