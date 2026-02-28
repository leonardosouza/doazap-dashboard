# Plano: DoaZap Dashboard — Analytics com Plotly Dash

## Contexto

O DoaZap (v1.5.8) acumula dados de conversas, mensagens, intents e sentimentos no banco Supabase
(PostgreSQL, mesmo que o bot). Não há interface de visualização — análises exigem psql direto ou
o Supabase dashboard (não ergonômico para storytelling de dados).

Esta aplicação independente (`doazap-dashboard/`, fora de `doacao-whatsapp/`) conecta ao mesmo
banco de produção e entrega um dashboard interativo multi-página com Plotly Dash. O objetivo é
transformar dados operacionais em inteligência de negócio: volume de uso, efetividade dos
guard-rails, demanda por categoria de ONG e padrões de comportamento dos usuários.

**Versão inicial:** `1.0.0`

---

## Decisões de Arquitetura

| Decisão | Escolha | Motivo |
|---------|---------|--------|
| Framework | **Plotly Dash 2.x** | Framework Python nativo do ecossistema Plotly; zero JS |
| UI components | **Dash Bootstrap Components (DBC)** | Grid, cards e tema responsivo sem CSS custom |
| Tema visual | **DBC `CYBORG`** (dark) | Visual moderno e profissional para apresentação do MBA |
| Auth | **`dash-auth` BasicAuth** | Dados sensíveis (conversas); simples, sem backend de usuários |
| Dados | **pandas + SQLAlchemy `text()`** | Queries analíticas são mais claras em SQL puro |
| Cache | **`flask-caching` (SimpleCache, TTL 5 min)** | Evita N queries ao banco a cada navegação |
| Deploy | **Render (novo Web Service free tier) + gunicorn** | Sem infra nova; separado do bot |
| Repositório | **GitHub público novo** (`doazap-dashboard`) | Separado do `doacao-whatsapp` |
| Phone numbers | **Mascarados** (`****1234`) em tabelas | Privacidade; agregados usam COUNT/GROUP sem PII |

---

## Repositório e Versionamento

### Repositório remoto
- Criar novo repositório público: `github.com/leonardosouza/doazap-dashboard`
- Branch padrão: `main`
- Commits graduais e lineares (um commit por arquivo ou grupo lógico)

### Convenção de versão
- Semantic Versioning: `MAJOR.MINOR.PATCH`
- Versão inicial: `1.0.0` (tag `v1.0.0` ao final da implementação inicial)
- Versão armazenada em `VERSION` (arquivo texto, uma linha)
- CHANGELOG.md seguindo padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)

### Ordem de commits planejada
```
1. chore: bootstrap do projeto (estrutura de pastas, .gitignore, .env.example)
2. chore: requirements.txt e Dockerfile
3. feat: config.py (DATABASE_URL, auth, cache, engine SQLAlchemy)
4. feat: data/queries.py (todas as queries analíticas → DataFrames)
5. feat: components/kpis.py (componente KPI card reutilizável)
6. feat: components/charts/overview.py (heatmap + timeline)
7. feat: components/charts/conversations.py (histograma, box plot, gauge, tabela)
8. feat: components/charts/intents.py (donut, stacked bar, grouped bar)
9. feat: components/charts/ongs.py (treemap, bar, datatable)
10. feat: components/charts/guardrails.py (linha OOS, atividade suspeita)
11. feat: app.py (Dash app, BasicAuth, layout com DBC Tabs, callbacks)
12. docs: README.md, CHANGELOG.md [1.0.0], VERSION 1.0.0
13. TAG v1.0.0 → deploy no Render
```

---

## Estrutura de Pastas

```
doazap-dashboard/
├── app.py                      # Entry point: Dash app, auth, layout multi-página
├── config.py                   # DATABASE_URL, auth, cache TTL via env vars
├── data/
│   └── queries.py              # Todas as queries SQL → DataFrames pandas
├── components/
│   ├── kpis.py                 # Componente KPI card reutilizável
│   └── charts/
│       ├── overview.py         # Heatmap de atividade + timeline de volume
│       ├── conversations.py    # Tamanho de conversa, tempo de resposta
│       ├── intents.py          # Donut de intents, sentimento, evolução
│       ├── ongs.py             # Treemap de categorias, barras por estado
│       └── guardrails.py       # Taxa OOS, guard-rails acionados
├── VERSION                     # "1.0.0"
├── README.md                   # Documentação completa do projeto
├── CHANGELOG.md                # Histórico de versões (Keep a Changelog)
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── Procfile                    # web: gunicorn app:server -b 0.0.0.0:$PORT
```

---

## Tabs do Dashboard (5 páginas)

### Tab 1 — Visão Geral

**KPI cards (linha topo):**
- Conversas hoje | Mensagens hoje | Usuários únicos | Intent mais comum
- Cada card exibe variação % vs dia anterior (seta ↑↓ colorida)

