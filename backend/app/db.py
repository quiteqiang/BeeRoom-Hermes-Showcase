from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_database_url: str | None = None


def init_db(database_url: str) -> None:
    global _engine, _session_factory, _database_url

    if _engine is not None:
        _engine.dispose()

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    from app import models  # noqa: F401  # ensure models are registered before create_all

    existing_tables = set(inspect(engine).get_table_names())
    legacy_tables = existing_tables - {"student", "comment", "sqlite_sequence"}
    if legacy_tables:
        engine.dispose()
        _engine = None
        _session_factory = None
        _database_url = None
        names = ", ".join(sorted(legacy_tables))
        raise RuntimeError(f"legacy database schema detected ({names}); migrate to a new database first")

    Base.metadata.create_all(engine)
    _engine = engine
    _session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    _database_url = database_url


def get_session() -> Session:
    if _session_factory is None:
        raise RuntimeError("database is not initialized; call init_db first")
    return _session_factory()
