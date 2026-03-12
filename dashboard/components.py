import asyncio
import subprocess
import pandas as pd
import streamlit as st


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza filtros na sidebar e retorna DataFrame filtrado."""
    st.sidebar.header("Filtros")

    cidades = sorted(df["cidade"].dropna().unique().tolist())
    cidade_sel = st.sidebar.multiselect(
        "Cidade", options=cidades, default=cidades
    )

    rating_min = st.sidebar.slider(
        "Avaliação mínima", min_value=0.0, max_value=5.0, value=0.0, step=0.5
    )

    filtered = df[df["cidade"].isin(cidade_sel)]
    if rating_min > 0:
        filtered = filtered[
            filtered["rating"].isna() | (filtered["rating"] >= rating_min)
        ]

    return filtered


def render_metrics(df: pd.DataFrame) -> None:
    """Exibe métricas resumidas."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Imobiliárias", len(df))
    col2.metric("Cidades", df["cidade"].nunique())

    rated = df["rating"].dropna()
    col3.metric(
        "Avaliação Média",
        f"{rated.mean():.1f} ⭐" if not rated.empty else "—",
    )
    col4.metric(
        "Maior Avaliação",
        f"{rated.max():.1f} ⭐" if not rated.empty else "—",
    )


def render_table(df: pd.DataFrame) -> None:
    """Renderiza tabela interativa das imobiliárias."""
    st.subheader("📋 Lista de Imobiliárias")

    display_cols = ["nome", "cidade", "rating", "reviews", "telefone", "website", "endereco"]
    available = [c for c in display_cols if c in df.columns]

    st.dataframe(
        df[available].sort_values("rating", ascending=False, na_position="last"),
        use_container_width=True,
        hide_index=True,
        column_config={
            "nome": st.column_config.TextColumn("Nome"),
            "cidade": st.column_config.TextColumn("Cidade"),
            "rating": st.column_config.NumberColumn("⭐ Rating", format="%.1f"),
            "reviews": st.column_config.NumberColumn("Reviews"),
            "telefone": st.column_config.TextColumn("Telefone"),
            "website": st.column_config.LinkColumn("Website"),
            "endereco": st.column_config.TextColumn("Endereço"),
        },
    )


def render_ranking(df: pd.DataFrame) -> None:
    """Renderiza ranking por avaliação."""
    st.subheader("🏆 Ranking por Avaliação")

    ranked = (
        df[df["rating"].notna()]
        .sort_values("rating", ascending=False)
        .head(20)[["nome", "cidade", "rating", "reviews"]]
        .reset_index(drop=True)
    )
    ranked.index += 1

    if ranked.empty:
        st.info("Nenhuma imobiliária com avaliação disponível.")
        return

    st.dataframe(
        ranked,
        use_container_width=True,
        column_config={
            "nome": st.column_config.TextColumn("Imobiliária"),
            "cidade": st.column_config.TextColumn("Cidade"),
            "rating": st.column_config.ProgressColumn(
                "⭐ Avaliação", min_value=0, max_value=5, format="%.1f"
            ),
            "reviews": st.column_config.NumberColumn("Reviews"),
        },
    )


def render_scan_input() -> None:
    """Renderiza campo para escanear nova cidade."""
    st.subheader("🔍 Escanear Nova Cidade")

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        cidade = st.text_input(
            "Nome da cidade",
            placeholder="Ex: Florianopolis, Sao Paulo, Porto Alegre",
            help="Digite o nome da cidade para escanear imobiliárias"
        )

    with col2:
        geocode_flag = st.checkbox("Com geocoding", value=True, help="Busca coordenadas (lat/lon)")

    with col3:
        btn_click = st.button("Escanear", type="primary", use_container_width=True)

    if btn_click and cidade:
        with st.spinner(f"Escaneando {cidade}..."):
            try:
                cmd = ["python", "scan_agencies.py", "--city", cidade]
                if geocode_flag:
                    cmd.append("--geocode")

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    st.success(f"Scan concluido para {cidade}. Atualize a pagina para ver os dados.")
                else:
                    st.error(f"Erro ao escanear: {result.stderr}")
            except subprocess.TimeoutExpired:
                st.error(f"Timeout ao escanear {cidade} (limite: 5 minutos)")
            except Exception as e:
                st.error(f"Erro: {str(e)}")
    elif btn_click:
        st.warning("Digite o nome de uma cidade para escanear.")
