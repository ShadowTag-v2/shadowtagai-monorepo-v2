---
name: "Scrapling Vue SPA Data Parser"
id: "scrapling-vue-spa-parse"
description: Use Scrapling to parse post-processed HTML. Resolves infinite-scroll spacing issues.
execution:
  script: |
    from scrapling import Core
    core = Core(html=user_input['rendered_html'], timeout=10)
    items = []
    for item in core.select(user_input['selector']):
        item_id = item.get("data-id") or item.get("id")
        if item_id not in [i['id'] for i in items]:
            items.append({"id": item_id, "text": item.text})
    return {"items": items, "total": len(items)}
---
