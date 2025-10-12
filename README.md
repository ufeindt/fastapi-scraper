# FastAPI Movie & Book scraper

A simple scraper to get movie and booker data for my collection.

Stack:
- Backend: FastAPI
- HTML Templates: Jinja2
- Progressive Enhancement: HTMX

The scraper is protected by an API key and requires an email address (for the
OpenLibrary API) in the env vars. You can start the dev server with:
```bash
API_KEY=TEST_KEY ADMIN_EMAIL=your@email.address uv fastapi dev main.py
```

Then navigate the http://localhost:8000/TEST_KEY/
ev
```