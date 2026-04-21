from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.clone_generator import _load_base_yaml, _max_plus_one, _get_column_info
from src.dictionary_loader import (
    find_dictionary_csv,
    load_field_dictionary_mapping,
    load_pcc_hanyou_dictionary,
    open_csv_with_fallback,
)
from src.sql_builder import build_insert_sql
from src.rollback_builder import build_delete_sql

import csv as csv_module

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


@st.cache_data
def load_table_csv(table_name: str) -> pd.DataFrame:
    csv_path = find_dictionary_csv(DATA_DIR, table_name)
    if not csv_path:
        return pd.DataFrame()
    f, enc = open_csv_with_fallback(csv_path)
    with f:
        rows = list(csv_module.DictReader(f))
    return pd.DataFrame(rows)


@st.cache_data
def load_hanyou_dict() -> tuple[dict, dict]:
    field_mapping = load_field_dictionary_mapping(CONFIG_DIR)
    dictionaries = load_pcc_hanyou_dictionary(DATA_DIR, CONFIG_DIR)
    return field_mapping, dictionaries


def available_tables() -> list[str]:
    names = []
    for f in sorted(DATA_DIR.glob("*.csv")):
        stem = f.stem
        if stem.startswith("dbo."):
            stem = stem[4:]
        if stem.upper() != "PCC_HANYOU":
            names.append(stem)
    return names


def main():
    st.set_page_config(page_title="Clone Tool", layout="wide")
    st.title("Clone Tool - 単体テストデータ生成")

    # --- サイドバー: テーブル選択 ---
    tables = available_tables()
    table_name = st.sidebar.selectbox("テーブル選択", tables)

    df = load_table_csv(table_name)
    if df.empty:
        st.error(f"CSV not found for: {table_name}")
        return

    base_yaml = _load_base_yaml(CONFIG_DIR, table_name)
    primary_keys: list[str] = base_yaml.get("primary_key", [])

    # --- 検索フィルター ---
    st.subheader(f"{table_name}  ({len(df)} rows)")
    col1, col2 = st.columns([2, 3])
    with col1:
        search_col = st.selectbox("検索カラム", df.columns.tolist(), key="search_col")
    with col2:
        search_val = st.text_input("検索値（部分一致）", key="search_val")

    filtered = df
    if search_val:
        filtered = df[df[search_col].astype(str).str.contains(search_val, case=False, na=False)]

    st.caption(f"{len(filtered)} / {len(df)} rows")

    # --- 行選択 ---
    if filtered.empty:
        st.warning("No matching rows.")
        return

    # Show index + PK columns for selection
    display_cols = list(dict.fromkeys(primary_keys + df.columns.tolist()[:6]))
    display_cols = [c for c in display_cols if c in df.columns]

    selected_idx = st.selectbox(
        "行を選択（クローン元）",
        options=filtered.index.tolist(),
        format_func=lambda i: "  |  ".join(
            f"{c}={filtered.loc[i, c]}" for c in display_cols if c in filtered.columns
        ),
    )
    source_row: dict[str, str] = filtered.loc[selected_idx].to_dict()

    st.divider()

    # --- PK: max+1 ---
    st.subheader("主キー（自動: max+1）")
    new_pks: dict[str, str] = {}
    for pk in primary_keys:
        all_vals = df[pk].tolist() if pk in df.columns else []
        col_info = _get_column_info(base_yaml, pk)
        new_val = _max_plus_one(all_vals, col_info.get("type", ""), col_info.get("length"))
        c1, c2 = st.columns(2)
        c1.text_input(f"{pk}（元値）", value=source_row.get(pk, ""), disabled=True)
        new_pks[pk] = c2.text_input(f"{pk}（新値）", value=new_val, key=f"pk_{pk}")

    st.divider()

    # --- 区分フィールド ---
    try:
        field_mapping, dictionaries = load_hanyou_dict()
    except Exception as e:
        st.warning(f"区分辞書の読み込み失敗: {e}")
        field_mapping, dictionaries = {}, {}

    kubun_fields = [f for f in source_row if f in field_mapping]
    kubun_overrides: dict[str, str] = {}

    if kubun_fields:
        st.subheader("区分フィールド（PCC_hanyou）")
        for field in kubun_fields:
            mapping = field_mapping[field]
            code_key = mapping.get("code_key", "")
            description = mapping.get("description", field)
            current = source_row.get(field, "").strip()
            options = list(dictionaries.get(code_key, {}).items())

            if not options:
                st.text_input(f"{field}  [{description}]", value=current, disabled=True)
                continue

            stored_values = [meta.get("unique_key", code) for code, meta in options]
            labels = [
                f"{meta.get('label', code)}  ({meta.get('unique_key', code)})"
                for code, meta in options
            ]

            default_idx = stored_values.index(current) if current in stored_values else 0

            chosen_label = st.selectbox(
                f"{field}  [{description}]",
                options=labels,
                index=default_idx,
                key=f"kubun_{field}",
            )
            chosen_idx = labels.index(chosen_label)
            kubun_overrides[field] = stored_values[chosen_idx]

    st.divider()

    # --- SQL生成 ---
    if st.button("SQL 生成", type="primary"):
        new_row = dict(source_row)
        new_row.update(new_pks)
        new_row.update(kubun_overrides)
        final_row = {k: (None if v == "" else v) for k, v in new_row.items()}

        insert_sql = build_insert_sql(table_name, [final_row])
        delete_sql = build_delete_sql(table_name, [final_row], primary_keys)

        out_insert = OUTPUT_DIR / f"clone_{table_name}.sql"
        out_rollback = OUTPUT_DIR / f"rollback_clone_{table_name}.sql"
        out_insert.write_text(insert_sql, encoding="utf-8")
        out_rollback.write_text(delete_sql, encoding="utf-8")

        st.success(f"保存: {out_insert.name}  /  {out_rollback.name}")

        st.subheader("INSERT SQL")
        st.code(insert_sql, language="sql")

        st.subheader("DELETE SQL (rollback)")
        st.code(delete_sql, language="sql")


if __name__ == "__main__":
    main()
