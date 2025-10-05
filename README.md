# FastAPI Movie & Book scraper

A simple scraper to get movie and booker data for my collection.

Stack:
- Backend: FastAPI
- HTML Templates: Jinja2
- Progressive Enhancement: HTMX
- Styling: TailwindCSS

The scraper is protected by an API key in the env vars. You can start the dev server
with:
```bash
API_KEY=TEST_KEY uv fastapi dev main.py
```

Then navigate the http://localhost:8000/TEST_KEY/

To keep the styling up to date, run Tailwind:
```bash
cd tailwindcss
npm install
npm run dev
```