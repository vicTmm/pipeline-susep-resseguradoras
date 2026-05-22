from __future__ import annotations

import logging
import shutil

from src.coleta_susep import coletar_resseguradoras
from src.comparacao import compare_tables, has_changes, write_changes_csv, write_markdown_report
from src.tratamento import normalize_rows, read_csv, write_csv, write_raw_csv
from src.utils import (
    HISTORY_DIR,
    PROCESSED_DIR,
    RAW_DIR,
    REPORTS_DIR,
    configure_logging,
    ensure_project_dirs,
    execution_timestamp,
    latest_history_file,
)


def main() -> None:
    ensure_project_dirs()
    log_file = configure_logging()
    timestamp = execution_timestamp()

    logging.info("Iniciando pipeline de monitoramento regulatório SUSEP.")
    logging.info("Log da execução: %s", log_file)

    current_raw_file = RAW_DIR / f"susep_resseguradoras_raw_{timestamp}.csv"
    current_processed_file = PROCESSED_DIR / "susep_resseguradoras_atual.csv"
    history_output_file = HISTORY_DIR / f"susep_resseguradoras_{timestamp}.csv"

    raw_rows = coletar_resseguradoras(headless=True)
    rows = normalize_rows(raw_rows)
    write_raw_csv(current_raw_file, raw_rows)
    write_csv(current_processed_file, rows)
    logging.info("%s registros coletados, padronizados e preparados para comparação.", len(rows))
    logging.info("Base atual salva em: %s", current_processed_file)

    previous_history_file = latest_history_file()
    if previous_history_file is None:
        shutil.copyfile(current_processed_file, history_output_file)
        logging.info("Nenhuma base histórica encontrada. Baseline de rastreabilidade criado em: %s", history_output_file)
        logging.info("Monitoramento finalizado. A próxima execução fará a primeira comparação histórica.")
        return

    previous_rows = read_csv(previous_history_file)
    diff_result = compare_tables(previous_rows, rows)

    shutil.copyfile(current_processed_file, history_output_file)
    logging.info("Snapshot histórico da execução salvo em: %s", history_output_file)

    report_csv = REPORTS_DIR / f"alteracoes_susep_{timestamp}.csv"
    report_md = REPORTS_DIR / f"alteracoes_susep_{timestamp}.md"
    write_changes_csv(report_csv, diff_result)
    write_markdown_report(report_md, diff_result, previous_history_file, current_processed_file)

    if not has_changes(diff_result):
        logging.info("Nenhuma alteração regulatória detectada em relação a %s.", previous_history_file.name)
        logging.info("Relatório CSV salvo em: %s", report_csv)
        logging.info("Relatório Markdown salvo em: %s", report_md)
        return

    logging.info(
        "Alterações regulatórias detectadas: %s novos, %s removidos, %s alterados.",
        len(diff_result["added"]),
        len(diff_result["removed"]),
        len(diff_result["changed"]),
    )
    logging.info("Relatório CSV salvo em: %s", report_csv)
    logging.info("Relatório Markdown salvo em: %s", report_md)
    logging.info("Monitoramento finalizado.")


if __name__ == "__main__":
    main()
