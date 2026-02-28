"""
Camada de dados: queries SQL analíticas → DataFrames pandas.

Todas as queries usam timezone America/Sao_Paulo (herdado da conexão em config.py).
Intents vêm das mensagens outbound (resposta do agente), não das inbound.
"""

import pandas as pd
from sqlalchemy import text

from config import engine


# ── Utilitário ───────────────────────────────────────────────────────────────

def _q(sql: str, **params) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def mask_phone(phone: str) -> str:
    """Mascara número de telefone preservando apenas os 4 últimos dígitos."""
    if not phone or len(phone) < 6:
        return "****"
    return phone[:2] + "****" + phone[-4:]


# ── KPIs ─────────────────────────────────────────────────────────────────────

def kpi_conversations_today() -> dict:
    df = _q("""
        SELECT
            COUNT(*) FILTER (WHERE started_at >= CURRENT_DATE) AS hoje,
            COUNT(*) FILTER (WHERE started_at >= CURRENT_DATE - INTERVAL '1 day'
                              AND started_at < CURRENT_DATE) AS ontem
        FROM conversations
    """)
    hoje = int(df["hoje"].iloc[0])
    ontem = int(df["ontem"].iloc[0])
    delta = round((hoje - ontem) / ontem * 100, 1) if ontem else None
    return {"value": hoje, "delta": delta}


def kpi_messages_today() -> dict:
    df = _q("""
        SELECT
            COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE) AS hoje,
            COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
                              AND created_at < CURRENT_DATE) AS ontem
        FROM messages
    """)
    hoje = int(df["hoje"].iloc[0])
    ontem = int(df["ontem"].iloc[0])
    delta = round((hoje - ontem) / ontem * 100, 1) if ontem else None
    return {"value": hoje, "delta": delta}


def kpi_unique_users_today() -> dict:
    df = _q("""
        SELECT
            COUNT(DISTINCT phone_number) FILTER (
                WHERE started_at >= CURRENT_DATE) AS hoje,
            COUNT(DISTINCT phone_number) FILTER (
                WHERE started_at >= CURRENT_DATE - INTERVAL '1 day'
                  AND started_at < CURRENT_DATE) AS ontem
        FROM conversations
    """)
    hoje = int(df["hoje"].iloc[0])
    ontem = int(df["ontem"].iloc[0])
    delta = round((hoje - ontem) / ontem * 100, 1) if ontem else None
    return {"value": hoje, "delta": delta}


def kpi_top_intent_today() -> dict:
    df = _q("""
        SELECT intent, COUNT(*) AS total
        FROM messages
        WHERE direction = 'outbound'
          AND intent IS NOT NULL
          AND created_at >= CURRENT_DATE
        GROUP BY intent
        ORDER BY total DESC
        LIMIT 1
    """)
    if df.empty:
        return {"value": "—", "delta": None}
    return {"value": df["intent"].iloc[0], "delta": None}


# ── Tab 1: Visão Geral ────────────────────────────────────────────────────────

def volume_by_hour_24h() -> pd.DataFrame:
    """Volume de mensagens por hora nas últimas 24h, separado por direção."""
    return _q("""
        SELECT
            DATE_TRUNC('hour', created_at) AS hora,
            direction,
            COUNT(*) AS total
        FROM messages
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY hora, direction
        ORDER BY hora
    """)


def activity_heatmap() -> pd.DataFrame:
    """Contagem de mensagens por hora do dia × dia da semana (0=Dom … 6=Sáb)."""
    return _q("""
        SELECT
            EXTRACT(DOW  FROM created_at)::int AS dow,
            EXTRACT(HOUR FROM created_at)::int AS hour,
            COUNT(*) AS total
        FROM messages
        GROUP BY dow, hour
    """)


# ── Tab 2: Conversas & Engajamento ───────────────────────────────────────────

