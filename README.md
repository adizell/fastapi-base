### Root Project

[![wakatime](https://wakatime.com/badge/user/d8ce363b-6bd3-43fb-a4bf-6c3fc2a9dd90/project/f37ba62e-15ed-4139-9be1-2ab69e1fa39f.svg)](https://wakatime.com/badge/user/d8ce363b-6bd3-43fb-a4bf-6c3fc2a9dd90/project/f37ba62e-15ed-4139-9be1-2ab69e1fa39f)

```python
fastapi-project/
│
├── alembic/                    # Migrations do banco de dados
│   └── versions/               # Versões de migrações
│
├── app/                        # Código principal da aplicação
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada da aplicação
│   │
│   ├── api/                    # Rotas da API versionadas
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependências específicas da API
│   │   ├── v1/                 # API v1
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Router principal da v1
│   │   │   └── endpoints/      # Rotas específicas
│   │   │       ├── __init__.py
│   │   │       ├── auth.py     # Autenticação
│   │   │       ├── users.py    # Usuários
│   │   │       ├── roles.py    # Papéis
│   │   │       └── permissions.py # Permissões
│   │   │
│   │   └── v2/                 # API v2 (futura expansão)
│   │       ├── __init__.py
│   │       └── ...
│   │
│   ├── core/                   # Configurações essenciais e utilidades
│   │   ├── __init__.py
│   │   ├── config.py           # Configurações da aplicação
│   │   ├── security.py         # Segurança, JWT, hashing
│   │   ├── dependencies.py     # Dependências compartilhadas
│   │   └── exceptions.py       # Handlers de exceções
│   │
│   ├── db/                     # Camada de banco de dados
│   │   ├── __init__.py
│   │   ├── session.py          # Configuração da sessão do SQLAlchemy
│   │   ├── base.py             # Classe base do modelo
│   │   └── init_db.py          # Inicialização do DB
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py             # Modelo de usuário
│   │   ├── role.py             # Modelo de papéis
│   │   └── permission.py       # Modelo de permissões
│   │
│   ├── schemas/                # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── base.py             # Schemas base
│   │   ├── user.py             # Schemas de usuário
│   │   ├── role.py             # Schemas de papéis
│   │   ├── permission.py       # Schemas de permissões
│   │   └── token.py            # Schemas de tokens
│   │
│   ├── crud/                   # Operações CRUD
│   │   ├── __init__.py
│   │   ├── base.py             # CRUD base genérico
│   │   ├── user.py             # CRUD específico para usuários
│   │   ├── role.py             # CRUD para papéis
│   │   └── permission.py       # CRUD para permissões
│   │
│   ├── services/               # Lógica de negócios
│   │   ├── __init__.py
│   │    └── auth.py             # Serviço de autenticação
│   │
│   ├── utils/                  # Utilitários
│   │   ├── __init__.py
│   │   ├── pagination.py       # Utilidades para paginação
│   │   └── ...
│   │
│   ├── tasks/                  # Tarefas assíncronas (opcional)
│   │   ├── __init__.py
│   │   └── worker.py           # Configuração de workers
│   │
│   └── tests/                  # Testes automatizados
│       ├── __init__.py
│       ├── conftest.py         # Fixtures para testes
│       ├── api/                # Testes para API
│       │   ├── v1/             # Testes para v1
│       │   │   ├── test_auth.py
│       │   │   ├── test_users.py
│       │   │   └── ...
│       │   └── ...
│       └── ...
│
│
├── migrations/                 # Scripts de migração manual (se necessário)
│   └── ...
│
├── logs/                       # Logs da aplicação
│   └── ...
│
├── static/                     # Arquivos estáticos (se usados)
│   └── ...
│
├── templates/                  # Templates (se usados)
│   └── ...
│
├── scripts/                    # Scripts úteis
│   ├── lint.py                 # Script para linting
│   └── start.sh                # Script de inicialização
│
├── .env                        # Variáveis de ambiente para desenvolvimento
├── .env.example                # Exemplo de variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo git
├── alembic.ini                 # Configuração do Alembic
├── docker-compose.yml          # Configuração do Docker Compose
├── Dockerfile                  # Configuração do Docker
├── README.md                   # Documentação do projeto
└── pyproject.toml              # Dependências e configuração do projeto
```
