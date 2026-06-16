from backend.database.db import engine, DB_PATH
from backend.models.transaction import Base


def init_db():
    Base.metadata.create_all(bind=engine)
    return DB_PATH


if __name__ == "__main__":
    path = init_db()
    print(f"Database initialized at: {path}")