def conversations_per_day(days: int = 30) -> pd.DataFrame:
    return _q("""
        SELECT
            DATE(started_at) AS dia,
            COUNT(*) AS total
        FROM conversations
        WHERE started_at >= NOW() - INTERVAL ':days days'
        GROUP BY dia
        ORDER BY dia
    """, days=days)


def conversation_size_distribution() -> pd.DataFrame:
    """Número de mensagens por conversa."""
    return _q("""
        SELECT conversation_id, COUNT(*) AS num_messages
        FROM messages
        GROUP BY conversation_id
    """)


def identification_rate() -> dict:
    """Taxa de conversas com nome de usuário coletado."""
    df = _q("""
        SELECT
            COUNT(*) FILTER (WHERE user_name IS NOT NULL) AS com_nome,
            COUNT(*) AS total
        FROM conversations
    """)
    com_nome = int(df["com_nome"].iloc[0])
    total = int(df["total"].iloc[0])
    rate = round(com_nome / total * 100, 1) if total else 0.0
    return {"com_nome": com_nome, "total": total, "rate": rate}


def response_time_by_intent() -> pd.DataFrame:
    """Tempo de resposta (segundos) entre inbound e o próximo outbound, por intent."""
    return _q("""
        SELECT
            m2.intent,
            EXTRACT(EPOCH FROM (m2.created_at - m1.created_at))::float AS seconds
        FROM messages m1
        JOIN messages m2
          ON m2.conversation_id = m1.conversation_id
         AND m2.direction = 'outbound'
         AND m2.created_at > m1.created_at
        WHERE m1.direction = 'inbound'
          AND m2.intent IS NOT NULL
          AND EXTRACT(EPOCH FROM (m2.created_at - m1.created_at)) < 300
    """)


def recent_conversations(limit: int = 10) -> pd.DataFrame:
    """Conversas recentes com phone mascarado."""
    df = _q("""
        SELECT
            c.phone_number,
            c.user_name,
            c.status,
            c.started_at,
            c.last_message_at,
            COUNT(m.id) AS num_messages,
            MAX(m.intent) FILTER (WHERE m.direction = 'outbound') AS last_intent
        FROM conversations c
        LEFT JOIN messages m ON m.conversation_id = c.id
        GROUP BY c.id
        ORDER BY c.last_message_at DESC
        LIMIT :limit
    """, limit=limit)
    df["phone_number"] = df["phone_number"].apply(mask_phone)
    return df


# ── Tab 3: Intents & Sentimentos ─────────────────────────────────────────────

def intent_distribution(days: int = 30) -> pd.DataFrame:
    return _q("""
        SELECT intent, COUNT(*) AS total
        FROM messages
        WHERE direction = 'outbound'
          AND intent IS NOT NULL
          AND (:days = 0 OR created_at >= NOW() - INTERVAL '1 day' * :days)
        GROUP BY intent
        ORDER BY total DESC
    """, days=days)


def intent_evolution_weekly() -> pd.DataFrame:
    return _q("""
        SELECT
            DATE_TRUNC('week', created_at) AS semana,
            intent,
            COUNT(*) AS total
        FROM messages
        WHERE direction = 'outbound'
          AND intent IS NOT NULL
        GROUP BY semana, intent
        ORDER BY semana
    """)


def sentiment_by_intent(days: int = 30) -> pd.DataFrame:
    return _q("""
        SELECT intent, sentiment, COUNT(*) AS total
        FROM messages
        WHERE direction = 'outbound'
          AND intent IS NOT NULL
          AND sentiment IS NOT NULL
          AND (:days = 0 OR created_at >= NOW() - INTERVAL '1 day' * :days)
        GROUP BY intent, sentiment
        ORDER BY intent, total DESC
    """, days=days)


# ── Tab 4: ONGs Parceiras ─────────────────────────────────────────────────────

def ongs_by_category() -> pd.DataFrame:
    return _q("""
        SELECT
            category,
            COALESCE(subcategory, 'Geral') AS subcategory,
            name,
            state,
            city,
            is_active,
            pix_key IS NOT NULL AS has_pix
        FROM ongs
        WHERE is_active = true
        ORDER BY category, subcategory, name
    """)


