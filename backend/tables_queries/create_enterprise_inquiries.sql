-- Optional: run on main app PostgreSQL if you do not use SQLAlchemy create_all.
-- Normally the table is created when the main API starts (init_orm_tables).

CREATE TABLE IF NOT EXISTS enterprise_inquiries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    contact_email VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    username VARCHAR(100),
    status VARCHAR(32) NOT NULL DEFAULT 'new',
    notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_enterprise_inquiries_user_id ON enterprise_inquiries (user_id);
CREATE INDEX IF NOT EXISTS ix_enterprise_inquiries_status ON enterprise_inquiries (status);
