from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.exc import OperationalError

# URL de base de données par défaut
DEFAULT_DATABASE_URL = "postgresql://admin:admin@localhost:5434/bdd_equide"

# URL de base de données fournie par la variable d'environnement
ENV_DATABASE_URL = os.getenv("DATABASE_URL")

# Fonction pour créer un engine et une session
def create_session(database_url):
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

# Essayer de se connecter avec l'URL de base de données par défaut
try:
    engine, SessionLocal = create_session(DEFAULT_DATABASE_URL)
    # Tester la connexion
    with engine.connect() as conn:
        print(f"Connected to the database at {DEFAULT_DATABASE_URL}")
except OperationalError:
    print(f"Failed to connect to the database at {DEFAULT_DATABASE_URL}")
    if ENV_DATABASE_URL:
        # Essayer de se connecter avec l'URL de base de données de l'environnement
        try:
            engine, SessionLocal = create_session(ENV_DATABASE_URL)
            # Tester la connexion
            with engine.connect() as conn:
                print(f"Connected to the database at {ENV_DATABASE_URL}")
        except OperationalError:
            print(f"Failed to connect to the database at {ENV_DATABASE_URL}")
            raise Exception("Failed to connect to the database using both the default and environment URLs.")
    else:
        raise Exception("Environment variable DATABASE_URL is not set and failed to connect using the default URL.")

Base = declarative_base()