def ongs_by_state() -> pd.DataFrame:
    return _q("""
        SELECT state, COUNT(*) AS total
        FROM ongs
        WHERE is_active = true
        GROUP BY state
        ORDER BY total DESC
    """)


def ongs_pix_coverage() -> pd.DataFrame:
    return _q("""
        SELECT
            CASE WHEN pix_key IS NOT NULL THEN 'Com PIX' ELSE 'Sem PIX' END AS tipo,
            COUNT(*) AS total
        FROM ongs
        WHERE is_active = true
        GROUP BY tipo
    """)


def ongs_list() -> pd.DataFrame:
    return _q("""
        SELECT name, category, subcategory, city, state,
               pix_key IS NOT NULL AS has_pix,
               bank_info IS NOT NULL AS has_bank,
               is_active
        FROM ongs
        ORDER BY name
    """)


# ── Tab 5: Guard-Rails & Segurança ───────────────────────────────────────────

def oos_rate_daily(days: int = 30) -> pd.DataFrame:
    """Taxa diária de mensagens 'Fora do Escopo' sobre o total outbound."""
    return _q("""
        SELECT
            DATE(created_at) AS dia,
            COUNT(*) FILTER (WHERE intent = 'Fora do Escopo') AS oos,
            COUNT(*) AS total_outbound,
            ROUND(
                COUNT(*) FILTER (WHERE intent = 'Fora do Escopo')::numeric
                / NULLIF(COUNT(*), 0) * 100, 2
            ) AS pct_oos
        FROM messages
        WHERE direction = 'outbound'
          AND intent IS NOT NULL
          AND (:days = 0 OR created_at >= NOW() - INTERVAL '1 day' * :days)
        GROUP BY dia
        ORDER BY dia
    """, days=days)


def suspicious_conversations(threshold: float = 0.8) -> pd.DataFrame:
    """
    Conversas onde a proporção de mensagens inbound é alta (≥ threshold)
    sem respostas outbound correspondentes — proxy para bots ou rate limiting.
    """
    df = _q("""
        SELECT
            c.phone_number,
            c.started_at,
            COUNT(m.id) AS total_msgs,
            COUNT(m.id) FILTER (WHERE m.direction = 'inbound') AS inbound,
            COUNT(m.id) FILTER (WHERE m.direction = 'outbound') AS outbound
        FROM conversations c
        JOIN messages m ON m.conversation_id = c.id
        GROUP BY c.id
        HAVING COUNT(m.id) >= 3
           AND COUNT(m.id) FILTER (WHERE m.direction = 'outbound') = 0
            OR (
                COUNT(m.id) FILTER (WHERE m.direction = 'inbound')::float
                / NULLIF(COUNT(m.id), 0) >= :threshold
               )
        ORDER BY c.started_at DESC
        LIMIT 50
    """, threshold=threshold)
    df["phone_number"] = df["phone_number"].apply(mask_phone)
    return df


def guardrail_events_summary() -> pd.DataFrame:
    """Estimativa de eventos por tipo de guard-rail (heurística por padrão de conversa)."""
    return _q("""
        SELECT
            DATE(c.started_at) AS dia,
            COUNT(DISTINCT c.id) FILTER (
                WHERE NOT EXISTS (
                    SELECT 1 FROM messages m2
                    WHERE m2.conversation_id = c.id AND m2.direction = 'outbound'
                )
            ) AS sem_resposta,
            COUNT(DISTINCT c.id) FILTER (
                WHERE EXISTS (
                    SELECT 1 FROM messages m2
                    WHERE m2.conversation_id = c.id
                      AND m2.direction = 'outbound'
                      AND m2.intent = 'Fora do Escopo'
                )
            ) AS oos_detectado
        FROM conversations c
        GROUP BY dia
        ORDER BY dia DESC
        LIMIT 30
    """)
