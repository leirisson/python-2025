-- Criação da tabela de usuarios

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    age INTEGER,
    uf TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);