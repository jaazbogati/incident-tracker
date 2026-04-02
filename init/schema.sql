-- DROP TABLE IF EXISTS incidents;
-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS incident_events;


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',
    is_active INTEGER NOT NULL DEFAULT 1,
    token_version INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP DEFAULT NULL
);

CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_by INTEGER DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT NULL,
    deleted_at TIMESTAMP DEFAULT NULL,
    deleted_by INTEGER DEFAULT NULL,

    FOREIGN KEY (deleted_by)
        REFERENCES users(id),

    FOREIGN KEY (created_by)
        REFERENCES users(id),

    FOREIGN KEY (updated_by)
        REFERENCES users(id)

);

CREATE TABLE incident_events (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER,
    event_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    performed_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,

    FOREIGN KEY (incident_id)
        REFERENCES incidents(id),

    FOREIGN KEY (performed_by)
        REFERENCES users(id)
);
