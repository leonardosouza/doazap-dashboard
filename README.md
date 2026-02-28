# DoaZap Dashboard

Dashboard analítico do [DoaZap](https://github.com/leonardosouza/doacao-whatsapp) — bot WhatsApp de doações sociais. Transforma dados operacionais do banco de produção em visualizações interativas para a equipe e stakeholders.

## Sobre o Projeto

O DoaZap Dashboard conecta ao mesmo banco de dados PostgreSQL (Supabase) do bot DoaZap e oferece cinco visões analíticas:

| Tab | Conteúdo |
|-----|----------|
| **Visão Geral** | KPIs com delta diário, heatmap de atividade hora × dia, volume 24h |
| **Conversas** | Volume diário, tamanho de sessão, taxa de identificação, tempo de resposta |
| **Intents** | Distribuição, evolução semanal, sentimento por intent |
| **ONGs** | Treemap de categorias, distribuição geográfica, cobertura PIX |
| **Guard-Rails** | Taxa "Fora do Escopo", eventos de proteção, atividade suspeita |

## Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| Framework | [Plotly Dash](https://dash.plotly.com/) 2.x |
| UI | Dash Bootstrap Components (tema CYBORG) |
| Autenticação | dash-auth (Basic Auth) |
| Dados | pandas + SQLAlchemy + psycopg2 |
| Cache | flask-caching (SimpleCache, TTL 5 min) |
| Banco | PostgreSQL (Supabase) — mesmo do DoaZap |
| Deploy | Render (Web Service free tier) |
| Servidor | gunicorn |

## Pré-requisitos

- Python 3.10+
- Acesso ao banco de produção Supabase (variável `DATABASE_URL`)

## Como Executar Localmente

### Com Docker (recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/leonardosouza/doazap-dashboard.git
cd doazap-dashboard

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com DATABASE_URL, DASHBOARD_USER e DASHBOARD_PASSWORD

# 3. Suba o container
docker compose up -d

# Acesse: http://localhost:8050
```

### Sem Docker

```bash
# 1. Clone o repositório
git clone https://github.com/leonardosouza/doazap-dashboard.git
cd doazap-dashboard

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com DATABASE_URL, DASHBOARD_USER e DASHBOARD_PASSWORD

# 5. Execute
python app.py
# Acesse: http://localhost:8050
```

## Variáveis de Ambiente

| Variável | Descrição | Obrigatória | Default |
|----------|-----------|:-----------:|---------|
| `DATABASE_URL` | URL de conexão PostgreSQL (Supabase) | Sim | — |
| `DASHBOARD_USER` | Usuário para autenticação Basic Auth | Não | `admin` |
| `DASHBOARD_PASSWORD` | Senha para autenticação Basic Auth | Sim | — |
| `CACHE_TTL` | TTL do cache em segundos | Não | `300` |

## Estrutura do Projeto

```
doazap-dashboard/
├── app.py                      # Entry point: Dash app, auth, layout e callbacks
├── config.py                   # Engine SQLAlchemy, cache e credenciais
├── data/
│   └── queries.py              # Queries SQL analíticas → DataFrames pandas
├── components/
│   ├── kpis.py                 # Componente KPI card reutilizável
│   └── charts/
│       ├── overview.py         # Heatmap + timeline 24h
│       ├── conversations.py    # Funil de conversas e engajamento
│       ├── intents.py          # Distribuição e evolução de intents
│       ├── ongs.py             # Treemap e mapa geográfico de ONGs
│       └── guardrails.py       # Métricas de segurança e guard-rails
├── VERSION                     # Versão atual (semver)
├── CHANGELOG.md                # Histórico de versões
├── requirements.txt
├── Dockerfile
├── Procfile                    # Start command para Render
└── .env.example                # Template de variáveis de ambiente
```

## Privacidade

Números de telefone são mascarados em todas as tabelas (`55****1234`). Queries de heatmap, intents e sentimentos são sempre agregadas e não expõem dados individuais.

## Deploy em Produção

O dashboard está hospedado no [Render](https://render.com/) como Web Service free tier:

| Configuração | Valor |
|-------------|-------|
| URL | <https://doazap-dashboard.onrender.com> |
| Runtime | Docker (Dockerfile na raiz) |
| Region | Oregon (US West) |
| Env vars | `DATABASE_URL`, `DASHBOARD_USER`, `DASHBOARD_PASSWORD`, `CACHE_TTL` |

> **Nota:** o free tier do Render hiberna após 15 min de inatividade. O primeiro acesso após inatividade
> pode demorar ~30 segundos para o container inicializar.

## Versionamento

Novas funcionalidades recebem bump de versão em `VERSION` e entrada em `CHANGELOG.md`, seguidos de tag `vX.Y.Z` no git.

## Projeto Principal

Este dashboard é complementar ao [DoaZap](https://github.com/leonardosouza/doacao-whatsapp) — bot WhatsApp de conexão entre doadores e ONGs parceiras, desenvolvido pelo Grupo 02 do MBA em Engenharia de Software — [Faculdade Impacta](https://www.impacta.edu.br/).

## Licença

MIT
