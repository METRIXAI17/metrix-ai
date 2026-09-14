# Сделать репозиторий приватным

Публичная витрина не должна светить ядро (промпты, OAE, lexicons, principle-graph).

## GitHub

1. Откройте https://github.com/METRIXAI17/metrix-ai/settings
2. Danger Zone → **Change repository visibility** → **Private**
3. Проверьте Collaborators: только операторы, которым нужен backend
4. Если в истории светились ключи — **ротируйте** токены (Telegram, Railway, Vercel, Tribute) и прогоните `git filter-repo` / BFG по `.env` и `*.pem`
5. Pages: если нужна публичная витрина — отдельный **public-only** репозиторий без `backend/core/prompts`

## Что не пушить

- `.env`, ключи, `*.pem`
- клиентские брифы (`backend/data/client_briefs/`, `backend/workspace/`)
- `pilot_private/`

См. корневой `.gitignore`.
