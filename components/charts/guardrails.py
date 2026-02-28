"""Gráficos da Tab 5 — Guard-Rails & Segurança."""

import pandas as pd
import plotly.graph_objects as go

from data.queries import guardrail_events_summary, oos_rate_daily, suspicious_conversations

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dee2e6"),
    margin=dict(l=10, r=10, t=70, b=10),
)


def fig_oos_rate(days: int = 30) -> go.Figure:
    """Linha diária da taxa 'Fora do Escopo' (%)."""
    df = oos_rate_daily(days)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Taxa Fora do Escopo — sem dados", **_LAYOUT)
        return fig

    df["dia"] = pd.to_datetime(df["dia"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["dia"],
        y=df["pct_oos"].astype(float),
        mode="lines+markers",
        name="% OOS",
        line=dict(color="#dc3545", width=2),
        fill="tozeroy",
        fillcolor="rgba(220,53,69,0.15)",
        hovertemplate="%{x|%d/%m}<br>OOS: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=f"Taxa Diária 'Fora do Escopo' (últimos {days} dias)",
        xaxis_title="Data",
        yaxis_title="% de mensagens OOS",
        yaxis=dict(range=[0, 100]),
        **_LAYOUT,
    )
    return fig


def fig_guardrail_events() -> go.Figure:
    """Barras empilhadas: conversas sem resposta × com OOS detectado por dia."""
    df = guardrail_events_summary()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Eventos de Guard-Rail — sem dados", **_LAYOUT)
        return fig

    df["dia"] = pd.to_datetime(df["dia"])
    df = df.sort_values("dia")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["dia"],
        y=df["sem_resposta"],
        name="Sem resposta (bloqueadas)",
        marker_color="#fd7e14",
        hovertemplate="%{x|%d/%m}<br>Sem resposta: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["dia"],
        y=df["oos_detectado"],
        name="OOS detectado",
        marker_color="#dc3545",
        hovertemplate="%{x|%d/%m}<br>OOS: %{y}<extra></extra>",
    ))
    fig.update_layout(
        barmode="group",
        title="Eventos de Guard-Rail por Dia (últimos 30 dias)",
        xaxis_title="Data",
        yaxis_title="Conversas",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        **_LAYOUT,
    )
    return fig


def table_suspicious_conversations() -> pd.DataFrame:
    """DataFrame de conversas suspeitas para DataTable."""
    df = suspicious_conversations(threshold=0.55)
    if df.empty:
        return pd.DataFrame(columns=["Telefone", "Início", "Total", "Inbound", "Outbound"])
    df = df.rename(columns={
        "phone_number": "Telefone",
        "started_at": "Início",
        "total_msgs": "Total",
        "inbound": "Inbound",
        "outbound": "Outbound",
    })
    df["Início"] = pd.to_datetime(df["Início"]).dt.strftime("%d/%m %H:%M")
    return df
