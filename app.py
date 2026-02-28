"""
DoaZap Dashboard — aplicação Plotly Dash.

Entry point: Dash app com BasicAuth, 5 tabs e auto-refresh a cada 5 minutos.
"""

import dash_auth
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dcc, html
from dash.dash_table import DataTable

import config
from components.charts.conversations import (
    fig_conversations_per_day,
    fig_conversation_size,
    fig_identification_gauge,
    fig_response_time,
    table_recent_conversations,
)
from components.charts.guardrails import (
    fig_guardrail_events,
    fig_oos_rate,
    table_suspicious_conversations,
)
from components.charts.intents import (
    fig_intent_donut,
    fig_intent_evolution,
    fig_sentiment_by_intent,
)
from components.charts.ongs import (
    fig_ongs_by_state,
    fig_ongs_treemap,
    table_ongs_list,
)
from components.charts.overview import fig_activity_heatmap, fig_volume_24h
from components.kpis import kpi_card
from data.queries import (
    kpi_conversations_today,
    kpi_messages_today,
    kpi_top_intent_today,
    kpi_unique_users_today,
)

# ── App ──────────────────────────────────────────────────────────────────────

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
    title="DoaZap Dashboard",
    suppress_callback_exceptions=True,
)
server = app.server  # gunicorn entry point

config.cache.init_app(server)
dash_auth.BasicAuth(app, config.AUTH_USERS)

# ── Helpers ───────────────────────────────────────────────────────────────────

_TABLE_STYLE = {
    "style_header": {"backgroundColor": "#212529", "color": "#dee2e6", "fontWeight": "bold"},
    "style_data": {"backgroundColor": "#1a1d21", "color": "#adb5bd"},
    "style_data_conditional": [{"if": {"row_index": "odd"}, "backgroundColor": "#212529"}],
    "style_table": {"overflowX": "auto"},
    "page_size": 10,
}

_PERIOD_OPTIONS = [
    {"label": "Últimos 7 dias", "value": 7},
    {"label": "Últimos 30 dias", "value": 30},
    {"label": "Todos os tempos", "value": 0},
]


def _graph(fig_id: str) -> dcc.Graph:
    return dcc.Graph(id=fig_id, config={"displayModeBar": False})


def _section(title: str, *children) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([html.H6(title, className="text-muted mb-3"), *children]),
        className="mb-4 border-0 shadow-sm",
    )


# ── Layout ────────────────────────────────────────────────────────────────────

def _kpi_row() -> dbc.Row:
    return dbc.Row(id="kpi-row", className="mb-4 g-3")


def _period_filter(filter_id: str) -> dbc.Row:
    return dbc.Row(dbc.Col(dbc.RadioItems(
        id=filter_id,
        options=_PERIOD_OPTIONS,
        value=30,
        inline=True,
        className="mb-3",
    )))


# Tab 1 — Visão Geral
tab1 = dbc.Tab(label="Visão Geral", tab_id="tab-overview", children=[
    dbc.Row([
        dbc.Col(_graph("fig-volume-24h"), md=8),
        dbc.Col(_graph("fig-heatmap"), md=4),
    ]),
])

# Tab 2 — Conversas & Engajamento
tab2 = dbc.Tab(label="Conversas", tab_id="tab-conversations", children=[
    dbc.Row([
        dbc.Col(_graph("fig-conv-day"), md=8),
        dbc.Col(_graph("fig-conv-gauge"), md=4),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(_graph("fig-conv-size"), md=6),
        dbc.Col(_graph("fig-response-time"), md=6),
    ], className="mb-4"),
    _section("Conversas Recentes", html.Div(id="table-recent-conv")),
])

# Tab 3 — Intents & Sentimentos
tab3 = dbc.Tab(label="Intents", tab_id="tab-intents", children=[
    _period_filter("filter-intents"),
    dbc.Row([
        dbc.Col(_graph("fig-intent-donut"), md=5),
        dbc.Col(_graph("fig-intent-evo"), md=7),
    ], className="mb-4"),
    dbc.Row(dbc.Col(_graph("fig-sentiment"), md=12)),
])

# Tab 4 — ONGs Parceiras
tab4 = dbc.Tab(label="ONGs", tab_id="tab-ongs", children=[
    dbc.Row([
        dbc.Col(_graph("fig-treemap"), md=8),
        dbc.Col(_graph("fig-ongs-state"), md=4),
    ], className="mb-4"),
    _section("Lista de ONGs", html.Div(id="table-ongs")),
])

