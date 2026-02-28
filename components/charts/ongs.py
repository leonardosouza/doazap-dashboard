"""Gráficos da Tab 4 — ONGs Parceiras."""

import pandas as pd
import plotly.graph_objects as go

from data.queries import ongs_by_category, ongs_by_state, ongs_list, ongs_pix_coverage

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dee2e6"),
    margin=dict(l=10, r=10, t=40, b=10),
)


def fig_ongs_treemap() -> go.Figure:
    """Treemap hierárquico: categoria → subcategoria → ONG."""
    df = ongs_by_category()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="ONGs por Categoria — sem dados", **_LAYOUT)
        return fig

    # Valores uniformes (1 por ONG) para que o tamanho reflita quantidade
    fig = go.Figure(go.Treemap(
        labels=df["name"].tolist() + df["subcategory"].unique().tolist() + df["category"].unique().tolist(),
        parents=(
            df["subcategory"].tolist()
            + df["category"].unique().tolist()
            + [""] * len(df["category"].unique())
        ),
        values=[1] * len(df) + [0] * len(df["subcategory"].unique()) + [0] * len(df["category"].unique()),
        branchvalues="total",
        marker=dict(colorscale="Teal"),
        hovertemplate="<b>%{label}</b><br>%{value} ONG(s)<extra></extra>",
        maxdepth=3,
    ))
    fig.update_layout(title="ONGs por Categoria e Subcategoria", **_LAYOUT)
    return fig


def fig_ongs_by_state() -> go.Figure:
    """Barras horizontais de ONGs ativas por estado."""
    df = ongs_by_state()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="ONGs por Estado — sem dados", **_LAYOUT)
        return fig

    fig = go.Figure(go.Bar(
        x=df["total"],
        y=df["state"],
        orientation="h",
        marker_color="#20c997",
        hovertemplate="<b>%{y}</b><br>ONGs: %{x}<extra></extra>",
    ))
    fig.update_layout(
        title="ONGs Ativas por Estado",
        xaxis_title="Quantidade",
        yaxis=dict(autorange="reversed"),
        **_LAYOUT,
    )
    return fig


def fig_ongs_pix() -> go.Figure:
    """Donut: ONGs com vs sem chave PIX."""
    df = ongs_pix_coverage()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Cobertura PIX — sem dados", **_LAYOUT)
        return fig

    fig = go.Figure(go.Pie(
        labels=df["tipo"],
        values=df["total"],
        hole=0.5,
        marker=dict(colors=["#20c997", "#495057"]),
        hovertemplate="<b>%{label}</b><br>%{value} ONGs (%{percent})<extra></extra>",
    ))
    fig.update_layout(title="Cobertura de Chave PIX", **_LAYOUT)
    return fig


def table_ongs_list() -> pd.DataFrame:
    """DataFrame de ONGs para exibição em DataTable Dash."""
    df = ongs_list()
    df = df.rename(columns={
        "name": "Nome",
        "category": "Categoria",
        "subcategory": "Subcategoria",
        "city": "Cidade",
        "state": "UF",
        "has_pix": "PIX",
        "has_bank": "Dados bancários",
        "is_active": "Ativa",
    })
    df["PIX"] = df["PIX"].map({True: "✓", False: "—"})
    df["Dados bancários"] = df["Dados bancários"].map({True: "✓", False: "—"})
    df["Ativa"] = df["Ativa"].map({True: "Sim", False: "Não"})
    return df
