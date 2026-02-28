"""Gráficos da Tab 3 — Intents & Sentimentos."""

import plotly.graph_objects as go

from data.queries import intent_distribution, intent_evolution_weekly, sentiment_by_intent

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dee2e6"),
    margin=dict(l=10, r=10, t=40, b=10),
)

_INTENT_COLORS = {
    "Quero Doar": "#20c997",
    "Busco Ajuda/Beneficiário": "#6ea8fe",
    "Voluntariado": "#ffc107",
    "Parceria Corporativa": "#fd7e14",
    "Informação Geral": "#6f42c1",
    "Ambíguo": "#adb5bd",
    "Fora do Escopo": "#dc3545",
}


def fig_intent_donut(days: int = 30) -> go.Figure:
    """Donut chart de distribuição de intents."""
    df = intent_distribution(days)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Distribuição de Intents — sem dados", **_LAYOUT)
        return fig

    colors = [_INTENT_COLORS.get(i, "#868e96") for i in df["intent"]]
    fig = go.Figure(go.Pie(
        labels=df["intent"],
        values=df["total"],
        hole=0.45,
        marker=dict(colors=colors),
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Total: %{value}<br>%{percent}<extra></extra>",
    ))
    label = "todos os tempos" if days == 0 else f"últimos {days} dias"
    fig.update_layout(
        title=f"Distribuição de Intents ({label})",
        legend=dict(orientation="v", x=1.05),
        **_LAYOUT,
    )
    return fig


def fig_intent_evolution() -> go.Figure:
    """Stacked bar semanal dos intents."""
    df = intent_evolution_weekly()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Evolução de Intents — sem dados", **_LAYOUT)
        return fig

    import pandas as pd
    df["semana"] = pd.to_datetime(df["semana"]).dt.strftime("%d/%m/%Y")

    fig = go.Figure()
    for intent in df["intent"].unique():
        subset = df[df["intent"] == intent]
        fig.add_trace(go.Bar(
            x=subset["semana"],
            y=subset["total"],
            name=intent,
            marker_color=_INTENT_COLORS.get(intent, "#868e96"),
            hovertemplate=f"<b>{intent}</b><br>Semana: %{{x}}<br>Total: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="stack",
        title="Evolução Semanal de Intents",
        xaxis_title="Semana",
        yaxis_title="Mensagens",
        legend=dict(orientation="h", y=-0.25),
        **_LAYOUT,
    )
    return fig


def fig_sentiment_by_intent(days: int = 30) -> go.Figure:
    """Grouped bar: sentimento × intent."""
    df = sentiment_by_intent(days)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sentimento por Intent — sem dados", **_LAYOUT)
        return fig

    sentiment_colors = {
        "positivo": "#20c997",
        "neutro": "#adb5bd",
        "negativo": "#dc3545",
    }

    fig = go.Figure()
    for sentiment in df["sentiment"].unique():
        subset = df[df["sentiment"] == sentiment]
        fig.add_trace(go.Bar(
            x=subset["intent"],
            y=subset["total"],
            name=sentiment.capitalize(),
            marker_color=sentiment_colors.get(sentiment.lower(), "#6ea8fe"),
            hovertemplate=f"<b>%{{x}}</b><br>{sentiment}: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        barmode="group",
        title="Sentimento por Intent",
        xaxis_title="Intent",
        yaxis_title="Mensagens",
        legend=dict(orientation="h", y=1.1),
        **_LAYOUT,
    )
    return fig
