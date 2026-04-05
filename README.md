# Open Rent — Bay Area Overview

SvelteKit app migrated from standalone HTML. The marketing site lives at `/`; the Mapbox scrollytelling map is at `/map` (also embedded in an iframe on the home page).

## Setup

```bash
npm install
cp .env.example .env
```

In `.env`, set **exactly** `PUBLIC_MAPBOX_TOKEN=pk....` (the `PUBLIC_` prefix is required so Vite exposes it to the map). Do not use `MAPBOX_TOKEN` or spaces around `=`. After editing `.env`, restart `npm run dev` (or run `npm run build` again for preview).

## Scripts

- `npm run dev` — local dev server
- `npm run build` — production build
- `npm run preview` — preview the production build

## Project notes

- **Legacy HTML** is under `legacy/` for reference. Inline base64 images were extracted to `static/embedded/` via `scripts/extract_data_uris.py`.
- **Mapbox**: the token must be in `.env` as `PUBLIC_MAPBOX_TOKEN`. Do not commit real secrets in public repos; rotate tokens that were previously committed in HTML.
- **Large media**: `static/Rent Tool Video.mov` and images are served as static files.
