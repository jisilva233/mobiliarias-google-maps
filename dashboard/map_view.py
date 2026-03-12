import logging
import re

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


def _parse_coords_from_endereco(endereco: str):
    """Tenta extrair lat/lon de string de endereço (fallback simples)."""
    # Google Maps às vezes inclui coords no endereço — não é confiável
    # Retorna None; geocoding real requer API externa
    return None, None


def render_map(df: pd.DataFrame) -> None:
    """Renderiza mapa com as imobiliárias que têm coordenadas."""
    st.subheader("🗺️ Mapa de Imobiliárias")

    # Verifica se há colunas de latitude/longitude
    has_coords = "latitude" in df.columns and "longitude" in df.columns
    if not has_coords:
        st.info(
            "📍 O mapa requer colunas `latitude` e `longitude` na tabela do Supabase.\n\n"
            "Para habilitar:\n"
            "1. Adicione as colunas `latitude FLOAT` e `longitude FLOAT` à tabela.\n"
            "2. Use uma API de geocoding (ex: Google Geocoding API) para popular as coordenadas.\n"
            "3. Rode `scan_agencies.py` novamente após a atualização."
        )
        return

    map_df = df[df["latitude"].notna() & df["longitude"].notna()].copy()

    if map_df.empty:
        st.warning("Nenhuma imobiliária com coordenadas disponíveis.")
        return

    # Mapa nativo do Streamlit (st.map)
    st.map(
        map_df.rename(columns={"latitude": "lat", "longitude": "lon"})[
            ["lat", "lon", "nome"]
        ],
        zoom=12,
    )

    st.caption(f"{len(map_df)} imobiliárias exibidas no mapa.")
