"""Gráficos da Tab 1 — Visão Geral: heatmap de atividade e volume 24h."""

import plotly.graph_objects as go

from data.queries import activity_heatmap, volume_by_hour_24h

_DAYS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
_HOURS = [f"{h:02d}h" for h in range(24)]

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dee2e6"),
    margin=dict(l=10, r=10, t=70, b=10),
)


def fig_activity_heatmap() -> go.Figure:
    """Heatmap: hora do dia (eixo X) × dia da semana (eixo Y)."""
    df = activity_heatmap()

    # Monta matriz 7 × 24 (dow × hour)
    import numpy as np
    z = np.zeros((7, 24), dtype=int)
    for _, row in df.iterrows():
        dow = int(row["dow"])
        hour = int(row["hour"])
        z[dow][hour] = int(row["total"])

    fig = go.Figure(go.Heatmap(
        z=z,
        x=_HOURS,
        y=_DAYS,
        colorscale="Teal",
        hoverongaps=False,
        hovertemplate="<b>%{y} %{x}</b><br>Mensagens: %{z}<extra></extra>",
        colorbar=dict(title="Msgs"),
    ))
    fig.update_layout(
        title="Heatmap de Atividade (hora × dia da semana)",
        **_LAYOUT,
    )
    return fig


def fig_volume_24h() -> go.Figure:
    """Área dupla inbound/outbound nas últimas 24h."""
    df = volume_by_hour_24h()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Volume por Hora (últimas 24h) — sem dados", **_LAYOUT)
        return fig

    inbound = df[df["direction"] == "inbound"].set_index("hora")
    outbound = df[df["direction"] == "outbound"].set_index("hora")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=inbound.index, y=inbound["total"],
        mode="lines", name="Inbound",
        fill="tozeroy", line=dict(color="#20c997"),
        hovertemplate="%{x|%Hh}<br>Inbound: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=outbound.index, y=outbound["total"],
        mode="lines", name="Outbound",
        fill="tozeroy", line=dict(color="#6ea8fe"),
        hovertemplate="%{x|%Hh}<br>Outbound: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title="Volume por Hora — últimas 24h",
        xaxis_title="Hora",
        yaxis_title="Mensagens",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        **_LAYOUT,
    )
    return fig
