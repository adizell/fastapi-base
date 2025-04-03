### Root Project
```python
fastapi-project/
│
├── alembic/                    # Migrations do banco de dados
│   └── versions/
│       └── README.md
│
├── app/                        # Código principal da aplicação
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada da aplicação
│   ├── core/                   # Configurações essenciais e utilidades
│   │   ├── __init__.py
│   │   ├── config.py           # Configurações da aplicação (env vars, etc)
│   │   ├── security.py         # Segurança, JWT, hashing
│   │   ├── dependencies.py     # Dependências compartilhadas (auth, perms)
│   │   └── exceptions.py       # Handlers de exceções
│   │
│   ├── api/                    # Rotas da API versionadas
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependências específicas da API
│   │   ├── v1/                 # API v1
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Router principal da v1
│   │   │   ├── endpoints/      # Rotas específicas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py     # Autenticação
│   │   │   │   ├── users.py    # Usuários
│   │   │   │   ├── roles.py    # Permissões e Grupos
│   │   │   │   └── ...
│   │   │   └── websockets/     # Rotas websocket
│   │   │       ├── __init__.py
│   │   │       └── notifications.py
│   │   └── v2/                 # API v2 (futura expansão)
│   │       ├── __init__.py
│   │       └── ...
│   │
│   ├── db/                     # Camada de banco de dados
│   │   ├── __init__.py
│   │   ├── session.py          # Configuração da sessão do SQLAlchemy
│   │   ├── base.py             # Classe base do modelo
│   │   └── init_db.py          # Inicialização do DB (admin, etc)
│   │
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py             # Modelo de usuário
│   │   ├── role.py             # Permissões e grupos
│   │   └── ...
│   │
│   ├── schemas/                # Schemas Pydantic (validação, serialização)
│   │   ├── __init__.py
│   │   ├── user.py             # Schemas de usuário
│   │   ├── role.py             # Schemas de permissões
│   │   ├── token.py            # Schemas de tokens
│   │   └── ...
│   │
│   ├── crud/                   # Operações CRUD
│   │   ├── __init__.py
│   │   ├── base.py             # CRUD base genérico
│   │   ├── user.py             # CRUD específico para usuários
│   │   ├── role.py             # CRUD para permissões e grupos
│   │   └── ...
│   │
│   ├── services/               # Lógica de negócios
│   │   ├── __init__.py
│   │   ├── auth.py             # Serviço de autenticação
│   │   └── ...
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
├── migrations/                 # Scripts de migração manual (se necessário)
│   └── ...
│
├── logs/                       # Logs da aplicação
│   └── ...
│
├── scripts/                    # Scripts úteis
│   ├── start.sh
│   ├── test.sh
│   └── ...
│
├── static/                     # Arquivos estáticos (se usados)
│   └── ...
│
├── templates/                  # Templates (se usados)
│   └── ...
│
├── .env                        # Variáveis de ambiente para desenvolvimento
├── .env.example                # Exemplo de variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo git
├── .pre-commit-config.yaml     # Hooks pre-commit
├── alembic.ini                 # Configuração do Alembic
├── docker-compose.yml          # Configuração do Docker Compose
├── Dockerfile                  # Configuração do Docker
├── README.md                   # Documentação do projeto
└── pyproject.toml              # Dependências e configuração do projeto
```