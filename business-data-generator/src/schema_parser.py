import re


def _extract_primary_key(sql_text: str) -> list[str]:
    """PRIMARY KEY ブロックから主キー列を抽出する。"""
    pk_start = re.search(r"PRIMARY\s+KEY", sql_text, re.IGNORECASE)
    if not pk_start:
        return []

    tail = sql_text[pk_start.start():]

    # PRIMARY KEY の後ろにある最初の "(" を探す
    first_paren = tail.find("(")
    if first_paren == -1:
        return []

    # 対応する ")" を探す
    depth = 0
    end_index = -1
    for i, ch in enumerate(tail[first_paren:], start=first_paren):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end_index = i
                break

    if end_index == -1:
        return []

    pk_block = tail[first_paren:end_index + 1]
    pk_fields = re.findall(r"\[(.*?)\]", pk_block)
    return pk_fields



def parse_ddl(sql_text: str) -> dict:
    result = {
        "table_name": None,
        "columns": [],
        "primary_key": []
    }

    # 表名
    table_match = re.search(
        r"CREATE\s+TABLE\s+\[.*?\]\.\[(.*?)\]",
        sql_text,
        re.IGNORECASE,
    )
    if not table_match:
        table_match = re.search(
            r"CREATE\s+TABLE\s+\[(.*?)\]",
            sql_text,
            re.IGNORECASE,
        )
    if table_match:
        result["table_name"] = table_match.group(1)

    # 字段定义
    column_pattern = re.compile(
        r"^\s*\[(?P<name>[^\]]+)\]\s+\[(?P<type>\w+)\](?:\((?P<length>[^\)]*)\))?\s+(?P<nullable>NOT\s+NULL|NULL)",
        re.IGNORECASE | re.MULTILINE,
    )

    for match in column_pattern.finditer(sql_text):
        raw_length = match.group("length")
        length = raw_length.strip() if raw_length else None

        result["columns"].append({
            "name": match.group("name"),
            "type": match.group("type").lower(),
            "length": length,
            "nullable": match.group("nullable").upper().replace(" ", "") != "NOTNULL"
        })

    # 主键
    result["primary_key"] = _extract_primary_key(sql_text)

    return result