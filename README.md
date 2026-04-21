# Fofoqueiro

Projeto para pegar informações de blogs do amazonas e faz um resumo do dia

## Ambiente virtual no Windows

Não precisa criar um arquivo `.env` para a API funcionar.
O que pode ser útil é criar um ambiente virtual Python, por exemplo com `.venv`:

```bash
python -m venv .venv
```
```
.venv\Scripts\activate.bat
```

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Configuração

1. Copie `.env.example` para `.env`.
2. Ajuste os feeds em `RSS_SOURCES`.
3. Configure `ENVIAR_PARA` como `telegram`, `whatsapp`, `ambos` ou `nenhum`.
4. Preencha credenciais do canal escolhido.
5. Por padrao, o projeto grava no SQLite (`SQLITE_ENABLED=true` e `DB_PATH`).
6. Para gravar tambem no PostgreSQL, ative `POSTGRES_ENABLED=true` e preencha as variaveis `POSTGRES_*`.
7. Para rodar somente com PostgreSQL (ex.: Railway), use `SQLITE_ENABLED=false` e `POSTGRES_ENABLED=true`.
8. Para testes mais rapidos do scheduler, defina `FETCH_INTERVAL_MINUTES=10` (com `0`, ele usa `FETCH_INTERVAL_HOURS`).

## Banco PostgreSQL com Docker Compose

O `compose.yaml` está configurado para carregar credenciais do `.env`. Subir o PostgreSQL local:

```bash
docker compose up -d
```

O Docker Compose lerá automaticamente as variáveis `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` e `POSTGRES_PORT` do seu arquivo `.env`.

Com o PostgreSQL ativo e `POSTGRES_ENABLED=true`, cada coleta passa a cadastrar as noticias no SQLite e no PostgreSQL.

Para ambiente de producao com filesystem efemero, como Railway, prefira `SQLITE_ENABLED=false` para usar apenas PostgreSQL.

## Estrutura do projeto

```text
src/
	app.py
	config/
	domain/
	feeds/
	storage/
	summarizer/
	notifiers/
	scheduler/
	utils/
scripts/
	run_once.py
	run_scheduler.py
```

## Como executar

Executar uma coleta + resumo imediatamente:

```bash
python parse.py
```

Executar modo scheduler (coleta a cada X horas + resumo diario 18:00):

```bash
python scripts/run_scheduler.py
```