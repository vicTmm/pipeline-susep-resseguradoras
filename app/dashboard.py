from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HISTORY_DIR = PROJECT_ROOT / "data" / "history"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"


STATUS_LABELS = {
    "novo": "Novos",
    "removido": "Removidos",
    "alterado": "Alterados",
}

THEMES = {
    "Claro": {
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_alt": "#F1F5F9",
        "text": "#0F172A",
        "muted": "#64748B",
        "border": "#E2E8F0",
        "grid": "#F1F5F9",
        "accent": "#2563EB",
        "local": "#4F46E5",
        "admitida": "#10B981",
        "eventual": "#F59E0B",
        "shadow": "rgba(148, 163, 184, 0.15)",
        "gradient_hero": "linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%)",
        "hero_border": "#E2E8F0"
    },
    "Escuro": {
        "background": "#020617",
        "surface": "#0F172A",
        "surface_alt": "#1E293B",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "border": "#1E293B",
        "grid": "#0F172A",
        "accent": "#3B82F6",
        "local": "#818CF8",
        "admitida": "#34D399",
        "eventual": "#FBBF24",
        "shadow": "rgba(0, 0, 0, 0.5)",
        "gradient_hero": "linear-gradient(135deg, #0F172A 0%, #020617 100%)",
        "hero_border": "#1E293B"
    },
}


st.set_page_config(
    page_title="Monitoramento SUSEP",
    layout="wide",
)


def extract_timestamp(path: Path) -> datetime | None:
    match = re.search(r"(\d{8}_\d{6})", path.name)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")


def format_timestamp(value: datetime | None) -> str:
    if value is None:
        return "Data não identificada"
    return value.strftime("%d/%m/%Y %H:%M:%S")


@st.cache_data
def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def list_csv_files(directory: Path, pattern: str) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern), key=lambda item: extract_timestamp(item) or datetime.min)


def latest_file(files: list[Path]) -> Path | None:
    return files[-1] if files else None


def load_latest_history() -> tuple[pd.DataFrame, Path | None]:
    files = list_csv_files(HISTORY_DIR, "susep_resseguradoras_*.csv")
    current = latest_file(files)
    if current is None:
        return pd.DataFrame(), None
    return read_csv(str(current)), current


def load_reports() -> list[Path]:
    return list_csv_files(REPORTS_DIR, "alteracoes_susep_*.csv")


def status_count(df: pd.DataFrame, status: str) -> int:
    if df.empty or "status" not in df.columns:
        return 0
    return int((df["status"] == status).sum())


