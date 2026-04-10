import sqlite3
from pathlib import Path



def get_connection(db_path: str) -> sqlite3.Connection:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn



def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            source_url TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE,
            published_at TEXT NOT NULL,
            collected_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    conn.commit()
