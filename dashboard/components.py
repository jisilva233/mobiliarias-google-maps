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
