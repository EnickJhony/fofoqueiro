# Fofoqueiro enunciado

preciso de uma aplicação que faça as seguintes coisas:

- Pegue notícia de portais de notícia da regiao via rss
- Os portais são de uma lista que vou colocar em uma lista
- Precisa de uma cron para fazer essa busca a cada x horas
- Salve essas informações em um banco de dados
- Gere um resumo das notícias do dia
- Envie esse resumo para um Telegram ou Whatsapp.

Stacks que vamos usar:

- Python

Estrutura proposta:

src/
app.py
config/
settings.py
logging.py
domain/
entities.py
schemas.py
feeds/
sources.py
parser.py
collector.py
storage/
database.py
models.py
repository.py
summarizer/
daily_summary.py
notifiers/
base.py
telegram.py
whatsapp.py
dispatcher.py
scheduler/
jobs.py
cron.py
utils/
datetime_utils.py
text_utils.py

tests/
test_feeds_parser.py
test_collector.py
test_summary.py
test_notifiers.py
test_repository.py

scripts/
run_once.py
run_scheduler.py

Funcoes:

1) feeds
- Lista de portais RSS em sources.py.
- Leitura e normalização de feeds em parser.py.
- Orquestração de coleta de vários portais em collector.py.
2) storage
- Conexão do banco em database.py.
- Tabelas/ORM em models.py.
- Operações de salvar/buscar notícia em repository.py.
3) summarizer
- Geração de resumo diário em daily_summary.py.
- Pode começar com resumo simples por regra e depois evoluir para IA.
4) notifiers
- Implementação de envio Telegram em telegram.py.
- Implementação de envio WhatsApp em whatsapp.py.
- dispatcher.py decide para qual canal enviar (telegram, whatsapp, ambos).
5) scheduler
- jobs.py define os jobs: coletar notícias e enviar resumo diário.
- cron.py configura execução a cada X horas.
6) config
- settings.py lê variáveis de ambiente.
- logging.py centraliza logs.
7) app.py
- Ponto de entrada: sobe scheduler e inicializa dependências.

Passos futuros:

1) Definir banco e esquema inicial
- Escolha SQLite para começar (rápido) ou PostgreSQL (produção).
- Campos mínimos de notícia: id, portal, titulo, link, publicado_em, conteudo_resumo, coletado_em.
- Criar regra de unicidade por link para evitar duplicados.
2) Criar a camada de configuração
- Centralizar .env em settings.py.
- Variáveis: RSS_SOURCES, DB_URL, FETCH_INTERVAL_HOURS, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, WHATSAPP_PROVIDER, WHATSAPP_CREDENTIALS.
3) Implementar coleta multi-portal
- Mover lista de feeds para feeds/sources.py.
- Fazer parser genérico para cada feed.
- Normalizar datas para timezone local.
4) Persistir no banco
- Criar storage/models.py e storage/repository.py.
- Salvar apenas notícias novas.
5) Criar job de coleta
- Em scheduler/jobs.py, job collect_news_job roda a cada X horas.
- Logar quantas notícias foram lidas e quantas novas foram salvas.
6) Criar resumo diário
- Em summarizer/daily_summary.py, buscar notícias do dia.
- Gerar texto compacto por portal ou por tema.
- Definir horário fixo para envio, por exemplo 18:00.
7) Criar envio de mensagens
- Telegram funcionando via bot.
- WhatsApp: decidir provedor (CallMeBot, Twilio ou API oficial).
- Implementar fallback: se um canal falhar, tentar outro.
8) Orquestrar envio
- notifiers/dispatcher.py escolhe canal conforme configuração.
- Formatar mensagem com limite de tamanho por canal.
9) Testes mínimos
- Parser de RSS.
- Deduplicação no repository.
- Montagem de resumo diário.
- Simulação de envio sem chamar API real.
10) Operação e observabilidade
- Logs de execução por job.
- Tratamento de erro por feed (não parar o ciclo inteiro).
- Métrica simples: total coletado, total novo, total enviado.
11) Documentar execução
- Atualizar README com:
- Como configurar .env
- Como rodar uma vez (scripts/run_once.py)
- Como iniciar scheduler (scripts/run_scheduler.py)
