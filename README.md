# Ether3D News

Automacao sem VPS, sem n8n e sem chave de IA que coleta noticias de impressao 3D, remove repeticoes, seleciona por regras editoriais, traduz automaticamente para pt-BR e envia quatro noticias por dia para um chat privado no Telegram.

## Fontes

- All3DP
- Fabbaloo
- 3D Printing Industry
- Tom's Hardware — 3D Printing
- Creative Bloq — 3D Printing

Uma fonte temporariamente indisponivel nao interrompe as demais. O sistema considera itens dos ultimos 10 dias, normaliza URLs, ignora links ja enviados e limita a selecao a 35 candidatos recentes.

## Como funciona

1. O GitHub Actions inicia diariamente as 08:00 no horario de Brasilia (11:00 UTC).
2. Os feeds RSS das cinco fontes sao consultados.
3. URLs duplicadas, antigas ou presentes em `data/history.json` sao removidas.
4. Regras de palavras-chave selecionam ate quatro noticias relevantes e um tradutor publico sem chave converte titulo e trecho para pt-BR.
5. Cada noticia e enviada separadamente pelo Telegram Bot API.
6. O workflow grava os itens enviados no historico e faz commit automatico.

O agendamento do GitHub pode sofrer alguns minutos de atraso em horarios de alta demanda. A execucao manual fica disponivel em **Actions > Ether3D News > Run workflow**.

## Configuracao

### 1. Criar o bot e descobrir o chat ID

1. No Telegram, converse com `@BotFather`, execute `/newbot` e guarde o token.
2. Abra uma conversa privada com o novo bot e envie qualquer mensagem, como `Oi`.
3. No navegador, acesse `https://api.telegram.org/botSEU_TOKEN/getUpdates`.
4. No JSON retornado, copie o numero em `message.chat.id`. Esse e o `TELEGRAM_CHAT_ID`.

Nunca salve o token ou o chat ID diretamente no repositorio.

### 2. Criar os secrets no GitHub

No repositorio, abra **Settings > Secrets and variables > Actions > New repository secret** e crie:

| Secret | Valor |
|---|---|
| `TELEGRAM_BOT_TOKEN` | token fornecido pelo BotFather |
| `TELEGRAM_CHAT_ID` | ID numerico do chat privado |

### 3. Permitir o commit do historico

Em **Settings > Actions > General > Workflow permissions**, selecione **Read and write permissions**. Em repositorios com branch protegida, permita que GitHub Actions grave na branch ou use uma branch sem essa restricao.

### 4. Ativar e testar

Envie estes arquivos para a branch padrao do GitHub. Abra **Actions**, selecione **Ether3D News**, clique em **Run workflow** e acompanhe a primeira execucao. Se funcionar, o agendamento diario ja estara ativo.

## Execucao local opcional

Requer Python 3.11 ou mais recente. Crie um ambiente virtual, instale `requirements.txt`, defina as tres variaveis do arquivo `.env.example` no seu terminal e execute:

```bash
python -m ether3d_news.main
```

O programa nao carrega `.env` automaticamente para evitar surpresas; o arquivo serve apenas como referencia. Para rodar os testes:

```bash
pip install -r requirements-dev.txt
pytest
```

## Ajustes comuns

- Horario: altere o `cron` em `.github/workflows/ether3d-news.yml` (sempre em UTC).
- Quantidade, idade maxima e limite de candidatos: altere os valores em `Settings`, em `ether3d_news/config.py`.
- Criterios de relevancia: ajuste `KEYWORDS` e `NEGATIVE_KEYWORDS`, em `ether3d_news/selector.py`.
- Fontes: edite `SOURCES` no mesmo arquivo.
- Historico: os 1.000 envios mais recentes sao mantidos, evitando crescimento ilimitado.

## Seguranca e custos

O token do Telegram entra somente como secret durante a execucao e o workflow nao registra seu valor. Nao ha chamada paga de IA. A traducao usa o endpoint publico do Google Translate por meio da biblioteca `deep-translator`, sem chave e sem garantia formal de disponibilidade; se ele estiver temporariamente indisponivel, a automacao envia o texto original em vez de parar.
