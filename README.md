**Focus Bot — Pomodoro & Streaks**

Uma implementação organizada de um bot de foco (Telegram) com suporte a sessões de foco, pausas, cálculo de streaks e métricas diárias.

**Project Overview**
- **Purpose**: Automatizar sessões de produtividade (Pomodoro-like), fornecer estatísticas e manter streaks diários.
- **Scope**: Bot Telegram, camada de persistência (SQLite / PostgreSQL), API para webhooks (FastAPI) e um runner de desenvolvimento em polling.

**Architecture**
- **Entry**: [main.py](main.py#L1) — FastAPI app, webhook endpoint e ciclo de vida (startup/shutdown).
- **Bot wiring**: [bot.py](bot.py#L1) — constrói `Application` do `python-telegram-bot` e regista handlers.
- **Config**: [config.py](config.py#L1) — validação de variáveis de ambiente e `Settings` central.
- **Database**: [database/migrations.py](database/migrations.py#L1) — criação de schema e índices; [database/connection.py](database/connection.py#L1) — pool/conn management.
- **Handlers**: `handlers/` — comandos e callbacks (start, foco, pausa, settings, stats).
- **Services**: `services/` — lógica de negócio (sessões, streaks, sweep jobs, async DB offload).
- **Utils**: `utils/` — helpers (formatting, keyboards, time helpers).
- **Tests**: `tests/` — testes unitários e fixtures (pytest).

**Quick Start — Development (polling)**
- Requisitos: Python 3.12+, `venv` recomendado.

Steps:
```powershell
# abrir PowerShell na pasta do projeto
Set-Location 'C:\Users\silla\PROJETOS\BOT DC\focus-bot'
# ativar venv (se existir)
.\venv\Scripts\Activate.ps1
# instalar dependências
pip install -r requirements.txt
# opcional: limpar webhook caso exista
python -c "from dotenv import load_dotenv, find_dotenv; import os; load_dotenv(find_dotenv()); from telegram import Bot; Bot(os.getenv('BOT_TOKEN')).delete_webhook(); print('webhook deleted')"
# correr em polling (desenvolvimento)
python run_polling.py
```

**Run with Webhook (production / testing with ngrok)**
- Defina `WEBHOOK_URL` público (ex.: `https://<your-domain>` ou URL do ngrok) no `.env`.
- Run the API server with Uvicorn (from `focus-bot` folder):
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- A app vai registar o webhook automaticamente durante o `lifespan`.

**Configuration**
- Copiar `.env.example` → `.env` e preencher as variáveis:
  - `BOT_TOKEN` — token do seu bot Telegram
  - `WEBHOOK_URL` — URL pública para webhooks (ou mantenha como placeholder se usar polling)
  - `WEBHOOK_SECRET` — segredo para validar webhooks
  - `DATABASE_URL` — `sqlite:///focus_bot.db` para dev, ou string PostgreSQL para produção

**Database & Migrations**
- As tabelas são criadas automaticamente em startup via `run_migrations()`; para produção, utilize um fluxo de migrações mais robusto (Alembic) se preferir.

**Testing**
- Executar testes com pytest:
```powershell
pytest -q
```

**Deployment**
- Exemplo `systemd` unit: [deploy/focus-bot.service](deploy/focus-bot.service#L1)
- Produção: execute `uvicorn main:app` atrás de um reverse proxy (nginx) e garanta `DATABASE_URL` apontando para PostgreSQL.

**Development notes & conventions**
- A arquitetura separa `handlers` (interface) → `services` (business logic) → `database` (persistência).
- Valores default e mensagens estão em `constants.py`.
- `run_polling.py` é para desenvolvimento local; não use polling em produção.

**Contributing**
- Fork → branch feature → PR com descrição e testes.

**License**
- (Coloque aqui a licença do seu projeto, ex.: MIT)

---

Se queres, adiciono:
- Badges e um `CHANGELOG.md`.
- Template de `docker-compose` para PostgreSQL + app.
- Integração com Alembic para migrações formais.
