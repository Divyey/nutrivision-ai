from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from core.config import settings

# Neon pooler (PgBouncer) is safer with NullPool: SQLAlchemy does not
# hold connections across requests.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    poolclass=NullPool,
)
