from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from src.tratamento import FIELDNAMES, Row, Table


SOURCE_URL = "https://www2.susep.gov.br/menuatendimento/procura_2011.asp"
REPORT_HIDDEN_COLUMNS = {"chave_monitoramento", "fax", "endereco"}
CHANGE_COLUMNS = [
    "status",
    "campos_alterados",
    *[field for field in FIELDNAMES if field not in REPORT_HIDDEN_COLUMNS],
]


def rows_equal(old_row: Row, new_row: Row) -> bool:
    """Compara dois registros padronizados campo a campo."""
    keys = sorted(set(old_row) | set(new_row))
    return all(old_row.get(key, "") == new_row.get(key, "") for key in keys)


def summarize_changes(old_row: Row, new_row: Row) -> str:
    """Descreve quais campos mudaram para facilitar revisao operacional."""
    changes = []
    ignored = {"chave_monitoramento"}

    for key in sorted((set(old_row) | set(new_row)) - ignored):
        old_value = old_row.get(key, "")
        new_value = new_row.get(key, "")
        if old_value != new_value:
            changes.append(f"{key}: {old_value or '-'} -> {new_value or '-'}")

    return " | ".join(changes)


def compare_tables(old_rows: Table, new_rows: Table) -> dict[str, Table]:
    """Classifica diferencas entre a ultima base historica e a base atual."""
    old_by_key = {row["chave_monitoramento"]: row for row in old_rows}
    new_by_key = {row["chave_monitoramento"]: row for row in new_rows}

    old_keys = set(old_by_key)
    new_keys = set(new_by_key)

    added = [new_by_key[key] for key in sorted(new_keys - old_keys)]
    removed = [old_by_key[key] for key in sorted(old_keys - new_keys)]

    changed = []
    for key in sorted(old_keys & new_keys):
        old_row = old_by_key[key]
        new_row = new_by_key[key]
        if not rows_equal(old_row, new_row):
            changed_row = new_row.copy()
            changed_row["campos_alterados"] = summarize_changes(old_row, new_row)
            changed.append(changed_row)

    return {"added": added, "removed": removed, "changed": changed}


def has_changes(diff_result: dict[str, Table]) -> bool:
    return any(diff_result[group] for group in ["added", "removed", "changed"])


def count_by_tipo(rows: Table) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        tipo = row.get("tipo", "nao_identificado") or "nao_identificado"
        counts[tipo] = counts.get(tipo, 0) + 1
    return counts


def write_changes_csv(path: Path, diff_result: dict[str, Table]) -> None:
    """Gera uma base tabular de evidencias para auditoria e analise."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: Table = []

    for status, group in [
        ("novo", diff_result["added"]),
        ("removido", diff_result["removed"]),
        ("alterado", diff_result["changed"]),
    ]:
        for row in group:
            report_row = {column: row.get(column, "") for column in CHANGE_COLUMNS}
            report_row["status"] = status
            rows.append(report_row)

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CHANGE_COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_report(
    path: Path,
    diff_result: dict[str, Table],
    history_file: Path,
    current_file: Path,
) -> None:
    """Gera um resumo executivo da execucao do monitoramento."""
    path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    total_changes = len(diff_result["added"]) + len(diff_result["removed"]) + len(diff_result["changed"])

    lines = [
        "# Monitoramento SUSEP - Resseguradoras",
        "",
        f"Gerado em: {generated_at}",
        f"Fonte regulatoria: {SOURCE_URL}",
        f"Base historica comparada: `{history_file.name}`",
        f"Base atual: `{current_file.name}`",
        "",
        "## Resumo executivo",
        "",
        f"- Total de alteracoes relevantes: {total_changes}",
        f"- Novos registros: {len(diff_result['added'])}",
        f"- Registros removidos: {len(diff_result['removed'])}",
        f"- Registros alterados: {len(diff_result['changed'])}",
        "- Evidencia gerada: relatorio CSV detalhado e snapshot historico da base atual",
        "",
    ]

    for label, key in [
        ("Novos registros", "added"),
        ("Registros removidos", "removed"),
        ("Registros alterados", "changed"),
    ]:
        lines.extend([f"## {label}", ""])
        counts = count_by_tipo(diff_result[key])
        if not counts:
            lines.extend(["Nenhum registro.", ""])
            continue

        for tipo, count in sorted(counts.items()):
            lines.append(f"- {tipo}: {count}")
        lines.append("")

    if diff_result["changed"]:
        lines.extend(["## Campos alterados", ""])
        for row in diff_result["changed"]:
            name = row.get("nome") or row.get("cnpj") or row["chave_monitoramento"]
            lines.append(f"- {row.get('tipo', '-')}: {name} - {row.get('campos_alterados', '')}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