def inject_theme_css(theme: dict[str, str]) -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            :root {{
                --app-bg: {theme["background"]};
                --app-surface: {theme["surface"]};
                --app-text: {theme["text"]};
                --app-muted: {theme["muted"]};
                --app-border: {theme["border"]};
                --app-accent: {theme["accent"]};
                --app-shadow: {theme.get("shadow", "rgba(0,0,0,0.1)")};
                --app-gradient: {theme.get("gradient_hero", "none")};
                --app-hero-border: {theme.get("hero_border", theme["border"])};
            }}

            .stApp {{
                background-color: var(--app-bg);
                color: var(--app-text);
                font-family: 'Inter', sans-serif;
            }}

            [data-testid="stHeader"] {{
                background: transparent;
            }}

            [data-testid="stMainBlockContainer"] {{
                max-width: 1200px;
                padding-top: 2.5rem;
                padding-bottom: 4rem;
            }}

            h1, h2, h3, h4, p, span, label, div {{
                font-family: 'Inter', sans-serif;
            }}

            /* TOPBAR & HERO */
            .topbar {{
                align-items: center;
                display: flex;
                gap: 24px;
                justify-content: space-between;
                margin-bottom: 2rem;
            }}

            .hero {{
                background: var(--app-gradient);
                border: 1px solid var(--app-hero-border);
                border-radius: 16px;
                flex: 1;
                padding: 32px;
                box-shadow: 0 4px 20px var(--app-shadow);
                position: relative;
                overflow: hidden;
            }}

            .hero::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 4px;
                background: linear-gradient(90deg, {theme["local"]}, {theme["admitida"]}, {theme["eventual"]});
            }}

            .hero-eyebrow {{
                color: var(--app-accent);
                font-size: 0.85rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                margin-bottom: 12px;
                text-transform: uppercase;
            }}

            .hero-title {{
                color: var(--app-text);
                font-size: 2.5rem;
                font-weight: 800;
                letter-spacing: -0.02em;
                line-height: 1.2;
                margin: 0;
            }}

            .hero-copy {{
                color: var(--app-muted);
                font-size: 1.05rem;
                line-height: 1.6;
                margin-top: 12px;
                max-width: 800px;
                font-weight: 400;
            }}

            /* THEME TOGGLE */
            .theme-label {{
                color: var(--app-muted);
                font-size: 0.75rem;
                font-weight: 700;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}

            div[data-testid="stRadio"] {{
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                border-radius: 99px;
                padding: 4px;
                box-shadow: 0 2px 8px var(--app-shadow);
            }}

            div[data-testid="stRadio"] > label {{
                display: none;
            }}
            
            div[data-testid="stRadio"] label {{
                font-size: 0.85rem;
                font-weight: 500;
                padding: 4px 12px;
                border-radius: 99px;
            }}

            /* METRIC CARDS */
            .metric-card {{
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 2px 10px var(--app-shadow);
                transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                min-height: 140px;
            }}

            .metric-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 24px var(--app-shadow);
                border-color: var(--app-accent);
            }}

            .metric-label {{
                color: var(--app-muted);
                font-size: 0.85rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}

            .metric-value {{
                color: var(--app-text);
                font-size: 2.75rem;
                font-weight: 800;
                line-height: 1;
                margin: 12px 0 8px 0;
            }}

            .metric-note {{
                color: var(--app-muted);
                font-size: 0.85rem;
                font-weight: 400;
            }}

            /* META LINE & BADGES */
            .status-container {{
                display: flex;
                gap: 16px;
                margin: 24px 0;
                padding-bottom: 24px;
                border-bottom: 1px solid var(--app-border);
                flex-wrap: wrap;
            }}
            .badge {{
                display: flex;
                align-items: center;
                gap: 8px;
                background: var(--app-surface);
                border: 1px solid var(--app-border);
                padding: 6px 12px;
                border-radius: 99px;
                font-size: 0.85rem;
                color: var(--app-muted);
                box-shadow: 0 2px 4px var(--app-shadow);
            }}
            .badge strong {{
                color: var(--app-text);
                font-weight: 600;
            }}
            .badge-icon {{
                color: var(--app-accent);
                font-size: 1rem;
            }}
            .metric-card.primary {{
                background: var(--app-gradient);
                border-color: var(--app-accent);
                box-shadow: 0 4px 16px var(--app-shadow);
            }}
            .metric-card.primary .metric-value {{
                color: var(--app-accent);
                font-size: 3.5rem;
            }}
            .metric-card.primary .metric-label {{
                color: var(--app-text);
            }}

            .section-title {{
                color: var(--app-text);
                font-size: 1.25rem;
                font-weight: 700;
                margin-bottom: 8px;
                letter-spacing: -0.01em;
            }}

            .section-caption {{
                color: var(--app-muted);
                font-size: 0.95rem;
                margin-bottom: 24px;
                line-height: 1.5;
            }}

            /* COMPONENT TWEAKS */
            div[data-testid="stDataFrame"] {{
                border: 1px solid var(--app-border);
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 12px var(--app-shadow);
            }}

            div[data-testid="stTabs"] button {{
                color: var(--app-muted);
                font-weight: 500;
                font-size: 1rem;
                padding-bottom: 12px;
            }}

            div[data-testid="stTabs"] button[aria-selected="true"] {{
                color: var(--app-accent);
                font-weight: 600;
            }}

            div[data-baseweb="tab-highlight"] {{
                background-color: var(--app-accent);
            }}

            @media (max-width: 780px) {{
                .hero {{ padding: 24px; }}
                .hero-title {{ font-size: 2rem; }}
                .metric-card {{ min-height: auto; padding: 16px; }}
                .metric-value {{ font-size: 2rem; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topbar() -> str:
    left, right = st.columns([5, 1.35])
    with left:
        st.markdown(
            """
            <div class="hero">
                <div class="hero-eyebrow">Monitoramento regulatório</div>
                <h1 class="hero-title">SUSEP Resseguradoras</h1>
                <div class="hero-copy">
                    Acompanhamento automatizado da base pública de resseguradoras,
                    com histórico versionado, comparação diária e evidências de alterações.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="theme-label">Tema</div>
            """,
            unsafe_allow_html=True,
        )
        theme_choice = st.radio(
            "Tema",
            ["Claro", "Escuro"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
        )
    return theme_choice


def render_metric_card(label: str, value: int | str, note: str, primary: bool = False) -> None:
    primary_class = " primary" if primary else ""
    st.markdown(
        f"""
        <div class="metric-card{primary_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_subscription_form() -> None:
    st.sidebar.markdown("### 🔔 Alertas de Atualização")
    st.sidebar.markdown(
        "Receba um e-mail sempre que a Susep alterar o status de alguma resseguradora."
    )
    with st.sidebar.form("email_subscription_form"):
        email = st.text_input("Seu melhor e-mail", placeholder="exemplo@email.com")
        submitted = st.form_submit_button("Assinar Grátis", use_container_width=True)
        if submitted:
            if "@" in email and "." in email:
                data_file = PROJECT_ROOT / "data" / "subscribers.json"
                subscribers = []
                if data_file.exists():
                    try:
                        with open(data_file, "r", encoding="utf-8") as f:
                            subscribers = json.load(f)
                    except json.JSONDecodeError:
                        pass
                
                if email not in subscribers:
                    subscribers.append(email)
                    with open(data_file, "w", encoding="utf-8") as f:
                        json.dump(subscribers, f, indent=4)
                
                st.success("E-mail cadastrado com sucesso!")
                st.balloons()
            else:
                st.error("Por favor, insira um e-mail válido.")


def render_section_header(title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-caption">{caption}</div>
        """,
        unsafe_allow_html=True,
    )


def build_type_distribution(history_df: pd.DataFrame) -> pd.DataFrame:
    by_type = history_df["tipo"].value_counts().rename_axis("Tipo").reset_index(name="Quantidade")
    total = int(by_type["Quantidade"].sum())
    by_type["Percentual"] = (by_type["Quantidade"] / total * 100).round(1)
    by_type["Participação"] = by_type["Percentual"].map(lambda value: f"{value:.1f}%")
    by_type["Rótulo"] = by_type.apply(
        lambda row: f"{row['Quantidade']}   {row['Participação']}",
        axis=1,
    )
    return by_type.sort_values("Quantidade", ascending=True)


def type_color_scale(theme: dict[str, str]) -> alt.Scale:
    return alt.Scale(
        domain=["Resseguradora Local", "Resseguradora Admitida", "Resseguradora Eventual"],
        range=[theme["local"], theme["admitida"], theme["eventual"]],
    )


def render_type_distribution(history_df: pd.DataFrame, theme: dict[str, str]) -> None:
    by_type = build_type_distribution(history_df)
    max_quantity = int(by_type["Quantidade"].max()) if not by_type.empty else 1
    domain_max = max_quantity + max(1, round(max_quantity * 0.25))

    bars = (
        alt.Chart(by_type)
        .mark_bar(cornerRadius=6, height=22)
        .encode(
            x=alt.X(
                "Quantidade:Q",
                title=None,
                scale=alt.Scale(domain=[0, domain_max]),
                axis=alt.Axis(
                    domain=False,
                    grid=True,
                    gridColor=theme["grid"],
                    labelColor=theme["muted"],
                    tickColor=theme["border"],
                    tickMinStep=1,
                ),
            ),
            y=alt.Y(
                "Tipo:N",
                title=None,
                sort=alt.SortField(field="Quantidade", order="descending"),
                axis=alt.Axis(
                    domain=False,
                    labelColor=theme["text"],
                    labelFontSize=13,
                    labelLimit=240,
                    ticks=False,
                ),
            ),
            color=alt.Color("Tipo:N", scale=type_color_scale(theme), legend=None),
            tooltip=[
                alt.Tooltip("Tipo:N", title="Tipo"),
                alt.Tooltip("Quantidade:Q", title="Quantidade"),
                alt.Tooltip("Participação:N", title="Participação"),
            ],
        )
    )

    labels = (
        alt.Chart(by_type)
        .mark_text(align="left", baseline="middle", dx=10, color=theme["muted"], fontSize=12)
        .encode(
            x="Quantidade:Q",
            y=alt.Y("Tipo:N", sort=alt.SortField(field="Quantidade", order="descending")),
            text="Rótulo:N",
        )
    )

    chart = (
        alt.layer(bars, labels)
        .properties(height=230, background=theme["surface"])
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, use_container_width=True)

    table_df = by_type.sort_values("Quantidade", ascending=False)[
        ["Tipo", "Quantidade", "Participação"]
    ]
    st.dataframe(table_df, use_container_width=True, hide_index=True)


def render_empty_state() -> None:
    st.info(
        "Ainda não há histórico versionado para exibição. "
        "Execute o pipeline localmente ou pelo GitHub Actions para gerar os primeiros arquivos."
    )


def main() -> None:
    theme_choice = render_topbar()
    theme = THEMES[theme_choice]
    inject_theme_css(theme)

    render_subscription_form()

    history_df, history_file = load_latest_history()
    report_files = load_reports()

    if history_df.empty and not report_files:
        render_empty_state()
        return

    latest_report = latest_file(report_files)
    latest_report_df = read_csv(str(latest_report)) if latest_report else pd.DataFrame()
    latest_history_date = extract_timestamp(history_file) if history_file else None
    latest_report_date = extract_timestamp(latest_report) if latest_report else None

    total_monitorado = len(history_df)
    novos = status_count(latest_report_df, "novo")
    removidos = status_count(latest_report_df, "removido")
    alterados = status_count(latest_report_df, "alterado")

    col_main, col_stats = st.columns([1.5, 2.5], gap="large")
    with col_main:
        render_metric_card("Total Monitorados", total_monitorado, "Registros ativos na base atual", primary=True)
    
    with col_stats:
        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric_card("Novos", novos, "Último relatório")
        with c2:
            render_metric_card("Removidos", removidos, "Último relatório")
        with c3:
            render_metric_card("Alterados", alterados, "Último relatório")

    hist_str = history_file.name if history_file else "-"
    rep_str = format_timestamp(latest_report_date or latest_history_date)
    st.markdown(
        f"""
        <div class="status-container">
            <div class="badge">
                <span class="badge-icon">🗃️</span> Último snapshot: <strong>{hist_str}</strong>
            </div>
            <div class="badge">
                <span class="badge-icon">⏱️</span> Última execução: <strong>{rep_str}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_resumo, tab_alteracoes, tab_historico = st.tabs(["Resumo", "Alterações", "Histórico"])

    with tab_resumo:
        render_section_header(
            "Distribuição da base atual",
            "Composição da base monitorada por tipo de resseguradora.",
        )
        if "tipo" in history_df.columns and not history_df.empty:
            render_type_distribution(history_df, theme)
        else:
            st.info("A base histórica ainda não possui dados para sumarização.")

    with tab_alteracoes:
        render_section_header(
            "Relatórios de alterações",
            "Consulta por execução, com filtro por status e download do CSV.",
        )
        if not report_files:
            st.info("Nenhum relatório de alterações foi encontrado.")
        else:
            options = {
                f"{format_timestamp(extract_timestamp(path))} - {path.name}": path
                for path in reversed(report_files)
            }
            selected_label = st.selectbox("Execução", list(options.keys()))
            selected_report = options[selected_label]
            report_df = read_csv(str(selected_report))

            status_options = ["Todos", *STATUS_LABELS.values()]
            selected_status = st.segmented_control("Status", status_options, default="Todos")
            visible_df = report_df.copy()
            if selected_status != "Todos" and "status" in visible_df.columns:
                reverse_labels = {value: key for key, value in STATUS_LABELS.items()}
                visible_df = visible_df[visible_df["status"] == reverse_labels[selected_status]]

            st.dataframe(visible_df, use_container_width=True, hide_index=True)
            st.download_button(
                "Baixar relatório CSV",
                data=selected_report.read_bytes(),
                file_name=selected_report.name,
                mime="text/csv",
            )

    with tab_historico:
        render_section_header(
            "Snapshots históricos",
            "Arquivos versionados usados para rastrear a evolução da base.",
        )
        history_files = list_csv_files(HISTORY_DIR, "susep_resseguradoras_*.csv")
        history_summary = pd.DataFrame(
            [
                {
                    "Data": format_timestamp(extract_timestamp(path)),
                    "Arquivo": path.name,
                    "Registros": len(read_csv(str(path))),
                }
                for path in reversed(history_files)
            ]
        )
        st.dataframe(history_summary, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
