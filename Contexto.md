# Contexto do projeto Fofoqueiro

## Objetivo

O Fofoqueiro coleta notícias de portais do Amazonas por RSS, salva os itens no
PostgreSQL, evita duplicatas por link, gera um resumo diário e pode enviar esse
resumo para Telegram ou WhatsApp.

O projeto está em estágio de MVP funcional. O resumo atual é uma listagem de
manchetes e links agrupada por portal; ainda não existe sumarização do conteúdo
das notícias.

## Estado atual

### Implementado

- Coleta de múltiplas fontes RSS configuradas em `RSS_SOURCES`.
- Normalização de título, portal, link e data de publicação.
- Conversão das datas para o timezone configurado.
- Persistência em PostgreSQL.
- Deduplicação por URL usando restrição `UNIQUE`.
- Coleta agendada por intervalo em horas ou minutos.
- Resumo diário agendado para 18:00.
- Envio para Telegram, WhatsApp, ambos ou nenhum canal.
- Divisão de mensagens grandes para o Telegram.
- Suporte a múltiplos chats do Telegram.
- Endpoint WSGI simples em `/` e `/healthz`.
- Suíte inicial configurada com `pytest`.
- Testes unitários para entidade, datas, configuração, parser, coletor,
  repositório, sumarizador, notificadores, jobs e scheduler.
- Testes de configuração cobrem defaults, valores customizados, prioridade das
  URLs de banco, limpeza de espaços e valores numéricos inválidos.
- Testes de falhas cobrem feeds inválidos, fontes sem título ou data, isolamento
  de erro no coletor, falhas de commit, erros do Telegram e canais desconhecidos.

### Ainda não implementado ou incompleto

- Testes de integração com PostgreSQL e cobertura completa das camadas.
- Agendamento do resumo explicitamente vinculado ao timezone configurado.
- Isolamento completo de falhas por feed.
- Métricas detalhadas por ciclo.
- Fallback entre canais de notificação.
- Validação do corpo das respostas das APIs externas.
- Divisão de mensagens para WhatsApp.
- Extração de conteúdo das páginas das notícias.
- Resumo real por notícia e agrupamento por tema.
- Healthcheck que valide a conexão com o banco.
- Dockerfile da aplicação.
- Migrações versionadas do banco.
- Logs estruturados, retries e encerramento limpo.
- Alertas por e-mail quando a aplicação cair ou um ciclo crítico falhar.

A lista detalhada e priorizada deve ser mantida em `Afazeres.md`.

## Arquitetura

```text
src/
  app.py                         Entrada principal e endpoint WSGI
  config/
    settings.py                 Configuração por variáveis de ambiente
    logging.py                  Configuração de logs
  domain/
    entities.py                 Entidade NewsItem
  feeds/
    sources.py                  Lista de fontes configuradas
    parser.py                   Leitura e normalização de RSS
    collector.py                Coleta de várias fontes
  storage/
    database.py                 Conexão e inicialização do PostgreSQL
    repository.py               Persistência e consultas de notícias
  summarizer/
    daily_summary.py            Montagem do resumo diário
  notifiers/
    telegram.py                 Integração com Telegram
    whatsapp.py                 Integração com CallMeBot
    dispatcher.py                Seleção e despacho dos canais
  scheduler/
    jobs.py                     Jobs de coleta e envio
    cron.py                     Loop do scheduler
  utils/
    datetime_utils.py            Conversão de datas e timezones

scripts/
  run_once.py                   Uma coleta e um envio imediatos
  run_scheduler.py              Scheduler contínuo

tests/                          Testes unitários e de integração planejados
```

## Fluxo principal

1. `load_settings()` carrega `.env` e cria `Settings`.
2. A aplicação abre uma conexão PostgreSQL.
3. `init_postgres_db()` garante a tabela `news`.
4. O coletor consulta cada URL RSS.
5. O parser cria objetos `NewsItem`.
6. O repositório salva apenas links novos.
7. O job de resumo consulta as notícias recentes.
8. O sumarizador monta a mensagem.
9. O dispatcher envia para o canal configurado.

## Como executar

Instalar dependências:

```powershell
python -m pip install -r requirements.txt
```

Subir o PostgreSQL:

```powershell
docker compose up -d
```

Executar uma coleta e um resumo:

```powershell
python parse.py
```

Executar o scheduler:

```powershell
python scripts/run_scheduler.py
```

Executar testes:

```powershell
python -m pytest -q
```

## Configuração essencial

A configuração é carregada de `.env`. As variáveis principais são:

