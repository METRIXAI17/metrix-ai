# Online-business niche rework

Отдельный **prompt piece** + executor для переработки ниш, когда **исполнитель = online business**.

## Prompt

- Source: `backend/core/business_gen/online_niche_rework.py` → `ONLINE_NICHE_PROMPT`
- API: `GET /api/v1/analytics/online-niche-prompt`

## Execute

```http
POST /api/v1/analytics/online-niche-rework
{
  "business": "Online architecture library for IT builders…",
  "project_name": "Lib",
  "multi_pass": 3,
  "lang": "ru"
}
```

## Pipeline (modules)

1. Detect online executor  
2. Segment (`client_segmentation`)  
3. Expert directions  
4. Sophisticated path  
5. Multi-pass **originality inject** on 6 niche genomes  
6. Three directions text (product/unit/channel)  
7. Acceptance forecast  
8. wayD labels + terminal + unique functions  

## Eval

```bash
py -3 scripts/multi_pass_path_eval.py --passes 3
```

Report: `docs/reports/MULTI_PASS_TOP5_PATHS_2026-08-07.md`
