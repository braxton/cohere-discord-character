import logging
import os

import dataset
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

log = logging.getLogger(__name__)


class Database:

    def __init__(self) -> None:
        host = os.environ.get("DB_HOST")
        database = os.environ.get("DB_DATABASE")
        user = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASSWORD")

        if not all([host, database, user, password]):
            log.error("One or more database connection variables are missing, exiting...")
            raise SystemExit

        self.url = f"mysql://{user}:{password}@{host}/{database}?charset=utf8mb4"

    def get(self) -> dataset.Database:
        """
        Returns the dataset database object.
        """
        return dataset.connect(url=self.url)

    def setup(self) -> None:
        """
        Sets up the tables needed for Chiya.
        """
        engine = create_engine(self.url)
        if not database_exists(engine.url):
            create_database(engine.url)

        db = self.get()

        if "settings" not in db:
            settings: dataset.Table | None = db.create_table("settings")
            assert settings is not None

            settings.create_column("guild_id", db.types.bigint, unique=True, nullable=False)
            settings.create_column("char_name", db.types.text)
            settings.create_column("char_desc", db.types.text)
            log.info("Created missing table: settings")

        for table in db.tables:
            db.query(f"ALTER TABLE {table} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            log.info(f"Converted table to utf8mb4_unicode_ci: {table}")

        db.commit()
        db.close()