# Tab 5 — Guard-Rails & Segurança
tab5 = dbc.Tab(label="Guard-Rails", tab_id="tab-guardrails", children=[
    _period_filter("filter-guardrails"),
    dbc.Row([
        dbc.Col(_graph("fig-oos-rate"), md=7),
        dbc.Col(_graph("fig-guardrail-events"), md=5),
    ], className="mb-4"),
    _section("Atividade Suspeita", html.Div(id="table-suspicious")),
])

app.layout = dbc.Container([
    # Header
    dbc.Row(dbc.Col(html.Div([
        html.H3("DoaZap Dashboard", className="d-inline fw-bold text-success"),
        html.Span(" — Analytics em tempo real", className="text-muted ms-2"),
    ]), className="py-3 border-bottom mb-4")),

    # KPI cards
    _kpi_row(),

    # Tabs
    dbc.Tabs([tab1, tab2, tab3, tab4, tab5], id="main-tabs", active_tab="tab-overview"),

    # Auto-refresh a cada 5 minutos
    dcc.Interval(id="interval", interval=config.CACHE_TTL * 1000, n_intervals=0),

], fluid=True, className="px-4")


# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("kpi-row", "children"),
    Input("interval", "n_intervals"),
)
@config.cache.cached(timeout=config.CACHE_TTL, key_prefix="kpis")
def update_kpis(_):
    c = kpi_conversations_today()
    m = kpi_messages_today()
    u = kpi_unique_users_today()
    i = kpi_top_intent_today()
    return [
        dbc.Col(kpi_card("Conversas Hoje", c["value"], c["delta"]), md=3),
        dbc.Col(kpi_card("Mensagens Hoje", m["value"], m["delta"]), md=3),
        dbc.Col(kpi_card("Usuários Únicos", u["value"], u["delta"]), md=3),
        dbc.Col(kpi_card("Intent do Dia", i["value"], i["delta"]), md=3),
    ]


@app.callback(
    Output("fig-volume-24h", "figure"),
    Output("fig-heatmap", "figure"),
    Input("interval", "n_intervals"),
)
@config.cache.cached(timeout=config.CACHE_TTL, key_prefix="overview")
def update_overview(_):
    return fig_volume_24h(), fig_activity_heatmap()


@app.callback(
    Output("fig-conv-day", "figure"),
    Output("fig-conv-gauge", "figure"),
    Output("fig-conv-size", "figure"),
    Output("fig-response-time", "figure"),
    Output("table-recent-conv", "children"),
    Input("interval", "n_intervals"),
)
@config.cache.cached(timeout=config.CACHE_TTL, key_prefix="conversations")
def update_conversations(_):
    df = table_recent_conversations()
    table = DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        **_TABLE_STYLE,
    )
    return (
        fig_conversations_per_day(),
        fig_identification_gauge(),
        fig_conversation_size(),
        fig_response_time(),
        table,
    )


@app.callback(
    Output("fig-intent-donut", "figure"),
    Output("fig-intent-evo", "figure"),
    Output("fig-sentiment", "figure"),
    Input("filter-intents", "value"),
    Input("interval", "n_intervals"),
)
def update_intents(days, _):
    return (
        fig_intent_donut(days),
        fig_intent_evolution(),
        fig_sentiment_by_intent(days),
    )


@app.callback(
    Output("fig-treemap", "figure"),
    Output("fig-ongs-state", "figure"),
    Output("table-ongs", "children"),
    Input("interval", "n_intervals"),
)
@config.cache.cached(timeout=config.CACHE_TTL, key_prefix="ongs")
def update_ongs(_):
    df = table_ongs_list()
    table = DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        filter_action="native",
        sort_action="native",
        **_TABLE_STYLE,
    )
    return fig_ongs_treemap(), fig_ongs_by_state(), table


@app.callback(
    Output("fig-oos-rate", "figure"),
    Output("fig-guardrail-events", "figure"),
    Output("table-suspicious", "children"),
    Input("filter-guardrails", "value"),
    Input("interval", "n_intervals"),
)
def update_guardrails(days, _):
    df = table_suspicious_conversations()
    table = DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df.columns],
        **_TABLE_STYLE,
    )
    return fig_oos_rate(days), fig_guardrail_events(), table


# ── Entry point local ────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
