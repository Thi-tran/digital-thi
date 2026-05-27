"""
Converts database.csv to a SQL file with INSERT statements for chat_history table.
Usage: python csv_to_sql.py
Output: database_insert.sql
"""
import csv
import os

INPUT_FILE = os.path.join(os.path.dirname(__file__), "database.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "database_insert.sql")


def escape(value: str) -> str:
    """Escape single quotes for SQL string literals."""
    return value.replace("'", "''")


def format_embedding(value: str) -> str:
    """
    Embedding is stored as a Python/JSON list string e.g. [-0.017, 0.095, ...]
    Convert to PostgreSQL vector literal: '[−0.017,0.095,...]'
    """
    value = value.strip()
    if not value or value.lower() == "null":
        return "NULL"
    # Already looks like a list — wrap in single quotes for pgvector
    return f"'{value}'"


def format_value(value: str, col: str) -> str:
    if not value or value.strip().lower() == "null":
        return "NULL"
    if col == "user_embedding":
        return format_embedding(value)
    if col == "id":
        return value.strip()
    # Timestamp — no quotes needed if it's a valid ISO format, but safer with quotes
    if col == "created_at":
        return f"'{escape(value.strip())}'"
    return f"'{escape(value)}'"


def main():
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("No rows found in CSV.")
        return

    lines = [
        "-- Generated INSERT statements for chat_history",
        "-- Run against your target database\n",
        "BEGIN;\n",
    ]

    for row in rows:
        session_id   = format_value(row["session_id"],    "session_id")
        user_message = format_value(row["user_message"],  "user_message")
        bot_response = format_value(row["bot_response"],  "bot_response")
        embedding    = format_value(row["user_embedding"], "user_embedding")
        created_at   = format_value(row["created_at"],    "created_at")

        sql = (
            f"INSERT INTO chat_history (session_id, user_message, bot_response, user_embedding, created_at) "
            f"VALUES ({session_id}, {user_message}, {bot_response}, {embedding}, {created_at});"
        )
        lines.append(sql)

    lines.append("\nCOMMIT;")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Written {len(rows)} INSERT statements to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
