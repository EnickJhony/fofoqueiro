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