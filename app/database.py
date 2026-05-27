from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define onde o arquivo local do banco será guardado
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# O argumento 'check_same_thread' é obrigatório apenas para o SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cada instância de SessionLocal será uma sessão ativa de leitura/escrita no banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base que herdaremos para criar as tabelas (Modelos)
Base = declarative_base()

# Função utilitária (Injeção de Dependência) para gerenciar o abrir/fechar de conexões
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()