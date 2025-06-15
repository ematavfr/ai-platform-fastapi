# Script d'initialisation de la base de données
-- Création des extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Insertion de données de test (utilisateur admin)
INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser, role)
VALUES (
    uuid_generate_v4(),
    'admin@aiplatform.com',
    'admin',
    'Administrator',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- password: admin123
    true,
    true,
    'admin'
) ON CONFLICT (email) DO NOTHING;