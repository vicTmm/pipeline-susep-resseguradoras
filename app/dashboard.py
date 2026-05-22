from __future__ import annotations

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
        "background": "#f7f8fa",
        "surface": "#ffffff",
        "surface_alt": "#f1f4f8",
        "text": "#16181d",
        "muted": "#667085",
        "border": "#e4e7ec",
        "grid": "#edf0f4",
        "accent": "#2563eb",
        "local": "#2563eb",
        "admitida": "#059669",
        "eventual": "#d97706",
    },
    "Escuro": {
        "background": "#0b0f17",
        "surface": "#111827",
        "surface_alt": "#172033",
        "text": "#f3f4f6",
        "muted": "#9ca3af",
        "border": "#243044",
        "grid": "#1f2937",
        "accent": "#60a5fa",
        "local": "#60a5fa",
        "admitida": "#34d399",
        "eventual": "#fbbf24",
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
            :root {{
                --app-bg: {theme["background"]};
                --app-surface: {theme["surface"]};
                --app-text: {theme["text"]};
                --app-muted: {theme["muted"]};
                --app-border: {theme["border"]};
                --app-accent: {theme["accent"]};
            }}

            .stApp {{
                background: var(--app-bg);
                color: var(--app-text);
            }}

            [data-testid="stHeader"] {{
                background: transparent;
            }}

            [data-testid="stMainBlockContainer"] {{
                max-width: 1180px;
                padding-top: 2rem;
            }}

            h1, h2, h3, p, span, label {{
                color: var(--app-text);
            }}

            .topbar {{
                align-items: start;
                display: flex;
                gap: 24px;
                justify-content: space-between;
                margin-bottom: 18px;
            }}

            .hero {{
                border: 1px solid var(--app-border);
                background: var(--app-surface);
                border-radius: 12px;
                flex: 1;
                padding: 22px 24px;
            }}

            .hero-eyebrow {{
                color: var(--app-accent);
                font-size: 0.76rem;
                font-weight: 700;
                letter-spacing: 0;
                margin-bottom: 8px;
                text-transform: uppercase;
            }}

            .hero-title {{
                color: var(--app-text);
                font-size: 2rem;
                font-weight: 760;
                line-height: 1.15;
                margin: 0;
            }}

            .hero-copy {{
                color: var(--app-muted);
                font-size: 0.96rem;
                line-height: 1.55;
                margin-top: 8px;
                max-width: 760px;
            }}

            .theme-label {{
                color: var(--app-muted);
                font-size: 0.72rem;
                font-weight: 700;
                margin-bottom: 4px;
                text-transform: uppercase;
            }}

            .metric-card {{
                border: 1px solid var(--app-border);
                background: var(--app-surface);
                border-radius: 12px;
                min-height: 104px;
                padding: 16px 18px;
            }}

            .metric-label {{
                color: var(--app-muted);
                font-size: 0.76rem;
                font-weight: 650;
                margin-bottom: 10px;
                text-transform: uppercase;
            }}

            .metric-value {{
                color: var(--app-text);
                font-size: 2rem;
                font-weight: 760;
                line-height: 1;
            }}

            .metric-note {{
                color: var(--app-muted);
                font-size: 0.82rem;
                margin-top: 8px;
            }}

            .meta-line {{
                color: var(--app-muted);
                font-size: 0.9rem;
                margin: 10px 0 16px;
            }}

            .section-title {{
                color: var(--app-text);
                font-size: 1.05rem;
                font-weight: 720;
                margin-bottom: 4px;
            }}

            .section-caption {{
                color: var(--app-muted);
                font-size: 0.88rem;
                margin-bottom: 12px;
            }}

            div[data-testid="stRadio"] label {{
                font-size: 0.82rem;
            }}

            div[data-testid="stRadio"] > label {{
                display: none;
            }}

            div[data-testid="stRadio"] {{
                border: 1px solid var(--app-border);
                background: var(--app-surface);
                border-radius: 999px;
                padding: 4px 8px;
            }}

            div[data-testid="stDataFrame"] {{
                border: 1px solid var(--app-border);
                border-radius: 10px;
                overflow: hidden;
            }}

            div[data-testid="stTabs"] button {{
                color: var(--app-muted);
            }}

            div[data-testid="stTabs"] button[aria-selected="true"] {{
                color: var(--app-accent);
            }}

            @media (max-width: 780px) {{
                .topbar {{
                    display: block;
                }}

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


def render_metric_card(label: str, value: int | str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Monitorados", total_monitorado, "Registros na base atual")
    with col2:
        render_metric_card("Novos", novos, "Último relatório")
    with col3:
        render_metric_card("Removidos", removidos, "Último relatório")
    with col4:
        render_metric_card("Alterados", alterados, "Último relatório")

    st.markdown(
        f"""
        <div class="meta-line">
            Último snapshot histórico: <strong>{history_file.name if history_file else "-"}</strong>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            Última execução com relatório: <strong>{format_timestamp(latest_report_date or latest_history_date)}</strong>
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
