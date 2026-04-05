import adapter from '@sveltejs/adapter-vercel';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		// Pin serverless runtime so local builds work on Node 24+ and match Vercel.
		adapter: adapter({ runtime: 'nodejs22.x' })
	}
};

export default config;
