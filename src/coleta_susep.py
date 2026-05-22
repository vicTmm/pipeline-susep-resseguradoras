from __future__ import annotations

import logging
import re

from playwright.sync_api import Page, sync_playwright

from src.tratamento import Table


URL = "https://www2.susep.gov.br/menuatendimento/procura_2011.asp"
TIPOS_RESGURO = {
    "locais": "Resseguradora Local",
    "admitidos": "Resseguradora Admitida",
    "eventuais": "Resseguradora Eventual",
}


def consultar_tipo(page: Page, tipo_texto: str) -> Table:
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(1200)

    selects = page.locator("select")
    if selects.count() == 0:
        raise RuntimeError("Nenhum campo de selecao encontrado na pagina da SUSEP.")

    tipo_select = None
    for index in range(selects.count()):
        select = selects.nth(index)
        option_texts = select.locator("option").all_text_contents()
        if any("Resseguradora" in (text or "") for text in option_texts):
            tipo_select = select
            break

    if tipo_select is None:
        raise RuntimeError("Nao foi possivel identificar o campo de tipo de empresa.")

    tipo_select.select_option(label=tipo_texto)

    estado_select = page.locator("select[name='estado']")
    if estado_select.count() > 0:
        options = estado_select.locator("option").all_text_contents()
        todos_label = next((text for text in options if re.search("todos", text, re.IGNORECASE)), None)
        if todos_label:
            estado_select.select_option(label=todos_label)

    if page.get_by_role("button", name="Procurar").count() > 0:
        page.get_by_role("button", name="Procurar").click()
    else:
        page.locator("input[value='Procurar'], input[type='submit']").first.click()

    page.wait_for_timeout(2500)
    records: Table = []

    for index in range(page.locator("table").count()):
        table = page.locator("table").nth(index)
        if "CNPJ:" not in table.inner_text().strip():
            continue

        cells = [text.strip() for text in table.locator("td").all_inner_texts() if text.strip()]
        strong = table.locator("strong").first
        name = strong.inner_text().strip() if strong.count() > 0 else ""

        record = {
            "tipo": tipo_texto,
            "nome": name,
            "cnpj": "",
            "codigo_fip": "",
            "endereco": "",
            "cidade_uf_cep": "",
            "ddd": "",
            "tel": "",
            "fax": "",
            "site": "",
            "email": "",
            "data_autorizacao_cadastramento": "",
            "entcodigo": "",
            "codativo": "",
        }

        link = table.locator("a[onclick]").first
        if link.count() > 0:
            onclick = link.get_attribute("onclick") or ""
            match = re.search(r"entcodigo=(\d+).*?codativo=([A-Za-z]+)", onclick)
            if match:
                record["entcodigo"] = match.group(1)
                record["codativo"] = match.group(2)

        for line in cells:
            lower_line = line.lower()
            if line.startswith("CNPJ:"):
                record["cnpj"] = line.replace("CNPJ:", "").strip()
            elif lower_line.startswith("codigo fip:"):
                record["codigo_fip"] = re.sub(r"(?i)codigo fip:\s*", "", line).strip()
            elif lower_line.startswith("endereco:"):
                record["endereco"] = re.sub(r"(?i)endereco:\s*", "", line).strip()
            elif re.search(r"cep:", line, re.IGNORECASE):
                record["cidade_uf_cep"] = line.strip()
            elif lower_line.startswith("ddd:"):
                ddd_match = re.search(r"DDD:\s*([0-9]+)", line, re.IGNORECASE)
                tel_match = re.search(r"Tel:\s*([0-9\-()\s]+)", line, re.IGNORECASE)
                fax_match = re.search(r"Fax:\s*([0-9\-()\s]+)", line, re.IGNORECASE)
                record["ddd"] = ddd_match.group(1) if ddd_match else ""
                record["tel"] = tel_match.group(1).strip() if tel_match else ""
                record["fax"] = fax_match.group(1).strip() if fax_match else ""
            elif lower_line.startswith("site:"):
                record["site"] = line.replace("Site:", "").strip()
            elif lower_line.startswith("e-mail:") or lower_line.startswith("email:"):
                record["email"] = re.sub(r"(?i)e-?mail:\s*", "", line).strip()
            elif lower_line.startswith("data autorizacao/cadastramento:"):
                record["data_autorizacao_cadastramento"] = re.sub(
                    r"(?i)data autorizacao/cadastramento:\s*",
                    "",
                    line,
                ).strip()

        if record["cnpj"]:
            records.append(record)

    if not records:
        raise RuntimeError(f"Nenhum registro encontrado para '{tipo_texto}'.")

    return records


def coletar_resseguradoras(headless: bool = True) -> Table:
    all_rows: Table = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            for tipo in TIPOS_RESGURO.values():
                logging.info("Coletando dados da SUSEP para: %s", tipo)
                rows = consultar_tipo(page, tipo)
                logging.info("%s registros coletados para %s", len(rows), tipo)
                all_rows.extend(rows)
        finally:
            browser.close()

    return all_rows
