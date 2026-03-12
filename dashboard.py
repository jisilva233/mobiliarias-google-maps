"""
Dashboard Streamlit para visualização de imobiliárias mapeadas.

Uso:
    streamlit run dashboard.py
"""

import logging

import pandas as pd
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Mapa de Imobiliárias",
    page_icon="🏠",
    layout="wide",
)


@st.cache_data(ttl=300)
def load_data(cidade: str | None = None) -> pd.DataFrame:
    """Carrega dados do Supabase com cache de 5 minutos."""
    try:
        from db.client import get_client
        from db.repository import AgencyRepository

        client = get_client()
        repo = AgencyRepository(client)
        records = repo.fetch_all(cidade=cidade or None)
        return pd.DataFrame(records)
    except Exception as exc:
        logger.error("Erro ao carregar dados: %s", exc)
        return pd.DataFrame()


def main():
    st.title("🏠 Mapa de Imobiliárias")
    st.caption("Dados coletados via Google Maps · Atualizado via `scan_agencies.py`")

    from dashboard.components import render_filters, render_metrics, render_table, render_ranking, render_scan_input
    from dashboard.map_view import render_map

    # Seção para escanear nova cidade
    render_scan_input()

    st.divider()

    # Carrega todos os dados
    df = load_data()

    if df.empty:
        st.error(
            "⚠️ Nenhum dado encontrado.\n\n"
            "Verifique se:\n"
            "- As variáveis SUPABASE_URL e SUPABASE_KEY estão no `.env`\n"
            "- A tabela `real_estate_agencies` existe (rode `python scan_agencies.py --setup-db`)\n"
            "- Você já executou `python scan_agencies.py --city 'Sua Cidade'`"
        )
        return

    # Filtros na sidebar
    filtered = render_filters(df)

    # Métricas
    render_metrics(filtered)

    st.divider()

    # Abas
    tab_lista, tab_mapa, tab_ranking = st.tabs(["📋 Lista", "🗺️ Mapa", "🏆 Ranking"])

    with tab_lista:
        render_table(filtered)

    with tab_mapa:
        render_map(filtered)

    with tab_ranking:
        render_ranking(filtered)

    st.divider()
    st.caption(
        f"Total na base: {len(df)} imobiliárias · "
        f"Exibindo: {len(filtered)} após filtros"
    )


if __name__ == "__main__":
    main()
