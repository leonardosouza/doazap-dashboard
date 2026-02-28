"""Componente reutilizável de KPI card."""

import dash_bootstrap_components as dbc
from dash import html


def kpi_card(title: str, value, delta: float | None = None) -> dbc.Card:
    """
    Renderiza um card de KPI com título, valor e variação percentual opcional.

    Args:
        title:  Rótulo do indicador (ex.: "Conversas Hoje")
        value:  Valor principal (int, str ou qualquer coisa renderizável)
        delta:  Variação % em relação ao período anterior.
                Positivo → verde ↑ | Negativo → vermelho ↓ | None → sem badge
    """
    if delta is None:
        delta_badge = html.Span()
    elif delta >= 0:
        delta_badge = dbc.Badge(
            f"↑ {delta:+.1f}%",
            color="success",
            className="ms-2 fs-6",
        )
    else:
        delta_badge = dbc.Badge(
            f"↓ {delta:.1f}%",
            color="danger",
            className="ms-2 fs-6",
        )

    return dbc.Card(
        dbc.CardBody([
            html.P(title, className="text-muted mb-1 small text-uppercase fw-bold"),
            html.Div([
                html.Span(str(value), className="fs-2 fw-bold"),
                delta_badge,
            ], className="d-flex align-items-center"),
        ]),
        className="h-100 border-0 shadow-sm",
    )
