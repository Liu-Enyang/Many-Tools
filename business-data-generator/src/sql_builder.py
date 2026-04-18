def format_sql_value(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def build_insert_sql(table_name: str, rows: list[dict]) -> str:
    statements = []

    for row in rows:
        columns = ", ".join(row.keys())
        values = ", ".join(format_sql_value(v) for v in row.values())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
        statements.append(sql)

    return "\n".join(statements)