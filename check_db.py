from sqlalchemy import text

from app.database.session import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connection successful:", result.scalar())