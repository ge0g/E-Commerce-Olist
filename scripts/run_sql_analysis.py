from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "olist_analytics.db"
SQL_FILE_PATH = PROJECT_ROOT / "sql" / "analysis_queries.sql"


def split_sql_queries(sql_text: str) -> list[tuple[str, str]]:
    queries = []
    current_title = "SQL-запрос"
    current_query_lines = []

    for line in sql_text.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("--") and stripped_line[2:].strip():
            if current_query_lines:
                query = "\n".join(current_query_lines).strip()

                if query:
                    queries.append((current_title, query))

                current_query_lines = []

            current_title = stripped_line[2:].strip()

        elif stripped_line:
            current_query_lines.append(line)

    if current_query_lines:
        query = "\n".join(current_query_lines).strip()

        if query:
            queries.append((current_title, query))

    return queries


def run_query(query: str) -> pd.DataFrame:
    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(query, connection)


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"База не найдена: {DATABASE_PATH}")

    if not SQL_FILE_PATH.exists():
        raise FileNotFoundError(f"SQL-файл не найден: {SQL_FILE_PATH}")

    sql_text = SQL_FILE_PATH.read_text(encoding="utf-8")
    queries = split_sql_queries(sql_text)

    for query_number, (title, query) in enumerate(queries, start=1):
        print("=" * 80)
        print(f"{query_number}. {title}")
        print("=" * 80)

        result = run_query(query)

        print(result.head(20))
        print()


if __name__ == "__main__":
    main()
