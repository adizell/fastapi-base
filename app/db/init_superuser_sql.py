from dotenv import load_dotenv

load_dotenv()

from app.core.security import get_password_hash

hashed_password = get_password_hash("mm1cu1mm")
print(hashed_password)

# Execute este comando uma vez no seu banco de dados PostgreSQL para habilitar a extensão:
# CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Garanta que sua extensão uuid-ossp esteja criada:
# psql -U postgres -d fastapi_base -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

# Script abaixo executar no PostgreSQL
"""
INSERT INTO "user" (
  email, 
  hashed_password, 
  full_name, 
  is_active, 
  is_superuser, 
  id, 
  created_at, 
  updated_at
) 
VALUES (
  'adilsonmicuim@gmail.com', 
  -- Use o hash gerado na etapa anterior
  '$2b$12$kfB4NN7Ted9QWMu5swHb0OtvsOaFYAUCWSwlvZSt7XSZfSvIhbITu', 
  'System Administrator', 
  TRUE, 
  TRUE, 
  uuid_generate_v4(), 
  NOW(), 
  NOW()
);
"""
