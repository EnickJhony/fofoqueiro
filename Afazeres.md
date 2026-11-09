# Afazeres do Fofoqueiro

## Status atual

O projeto já possui um MVP funcional: coleta notícias via RSS, salva no PostgreSQL,
evita duplicatas por link, executa coletas agendadas e envia um resumo básico para
Telegram ou WhatsApp.

O resumo atual ainda é uma lista de manchetes e links agrupada por portal; ele não
resume o conteúdo das notícias.

### Concluído nesta etapa

- Dependência `pytest` adicionada ao `requirements.txt`.
- Configuração de descoberta criada em `pytest.ini`.
- Testes placeholder substituídos por testes reais de coletor, repositório e
  sumarizador.
- Testes adicionados para entidade `NewsItem`, conversão de datas e configuração.
- Testes de configuração ampliados para valores inválidos, defaults, limpeza de
  espaços e prioridade das URLs de banco.
- Testes do parser ampliados para feeds inválidos, títulos ausentes, datas
  ausentes e entradas sem link.
- Coletor protegido contra falha isolada de uma fonte, com log da URL afetada.
- Testes adicionados para falhas de banco, erros e credenciais ausentes do
  Telegram e canais de envio desconhecidos.
- Testes adicionados para os jobs de coleta/resumo e para o registro do scheduler.
- Suíte validada com `43 passed`.

## Prioridade imediata

### 1. Expandir a cobertura de testes

- Cobrir deduplicação e falhas de notificação adicionais.
- Adicionar testes de integração do repositório com PostgreSQL isolado.
- Adicionar relatório de cobertura.
- Executar os testes antes de cada mudança relevante.

### 2. Corrigir o agendamento por timezone

- Garantir que o resumo seja enviado às 18:00 no timezone configurado em
  `TIMEZONE_NAME`, independentemente do timezone do servidor.
- Manter a coleta no intervalo configurado em horas ou minutos.
- Adicionar um teste para validar o horário calculado.

### 3. Isolar falhas por feed

- Uma fonte RSS indisponível não deve interromper a coleta das demais.
- Registrar no log qual fonte falhou e o motivo.
- Registrar métricas por ciclo: fontes consultadas, fontes com erro, notícias lidas
  e notícias novas salvas.
- Definir timeout e comportamento para feeds lentos ou inválidos.

### 4. Fortalecer os canais de notificação

- Validar o corpo das respostas da API do Telegram, além do status HTTP.
- Implementar fallback entre canais quando `ENVIAR_PARA=ambos` e um canal falhar.
- Definir claramente no log se o envio foi total, parcial ou falhou.
- Implementar divisão de mensagens também para o WhatsApp, respeitando o limite
  do provedor escolhido.
- Evitar que credenciais apareçam em logs ou mensagens de erro.

## Próxima evolução do produto

### 5. Transformar a listagem em resumo de verdade

- Buscar o conteúdo ou descrição disponível de cada notícia.
- Gerar um resumo curto por notícia.
- Agrupar notícias por tema ou assunto.
- Ordenar por relevância, evitando excesso de manchetes repetidas.
- Manter links para leitura completa.
- Definir um limite de tamanho por resumo diário.
- Começar com regras simples e deixar a integração com IA para uma etapa posterior.

### 6. Melhorar o modelo de dados

- Avaliar campos para descrição, conteúdo resumido, autor, categoria e imagem.
- Registrar o horário efetivo da coleta e do envio.
- Considerar uma chave de deduplicação mais robusta quando portais alterarem URLs.
- Adicionar índices para consultas por data, portal e link.

### 7. Alinhar configuração e documentação

- Decidir se o nome oficial da conexão será `DATABASE_URL` ou
  `POSTGRES_DSN/POSTGRES_*`.
- Documentar todas as variáveis do `.env.example`.
- Explicar a diferença entre execução única e scheduler.
- Documentar a configuração do Telegram e do provedor de WhatsApp.
- Documentar como iniciar o PostgreSQL com Docker Compose.

