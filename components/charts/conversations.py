"""Gráficos da Tab 2 — Conversas & Engajamento."""

import pandas as pd
import plotly.graph_objects as go

from data.queries import (
    conversation_size_distribution,
    conversations_per_day,
    identification_rate,
    recent_conversations,
    response_time_by_intent,
)

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dee2e6"),
    margin=dict(l=10, r=10, t=70, b=10),
)


def fig_conversations_per_day(days: int = 30) -> go.Figure:
    """Barras diárias + linha de média móvel 7 dias."""
    df = conversations_per_day(days)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Conversas por Dia — sem dados", **_LAYOUT)
        return fig

    df["dia"] = pd.to_datetime(df["dia"])
    df = df.sort_values("dia")
    df["media7"] = df["total"].rolling(7, min_periods=1).mean().round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["dia"], y=df["total"],
        name="Conversas",
        marker_color="#20c997",
        hovertemplate="%{x|%d/%m}<br>Conversas: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["dia"], y=df["media7"],
        name="Média 7d",
        mode="lines",
        line=dict(color="#ffc107", dash="dot", width=2),
        hovertemplate="%{x|%d/%m}<br>Média 7d: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title=f"Conversas por Dia (últimos {days} dias)",
        xaxis_title="Data",
        yaxis_title="Conversas",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        bargap=0.15,
        **_LAYOUT,
    )
    return fig


def fig_conversation_size(days: int = 30) -> go.Figure:
    """Histograma do tamanho de conversa (nº de mensagens)."""
    df = conversation_size_distribution()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Tamanho das Conversas — sem dados", **_LAYOUT)
        return fig

    fig = go.Figure(go.Histogram(
        x=df["num_messages"],
        nbinsx=20,
        marker_color="#6ea8fe",
        hovertemplate="Mensagens: %{x}<br>Conversas: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title="Distribuição do Tamanho de Conversa",
        xaxis_title="Mensagens por conversa",
        yaxis_title="Quantidade",
        **_LAYOUT,
    )
    return fig


def fig_identification_gauge() -> go.Figure:
    """Gauge de taxa de identificação (user_name coletado)."""
    data = identification_rate()
    rate = data["rate"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rate,
        delta={"reference": 70, "suffix": "%", "font": {"size": 14}},
        number={"suffix": "%", "font": {"size": 26}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#20c997"},
            "steps": [
                {"range": [0, 40], "color": "#343a40"},
                {"range": [40, 70], "color": "#495057"},
                {"range": [70, 100], "color": "#3d6b5e"},
            ],
            "threshold": {
                "line": {"color": "#ffc107", "width": 3},
                "thickness": 0.75,
                "value": 70,
            },
        },
        title={"text": f"Taxa de Identificação<br><sub>{data['com_nome']} de {data['total']} conversas</sub>"},
    ))
    fig.update_layout(**_LAYOUT, height=300)
    return fig


def fig_response_time() -> go.Figure:
    """Box plot do tempo de resposta por intent."""
    df = response_time_by_intent()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Tempo de Resposta — sem dados", **_LAYOUT)
        return fig

    intents = df["intent"].unique()
    colors = [
        "#20c997", "#6ea8fe", "#ffc107", "#f8d7da",
        "#d63384", "#fd7e14", "#6f42c1",
    ]

    fig = go.Figure()
    for i, intent in enumerate(intents):
        subset = df[df["intent"] == intent]["seconds"]
        fig.add_trace(go.Box(
            y=subset,
            name=intent,
            marker_color=colors[i % len(colors)],
            boxpoints=False,
            hovertemplate=f"<b>{intent}</b><br>Tempo: %{{y:.1f}}s<extra></extra>",
        ))

    fig.update_layout(
        title="Tempo de Resposta por Intent (segundos)",
        yaxis_title="Segundos",
        showlegend=False,
        **_LAYOUT,
    )
    return fig


def table_recent_conversations() -> pd.DataFrame:
    """DataFrame de conversas recentes para exibição em DataTable Dash."""
    df = recent_conversations(10)
    df = df.rename(columns={
        "phone_number": "Telefone",
        "user_name": "Nome",
        "status": "Status",
        "started_at": "Início",
        "last_message_at": "Última msg",
        "num_messages": "Msgs",
        "last_intent": "Último intent",
    })
    for col in ["Início", "Última msg"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime("%d/%m %H:%M")
    return df
