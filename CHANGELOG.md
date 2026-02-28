# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adota o [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-02-28

### Added
- **Dashboard com 5 tabs** construído com Plotly Dash 2.x e Dash Bootstrap Components (tema CYBORG)
- **KPI cards com delta diário**: Conversas Hoje, Mensagens Hoje, Usuários Únicos, Intent do Dia
  — cada card exibe variação % em relação ao dia anterior
- **Tab 1 — Visão Geral**:
  - Heatmap de atividade (hora × dia da semana) revelando padrões de uso
  - Volume de mensagens por hora nas últimas 24h (inbound/outbound)
- **Tab 2 — Conversas & Engajamento**:
  - Conversas por dia (barras + média móvel 7 dias)
  - Histograma de tamanho de conversa (mensagens por sessão)
  - Gauge de taxa de identificação (usuários com nome coletado)
  - Box plot de tempo de resposta por intent
  - Tabela de conversas recentes (phone mascarado)
- **Tab 3 — Intents & Sentimentos**:
  - Donut chart de distribuição de intents com filtro de período (7d / 30d / tudo)
  - Stacked bar semanal de evolução de intents
  - Grouped bar de sentimento por intent (positivo / neutro / negativo)
- **Tab 4 — ONGs Parceiras**:
  - Treemap hierárquico (categoria → subcategoria → ONG)
  - Barras horizontais de ONGs ativas por estado
  - Donut de cobertura de chave PIX
  - DataTable interativa com filtro e ordenação nativos
- **Tab 5 — Guard-Rails & Segurança**:
  - Linha diária da taxa "Fora do Escopo" com filtro de período
  - Barras de eventos de guard-rail por dia (conversas sem resposta × OOS detectado)
  - Tabela de conversas suspeitas (alta proporção de inbound sem outbound)
- **Autenticação** via BasicAuth (`dash-auth`) com credenciais por variável de ambiente
- **Cache** de 5 minutos (`flask-caching` SimpleCache) para reduzir carga no banco
- **Auto-refresh** a cada 5 minutos via `dcc.Interval`
- **Privacidade**: números de telefone mascarados em todas as tabelas (`****1234`)
- Todos os timestamps exibidos em horário de São Paulo (UTC-3)