**Gráficos:**
- **Volume por hora** (últimas 24h): área dupla inbound/outbound
- **Heatmap de atividade**: hora (0–23) × dia da semana — intensidade = nº de mensagens
  → Revela padrões de uso (ex.: pico às 19h nas terças)

---

### Tab 2 — Conversas & Engajamento

- **Conversas por dia** (bar + linha de média móvel 7d): últimos 30 dias
- **Distribuição de tamanho** (histograma): nº de mensagens por conversa → revela funil
- **Taxa de identificação** (gauge 0–100%): conversas onde `user_name IS NOT NULL`
- **Tempo médio de resposta** (box plot por intent): segundos entre inbound → outbound
- **Tabela de conversas recentes** (10 últimas): phone mascarado, intent, nº msgs, started_at_sp

---

### Tab 3 — Intents & Sentimentos

- **Distribuição de intents** (donut): proporção de cada intent no período selecionado
- **Evolução semanal** (stacked bar): intents ao longo do tempo
- **Sentimento por intent** (grouped bar): positivo / neutro / negativo × intent
- Filtro de período (7d / 30d / tudo) no topo da tab

Intents mapeados:
| Intent | Descrição |
|--------|-----------|
| Quero Doar | Doação via PIX, transferência, roupas, alimentos |
| Busco Ajuda/Beneficiário | Usuário precisa de assistência |
| Voluntariado | Interesse em ser voluntário |
| Parceria Corporativa | Empresa buscando parceria |
| Informação Geral | Perguntas sobre as ONGs |
| Ambíguo | Mensagem sem intenção clara |
| **Fora do Escopo** | Uso indevido / guard-rail acionado |

---

### Tab 4 — ONGs Parceiras

- **Treemap categorias/subcategorias**: hierarquia visual das 52+ ONGs (`go.Treemap`)
- **ONGs por estado** (bar horizontal ordenado): concentração geográfica
- **Cobertura de PIX** (donut): ONGs com vs sem chave PIX
- **DataTable interativa** (filtros por estado/categoria): lista navegável de todas as ONGs

---

### Tab 5 — Guard-Rails & Segurança

- **Taxa "Fora do Escopo"** (linha diária): % de mensagens OOS / total outbound
- **Conversas bloqueadas estimadas** (bar): proxy para proteções acionadas
  - Conversas com alta concentração de inbound sem outbound → rate limit / bot / circuit breaker
- **Tabela de atividade suspeita**: conversas com razão inbound/outbound acima do threshold

---

## Queries Principais (`data/queries.py`)

Todas usam `AT TIME ZONE 'America/Sao_Paulo'` e aceitam parâmetro `days`.

```sql
-- KPI: conversas hoje
SELECT COUNT(DISTINCT id) FROM conversations
  WHERE started_at > NOW() - INTERVAL '1 day'

-- Heatmap de atividade (hora × dia da semana)
SELECT EXTRACT(DOW FROM created_at AT TIME ZONE 'America/Sao_Paulo') AS dow,
       EXTRACT(HOUR FROM created_at AT TIME ZONE 'America/Sao_Paulo') AS hour,
       COUNT(*) AS total
FROM messages GROUP BY dow, hour

-- Intent distribution (outbound = resposta do agente)
SELECT intent, COUNT(*) FROM messages
  WHERE direction = 'outbound' AND intent IS NOT NULL
  GROUP BY intent ORDER BY 2 DESC

-- Volume por hora (últimas 24h)
SELECT DATE_TRUNC('hour', created_at AT TIME ZONE 'America/Sao_Paulo') AS hora,
       direction, COUNT(*)
FROM messages WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY hora, direction ORDER BY hora

-- ONGs por estado
SELECT state, COUNT(*) FROM ongs
  WHERE is_active = true GROUP BY state ORDER BY 2 DESC

-- Tempo médio de resposta por intent
SELECT m1.intent,
       AVG(EXTRACT(EPOCH FROM (m2.created_at - m1.created_at))) AS avg_seconds
FROM messages m1
JOIN messages m2 ON m2.conversation_id = m1.conversation_id
  AND m2.direction = 'outbound' AND m2.created_at > m1.created_at
WHERE m1.direction = 'inbound'
GROUP BY m1.intent

-- Taxa de identificação
SELECT
  COUNT(*) FILTER (WHERE user_name IS NOT NULL) AS com_nome,
  COUNT(*) AS total
FROM conversations

-- Conversas por dia (últimos 30d)
SELECT DATE(started_at AT TIME ZONE 'America/Sao_Paulo') AS dia,
       COUNT(*) AS total
FROM conversations
WHERE started_at > NOW() - INTERVAL '30 days'
GROUP BY dia ORDER BY dia
```

---

## Segurança e Privacidade

