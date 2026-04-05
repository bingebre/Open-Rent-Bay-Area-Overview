# Open Rent — Bay Area Overview

SvelteKit app migrated from standalone HTML. The marketing site lives at `/`; the Mapbox scrollytelling map is at `/map` (also embedded in an iframe on the home page).

## Setup

```bash
npm install
cp .env.example .env
# Set PUBLIC_MAPBOX_TOKEN to your Mapbox public token (same as the old inline token).
npm run dev
```

## Scripts

- `npm run dev` — local dev server
- `npm run build` — production build
- `npm run preview` — preview the production build

## Project notes

- **Legacy HTML** is under `legacy/` for reference. Inline base64 images were extracted to `static/embedded/` via `scripts/extract_data_uris.py`.
- **Mapbox**: the token must be in `.env` as `PUBLIC_MAPBOX_TOKEN`. Do not commit real secrets in public repos; rotate tokens that were previously committed in HTML.
- **Large media**: `static/Rent Tool Video.mov` and images are served as static files.
