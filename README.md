shortlinks-app/
├── app/
│   ├── __init__.py
│   ├── main.py           # Entry point of the application
│   ├── config.py         # App configuration (env variables)
│   ├── db.py             # PostgreSQL connection setup (using asyncpg)
│   ├── auth/             
│   │   ├── models.py     # Pydantic models for auth (UserCreate, UserResponse)
│   │   ├── queries.py    # Python functions to execute queries
│   │   ├── routes.py     # FastAPI routes for user-related operations
│   │   ├── sql/          # Folder for raw SQL queries
│   │   │   ├── create_user.sql
│   │   │   ├── get_user_by_email.sql
│   ├── links/
│   │   ├── models.py     # Pydantic models for short links (LinkCreate, LinkResponse)
│   │   ├── queries.py    # Python functions to execute queries
│   │   ├── routes.py     # FastAPI routes for managing links
│   │   ├── sql/          # Folder for raw SQL queries
│   │   │   ├── insert_link.sql
│   │   │   ├── get_link_by_short_code.sql
├── Dockerfile            # Docker image build instructions
├── docker-compose.yml    # Compose file for FastAPI, Postgres, Redis
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