- `DASHBOARD_USER` + `DASHBOARD_PASSWORD` como env vars no Render (BasicAuth via `dash-auth`)
- Phone numbers mascarados: `phone[:2] + "****" + phone[-4:]` antes de renderizar tabelas
- Queries de intent/sentimento/heatmap: aggregadas, sem PII
- Conexão ao banco: mesma `DATABASE_URL` do DoaZap (postgres superusuário, contorna RLS)

---

## Dependências (`requirements.txt`)

```
dash>=2.18.0
dash-bootstrap-components>=1.6.0
dash-auth>=2.3.0
plotly>=5.24.0
pandas>=2.2.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
flask-caching>=2.3.0
gunicorn>=22.0.0
python-dotenv>=1.0.0
```

---

## Variáveis de Ambiente (`.env.example`)

```env
DATABASE_URL=postgresql://postgres:...@pooler.supabase.com:5432/postgres
DASHBOARD_USER=admin
DASHBOARD_PASSWORD=senha-segura
CACHE_TTL=300
```

---

## Deploy no Render (novo Web Service free tier)

1. Criar novo **repositório GitHub** `doazap-dashboard` (público)
2. Push do código para `main`
3. Criar novo **Web Service** no Render:
   - Source: repositório `doazap-dashboard`
   - Root directory: `.` (raiz do repo)
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:server -b 0.0.0.0:$PORT`
   - Instance type: **Free**
4. Env vars: `DATABASE_URL`, `DASHBOARD_USER`, `DASHBOARD_PASSWORD`
5. URL resultante: `https://doazap-dashboard.onrender.com`

---

## README.md (conteúdo planejado)

O README cobrirá:
- Sobre o projeto (o que é, propósito, relação com DoaZap)
- Stack tecnológica (tabela)
- Screenshots / prévia do dashboard
- Pré-requisitos
- Como executar localmente
- Variáveis de ambiente (tabela completa)
- Estrutura do projeto
- Deploy em produção (Render)
- Changelog (link)
- Equipe (mesma do DoaZap)
- Licença MIT

---

## CHANGELOG.md (estrutura)

```
## [Unreleased]

## [1.0.0] - 2026-02-28
### Added
- Dashboard com 5 tabs: Visão Geral, Conversas, Intents, ONGs, Guard-Rails
- KPI cards com variação diária
- Heatmap de atividade (hora × dia da semana)
- Distribuição de intents e sentimentos
- Treemap de ONGs por categoria
- Guard-rails: taxa "Fora do Escopo" e atividade suspeita
- Autenticação via BasicAuth (dash-auth)
- Cache de 5 minutos (flask-caching)
- Deploy no Render (free tier)
```

---

## Verificação

```bash
# 1. Instalar e rodar localmente
cd doazap-dashboard
pip install -r requirements.txt
DATABASE_URL="..." DASHBOARD_USER=admin DASHBOARD_PASSWORD=admin python app.py
# Abrir http://localhost:8050

# 2. Confirmar queries no banco de produção
./doacao-whatsapp/scripts/psql-production.sh -c "
  SELECT intent, COUNT(*) FROM messages
  WHERE direction='outbound' GROUP BY intent ORDER BY 2 DESC;"

# 3. Após deploy: acessar https://doazap-dashboard.onrender.com
#    com as credenciais configuradas no Render
```

---

## Arquivos a Criar (todos novos)

| Arquivo | Descrição |
|---------|-----------|
| `.gitignore` | venv/, .env*, __pycache__/, *.pyc |
| `.env.example` | Template de variáveis de ambiente |
| `requirements.txt` | 10 dependências |
| `Dockerfile` | Python 3.13-slim, start com gunicorn |
| `Procfile` | `web: gunicorn app:server -b 0.0.0.0:$PORT` |
| `VERSION` | `1.0.0` |
| `config.py` | Leitura de env vars, engine SQLAlchemy, cache |
| `data/queries.py` | ~15 funções retornando DataFrames pandas via `pd.read_sql` |
| `components/kpis.py` | Componente `kpi_card(title, value, delta)` reutilizável |
| `components/charts/overview.py` | Heatmap (`go.Heatmap`) + timeline (`go.Scatter` com área) |
| `components/charts/conversations.py` | Histograma, box plot, gauge (`go.Indicator`), DataTable |
| `components/charts/intents.py` | Donut (`go.Pie`), stacked bar, grouped bar |
| `components/charts/ongs.py` | Treemap (`go.Treemap`), bar horizontal, DataTable |
| `components/charts/guardrails.py` | Linha OOS, bar de atividade suspeita |
| `app.py` | Dash app, BasicAuth, layout com DBC Tabs, callbacks de filtro global |
| `README.md` | Documentação completa do projeto |
| `CHANGELOG.md` | Histórico [1.0.0] |
