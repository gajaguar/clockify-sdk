---
type: convention
title: Offset pagination
description: list() hides Clockify's page/page-size pagination behind a lazy iterator; list_page() exposes one page at a time.
tags: [sdk]
status: stable
---

# Offset pagination

Clockify collection endpoints are offset-paginated (`page`, `page-size`).
`list()` hides that behind a lazy iterator; `list_page()` exposes one page at
a time for callers that want to manage their own cursor.

```mermaid
flowchart LR
    A["ws.projects.list()"] --> B["request page=1"]
    B --> C{"page size\n== requested?"}
    C -- yes --> D["yield items"]
    D --> E["request page=N+1"]
    E --> C
    C -- no --> F["yield remaining items"]
    F --> G["StopIteration"]
```