### 8. Melhorar a operação em produção

- Criar uma imagem Docker da aplicação ou um serviço de execução.
- Adicionar healthcheck real para verificar a aplicação e a conexão com o banco.
- Enviar um alerta por e-mail quando a aplicação cair ou um ciclo crítico falhar.
- Definir quais erros disparam o alerta, evitando uma mensagem para cada falha
  repetida.
- Adicionar cooldown, agrupamento e informação sobre recuperação do serviço.
- Definir política de reinício e encerramento limpo.
- Estruturar logs para facilitar busca e monitoramento.
- Adicionar métricas simples de coleta, persistência e envio.
- Evitar que o scheduler dependa do timezone global do sistema.

## Melhorias arquiteturais opcionais

Estas mudanças só devem ser feitas se trouxerem benefício real, sem aumentar a
complexidade do MVP:

- Criar `schemas.py` para contratos de entrada e saída.
- Criar `models.py` caso seja adotado um ORM.
- Criar uma interface base para notificadores.
- Extrair utilitários de texto e divisão de mensagens.
- Adicionar suporte a SQLite apenas se for necessário para desenvolvimento local.

## Componentes ainda inexistentes

Os itens abaixo foram previstos na arquitetura inicial ou mencionados na
avaliação, mas ainda não existem de forma completa no projeto:

### Estrutura de domínio e persistência

- Criar `src/domain/schemas.py` para definir contratos e validações dos dados.
- Criar `src/storage/models.py` se o projeto adotar um ORM.
- Criar migrações versionadas do banco em vez de depender apenas de
  `CREATE TABLE IF NOT EXISTS`.
- Adicionar uma camada de abstração para permitir testes do repositório sem
  depender de um PostgreSQL real.

### Notificadores

- Criar `src/notifiers/base.py` com uma interface comum para os canais.
- Criar uma estratégia genérica para dividir mensagens por limite de cada canal.
- Implementar fallback configurável entre Telegram e WhatsApp.
- Tratar resultados parciais quando houver vários chats ou canais.
- Adicionar retries controlados e timeout por notificador.

### Conteúdo e resumo

- Criar `src/utils/text_utils.py` para limpeza, normalização e truncamento de
  textos.
- Armazenar descrição ou conteúdo extraído do RSS.
- Criar um extrator de conteúdo quando o feed fornecer apenas a manchete.
- Criar uma etapa de sumarização por notícia.
- Criar uma etapa de agrupamento por tema e remoção de notícias repetidas.
- Definir uma interface para trocar o resumo baseado em regras por um provedor
  de IA no futuro.

### Observabilidade e operação

- Criar métricas persistentes ou exportáveis de coleta, deduplicação, resumo e
  envio.
- Criar logs estruturados com identificador por execução.
- Criar healthcheck que valide também a conexão com o banco.
- Criar um notificador de e-mail para alertas de indisponibilidade e falhas
  críticas.
- Adicionar configuração segura de SMTP ou de um provedor de e-mail.
- Testar o envio de alerta sem usar um servidor SMTP real.
- Criar encerramento limpo do scheduler e fechamento da conexão PostgreSQL.
- Criar `Dockerfile` para executar a aplicação junto ao `compose.yaml`.
- Definir uma estratégia de retry para banco, RSS e APIs externas.
- Criar alertas ou notificações administrativas quando ciclos importantes falharem.

### Qualidade e segurança

- Adicionar testes de integração com PostgreSQL isolado.
- Adicionar testes dos jobs do scheduler sem esperar pelo relógio real.
- Adicionar testes dos limites e respostas inválidas das APIs externas.
- Validar todas as configurações obrigatórias no início da aplicação.
- Garantir que tokens, chaves e senhas nunca sejam exibidos nos logs.
- Adicionar lint, formatação e verificação de tipos ao fluxo de desenvolvimento.