- `RSS_SOURCES`: URLs RSS separadas por vírgula.
- `POSTGRES_DSN` ou `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`,
  `POSTGRES_PASSWORD` e `POSTGRES_DB`.
- `FETCH_INTERVAL_HOURS` ou `FETCH_INTERVAL_MINUTES`.
- `MAX_NOTICIAS`.
- `TIMEZONE_NAME`, atualmente `America/Manaus` por padrão.
- `ENVIAR_PARA`: `telegram`, `whatsapp`, `ambos` ou `nenhum`.
- `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_IDS`.
- `WHATSAPP_PHONE` e `WHATSAPP_APIKEY`.

Nunca registrar tokens, chaves ou senhas em logs, commits ou documentação.

## Decisões e cuidados

- O banco atual é PostgreSQL; SQLite não faz parte do fluxo atual.
- O banco isolado `fofoqueiro_test` foi criado no mesmo cluster PostgreSQL para
  os testes de integração e já está configurado no `.env` local.
- A configuração dos testes usa `TEST_POSTGRES_DSN` e valida que o banco alvo
  seja exatamente `fofoqueiro_test`; sem essa variável, os testes são ignorados.
- A deduplicação é feita pelo campo `link`.
- A integração de WhatsApp usa CallMeBot e deve ser tratada como dependência
  externa substituível.
- A decisão atual é não adicionar novas funcionalidades ou testes de WhatsApp;
  essa integração poderá ser removida no futuro.
- Alertas por e-mail são uma melhoria futura, ainda não implementada. Devem
  usar SMTP ou um provedor externo, com cooldown, agrupamento de falhas e aviso
  de recuperação para evitar excesso de mensagens.
- Mudanças devem preservar a tolerância a feeds individuais e não interromper o
  ciclo completo por causa de uma única fonte.
- Antes de alterar uma camada, verificar os testes e os contratos das camadas
  relacionadas.
- Todas as mensagens de commit devem ser escritas em inglês.

## Estado da última análise

- A arquitetura do MVP foi revisada.
- `Afazeres.md` foi reorganizado em prioridades, evolução do produto e componentes
  ainda inexistentes.
- `pytest` foi adicionado às dependências e configurado em `pytest.ini`.
- Os testes placeholder foram substituídos nos arquivos de coletor, repositório e
  sumarizador.
- Foram adicionados testes para entidade, datas, configuração e entradas RSS sem
  link.
- O coletor agora isola falhas individuais de fontes RSS, registra a URL com
  erro e continua processando as demais fontes.
- Foram adicionados testes para feeds inválidos, dados incompletos, falhas de
  banco e comportamentos de erro do Telegram.
- Foram adicionados testes dos jobs de coleta/resumo e do registro do scheduler,
  sem rede, banco real ou espera do relógio.
- A configuração foi testada para defaults, entradas customizadas, prioridade de
  banco, limpeza de espaços e valores numéricos inválidos.
- O banco PostgreSQL `fofoqueiro_test` foi criado e a conexão foi validada com a
  role `fofoqueiro`; nenhuma credencial foi adicionada ao repositório.
- Foram criados três testes de integração do repositório para inserção,
  deduplicação e consultas por data/horas.
- O `.env` local foi alinhado ao cluster existente: role `fofoqueiro`, banco
  `FOFOQUEIRO-AM` para a aplicação e `fofoqueiro_test` para a integração.
- A suíte de integração passou com `3 passed` e a suíte completa com `46 passed`;
  um aviso de depreciação veio de um plugin externo.
- `pytest-cov` foi adicionado às dependências.
- A cobertura unitária foi medida com `43 passed` e resultado total de `74%`.
- O relatório apontou lacunas em `src/app.py`, `src/config/logging.py`,
  `src/storage/database.py`, caminhos de notificação e alguns ramos menores.
- A execução conjunta de cobertura com os testes de integração travou no ambiente;
  os três testes de integração continuam passando sem cobertura.
- O próximo passo recomendado é cobrir as lacunas que representem risco real,
  começando pela conexão/inicialização do banco e pelo healthcheck.

## Regra de manutenção

Ao concluir uma tarefa:

1. Atualizar `Afazeres.md`, marcando o item concluído e reorganizando prioridades.
2. Atualizar este arquivo quando houver mudança de arquitetura, configuração,
   comportamento, comandos, decisões ou estado relevante.
3. Registrar no contexto quais testes foram executados e o resultado.
4. Manter os dois arquivos consistentes com o código real; não documentar planos
   como se fossem funcionalidades implementadas.
