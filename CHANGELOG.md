# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adota o [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.5] - 2026-02-28

### Changed
- **Tema visual**: CYBORG → **SLATE** (dark cinza-azulado; mesmo suporte a cores hardcoded dos gráficos)
- **Gauge "Taxa de Identificação"**: fontes reduzidas para garantir não-sobreposição em qualquer tema
  (`number.font.size` 26 → 22, `delta.font.size` 14 → 12, `height` 300 → 320 px)

## [1.0.4] - 2026-02-28

### Removed
- **Gráfico "Cobertura de Chave PIX"**: donut removido da Tab ONGs (dados disponíveis
  na DataTable interativa via coluna "PIX"); espaço lateral ocupado apenas pelas barras
  de ONGs por estado

## [1.0.3] - 2026-02-28

### Fixed
- **Gauge "Taxa de Identificação" com sobreposição**: removido `domain` ineficaz; reduzidos
  `number.font.size` de 36 → 26 e `delta.font.size` → 14 para caber no espaço interno do arco
  sem sobreposição ao semicírculo

## [1.0.2] - 2026-02-28

### Fixed
- **Treemap de ONGs em branco**: reconstrução da hierarquia com IDs compostos (`cat::X`,
  `sub::cat::X`, `ong::X`) para evitar colisão entre subcategorias de nomes iguais em
  categorias distintas (ex.: "Geral" em 7 categorias); corrigido `branchvalues="total"` →
  `branchvalues="remainder"` que causava falha silenciosa quando `value[pai] < Σvalue[filhos]`
- **Tabela "Atividade Suspeita" vazia**: corrigido bug de precedência no `HAVING` (faltavam
  parênteses entre `AND` e `OR`); threshold reduzido de 0.80 para 0.55 para capturar
  conversas com proporção elevada de mensagens inbound (padrão de bot/rate-limit)

## [1.0.1] - 2026-02-28

### Fixed
- **Sobreposição legenda × título** em todos os gráficos com múltiplas séries: margem superior
  aumentada de 40 px para 70 px (`t=70`) e legendas horizontais reposicionadas com
  `yanchor="bottom", y=1.02` para renderizarem abaixo do título sem colisão
- **Gauge de Taxa de Identificação** desalinhado: adicionado `domain={"x": [0,1], "y": [0.15,1]}`
  no `go.Indicator` para reservar espaço para o valor numérico e delta abaixo do arco

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
