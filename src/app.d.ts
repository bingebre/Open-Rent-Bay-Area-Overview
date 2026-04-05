// See https://svelte.dev/docs/kit/types#app.d.ts

interface ImportMetaEnv {
	/** Mapbox public token (set in `.env` as `PUBLIC_MAPBOX_TOKEN=...`) */
	readonly PUBLIC_MAPBOX_TOKEN?: string;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}

declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
