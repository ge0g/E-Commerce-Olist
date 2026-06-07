from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DIR / "olist_analytics.db"

TABLES = {
    "orders_analytical_base": "orders_analytical_base.csv",
    "valid_sales_orders": "valid_sales_orders.csv",
    "products_prepared": "products_prepared.csv",
    "order_items_enriched": "order_items_enriched.csv",
    "order_items_agg": "order_items_agg.csv",
    "payments_agg": "payments_agg.csv",
    "reviews_agg": "reviews_agg.csv",
    "customers_segmented": "customers_segmented.csv",
    "order_categories_base": "order_categories_base.csv",
    "delivery_reviews_base": "delivery_reviews_base.csv",
}


def check_processed_files() -> None:
    missing_files = [
        file_name for file_name in TABLES.values() if not (PROCESSED_DIR / file_name).exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "В папке data/processed отсутствуют файлы:\n"
            + "\n".join(missing_files)
            + f"\n\nПроверяемая папка: {PROCESSED_DIR}"
        )


def recreate_database() -> None:
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()


def load_table(file_name: str) -> pd.DataFrame:
    file_path = PROCESSED_DIR / file_name

    return pd.read_csv(file_path, low_memory=False)


def save_tables_to_sqlite() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        for table_name, file_name in TABLES.items():
            dataframe = load_table(file_name)

            dataframe.to_sql(
                name=table_name,
                con=connection,
                if_exists="replace",
                index=False,
            )

            print(f"{table_name}: {dataframe.shape[0]:,} строк")


def main() -> None:
    print(f"Корневая папка проекта: {PROJECT_ROOT}")
    print(f"Папка с подготовленными данными: {PROCESSED_DIR}")
    print()

    check_processed_files()
    recreate_database()
    save_tables_to_sqlite()

    print()
    print(f"SQLite-база создана: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
