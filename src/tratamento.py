from __future__ import annotations

import csv
import unicodedata
from pathlib import Path


Row = dict[str, str]
Table = list[Row]


FIELDNAMES = [
    "chave_monitoramento",
    "tipo",
    "nome",
    "cnpj",
    "codigo_fip",
    "endereco",
    "cidade_uf_cep",
    "ddd",
    "tel",
    "fax",
    "site",
    "email",
    "data_autorizacao_cadastramento",
    "entcodigo",
    "codativo",
]


def slugify_column(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_value.strip().lower().replace(" ", "_").replace("-", "_")


def clean_value(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else " ".join(text.split())


def build_monitoring_key(row: Row) -> str:
    """Cria uma chave estável para comparar a mesma entidade entre execuções."""
    identifier = row.get("entcodigo") or row.get("cnpj") or row.get("nome")
    return f"{row.get('tipo', '').lower()}::{identifier.lower()}"


def normalize_rows(rows: Table) -> Table:
    """Padroniza a base coletada para reduzir ruído na comparação histórica."""
    normalized: Table = []

    for row in rows:
        clean_row = {slugify_column(key): clean_value(value) for key, value in row.items()}
        full_row = {field: clean_row.get(field, "") for field in FIELDNAMES if field != "chave_monitoramento"}
        full_row["chave_monitoramento"] = build_monitoring_key(full_row)
        normalized.append(full_row)

    return sorted(normalized, key=lambda item: item["chave_monitoramento"])


def read_csv(path: Path) -> Table:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return normalize_rows(list(csv.DictReader(file)))


def write_raw_csv(path: Path, rows: Table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def write_csv(path: Path, rows: Table) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
