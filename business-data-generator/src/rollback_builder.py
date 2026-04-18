from .sql_builder import format_sql_value


def build_delete_sql(table_name: str, rows: list[dict], primary_keys: list[str]) -> str:
    statements = []

    for row in rows:
        where_clause = " AND ".join(
            f"{pk} = {format_sql_value(row[pk])}" for pk in primary_keys if pk in row
        )
        sql = f"DELETE FROM {table_name} WHERE {where_clause};"
        statements.append(sql)

    return "\n".join(statements)