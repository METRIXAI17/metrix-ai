# Локальная оценка + приватные комнаты

## Система оценки (`scripts/local_eval_suite.py`)

| Ось | Вес | Что меряет |
|-----|-----|------------|
| tests | 30% | pytest |
| deep_tech | 20% | circle surfaces + assertions |
| free_work | 15% | start / clarify / advance |
| niche_coverage | 15% | 6×3 answer packs + founders lane |
| private_rooms | 20% | mint link/password + unlock |

Отчёт: `docs/LOCAL_EVAL_REPORT.json`

Последний прогон: **100 / 100 · Grade A** · 73 tests green.

## Исправления по недочётам

- `pipeline_version` assertion обновлён (2.4-circle-system)
- Private rooms: hash пароля, wrong password reject, deploy mirror
- Welcome + workspace HTML, mint API

## Приватный деплой

```powershell
cd Desktop\metrix-ai
py -3 -m pilot_private.main
py -3 scripts\deploy_private_room.py --name "Имя клиента" --industry ai-agencies --lang ru --base-url http://127.0.0.1:8790
```

Клиенту: уникальная ссылка `/w/{slug}` + пароль.  
Возврат в среду: та же ссылка → пароль → `/w/{slug}/app`.

Папки: `pilot_private/deployed_rooms/{slug}/` (gitignored).
