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

## Deployment

This project uses [`adapter-auto`](https://kit.svelte.dev/docs/adapter-auto), which picks a SvelteKit adapter during the build on supported hosts (for example Vercel or Netlify). You do not need to change `svelte.config.js` for those platforms if you deploy with their default SvelteKit integration.

**Environment variable**

Configure **`PUBLIC_MAPBOX_TOKEN`** in the hosting dashboard (same value as in local `.env`). The map route needs it at **build time** and at runtime. Redeploy after changing it.

**Vercel**

1. Import the GitHub repo and keep the default **SvelteKit** / **Vite** settings.
2. **Build command:** `npm run build` (default).
3. **Output:** leave as recommended by the Vercel SvelteKit preset.
4. **Environment variables:** add `PUBLIC_MAPBOX_TOKEN` for Production (and Preview if you use it).

**Netlify**

1. Connect the repo; use the Netlify **SvelteKit** plugin or the [documented](https://kit.svelte.dev/docs/adapter-netlify) settings.
2. **Build command:** `npm run build`.
3. **Publish directory:** follow Netlify’s SvelteKit docs (often handled automatically by the adapter).
4. **Environment:** set `PUBLIC_MAPBOX_TOKEN` under Site configuration → Environment variables.

**Other hosts**

For a generic Node server or Docker, switch to [`adapter-node`](https://github.com/sveltejs/kit/tree/master/packages/adapter-node) (or another [official adapter](https://kit.svelte.dev/docs/adapters)) and follow that adapter’s deployment guide.

## Project notes

- **Legacy HTML** is under `legacy/` for reference. Inline base64 images were extracted to `static/embedded/` via `scripts/extract_data_uris.py`.
- **Mapbox**: the token must be in `.env` as `PUBLIC_MAPBOX_TOKEN`. Do not commit real secrets in public repos; rotate tokens that were previously committed in HTML.
- **Large media**: `static/Rent Tool Video.mov` and images are served as static files.
