from __future__ import annotations

from pathlib import Path
import re
import sqlite3

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "olist_analytics.db"
SQL_FILE_PATH = PROJECT_ROOT / "sql" / "analysis_queries.sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
SQL_RESULTS_PATH = REPORTS_DIR / "sql_results.md"


def clean_title(title: str) -> str:
    return re.sub(r"^\d+\.\s*", "", title).strip()


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
                    queries.append((clean_title(current_title), query))

                current_query_lines = []

            current_title = stripped_line[2:].strip()

        elif stripped_line:
            current_query_lines.append(line)

    if current_query_lines:
        query = "\n".join(current_query_lines).strip()

        if query:
            queries.append((clean_title(current_title), query))

    return queries


def run_query(query: str) -> pd.DataFrame:
    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(query, connection)


def format_value(value) -> str:
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        return f"{value:,.2f}"

    return str(value)


def dataframe_to_markdown(dataframe: pd.DataFrame, max_rows: int = 10) -> str:
    if dataframe.empty:
        return "_Запрос не вернул строк._"

    preview = dataframe.head(max_rows)
    columns = [str(column) for column in preview.columns]

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    rows = [
        "| " + " | ".join(format_value(value) for value in row) + " |" for row in preview.to_numpy()
    ]

    return "\n".join([header, separator, *rows])


def build_report_section(query_number: int, title: str, result: pd.DataFrame) -> str:
    rows_note = "Показаны первые 10 строк результата."

    return f"## {query_number}. {title}\n\n" f"{rows_note}\n\n" f"{dataframe_to_markdown(result)}\n"


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"База не найдена: {DATABASE_PATH}")

    if not SQL_FILE_PATH.exists():
        raise FileNotFoundError(f"SQL-файл не найден: {SQL_FILE_PATH}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    sql_text = SQL_FILE_PATH.read_text(encoding="utf-8")
    queries = split_sql_queries(sql_text)

    report_sections = [
        "# SQL-проверка ключевых метрик",
        (
            "Файл содержит результаты SQL-запросов из `sql/analysis_queries.sql`.\n\n"
            "SQL используется как независимый проверочный слой для ключевых метрик проекта. "
            "Запросы выполняются по подготовленной SQLite-базе за тот же период, что и основной "
            "бизнес-анализ: **2017-01 — 2018-07**."
        ),
    ]

    for query_number, (title, query) in enumerate(queries, start=1):
        result = run_query(query)

        print("=" * 80)
        print(f"{query_number}. {title}")
        print("=" * 80)
        print(result.head(10))
        print()

        report_sections.append(build_report_section(query_number, title, result))

    SQL_RESULTS_PATH.write_text("\n\n---\n\n".join(report_sections), encoding="utf-8")

    print(f"SQL-результаты сохранены: {SQL_RESULTS_PATH}")


if __name__ == "__main__":
    main()
