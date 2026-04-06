<script lang="ts">
	import { onMount } from 'svelte';
	import mapboxgl from 'mapbox-gl';
	import 'mapbox-gl/dist/mapbox-gl.css';
	import { PUBLIC_MAPBOX_TOKEN } from '$env/static/public';
	import './+page.css';

	const MAP_STYLE = 'mapbox://styles/arjunkakkar8/clzoilzc1006y01pzaqwl1csh';
	const SOURCE = 'composite';
	const SOURCE_LAYER = 'merged_rent_data_zip_sf';
	const LAYER = 'zip-rent-disparity';

	const VIEWS = [
		{ center: [-97.648, 40.205] as [number, number], zoom: 3.64 },
		{ center: [-122.15, 37.65] as [number, number], zoom: 8.8 },
		{ center: [-122.383, 37.735] as [number, number], zoom: 12.5 },
		{ center: [-121.89, 37.34] as [number, number], zoom: 10.5 },
		{ center: [-122.22, 37.8] as [number, number], zoom: 11.2 },
		{ center: [-122.15, 37.65] as [number, number], zoom: 9.2 }
	];

	let mapEl = $state<HTMLDivElement | undefined>(undefined);

	/** From `.env` via `$env/static/public` (SvelteKit; `import.meta.env.PUBLIC_*` is not reliable here). */
	const mapboxToken = (PUBLIC_MAPBOX_TOKEN ?? '').trim();

	function fmtDollars(n: unknown) {
		return n != null && !Number.isNaN(Number(n))
			? '$' + Math.round(Number(n)).toLocaleString('en-US')
			: '—';
	}
	function fmtPercent(n: unknown) {
		return n != null && !Number.isNaN(Number(n)) ? Math.round(Number(n) * 100) + '%' : '—';
	}

	onMount(() => {
		if (!mapEl) return;

		/** When /map is shown in an iframe, wheel must scroll the parent page — not zoom the map. */
		const embedded = typeof window !== 'undefined' && window.parent !== window;

		if (!mapboxToken) {
			mapEl.innerHTML =
				'<div style="display:flex;align-items:center;justify-content:center;height:100%;min-height:240px;padding:2rem;text-align:center;font-family:system-ui,sans-serif;background:#1a1a1a;color:#f5f5f5;">Set <code style="background:#333;padding:0.2em 0.4em;border-radius:4px;">PUBLIC_MAPBOX_TOKEN</code> in <code style="background:#333;padding:0.2em 0.4em;border-radius:4px;">.env</code> at the project root, then restart the dev server.</div>';
			return;
		}

		mapboxgl.accessToken = mapboxToken;

		if (!mapboxgl.supported()) {
			mapEl.innerHTML =
				'<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#fff;font-family:sans-serif;padding:2rem;text-align:center;">Your browser does not support Mapbox GL.</div>';
			return;
		}

		const map = new mapboxgl.Map({
			container: mapEl,
			style: MAP_STYLE,
			center: VIEWS[0].center,
			zoom: VIEWS[0].zoom,
			minZoom: 3,
			maxZoom: 14,
			cooperativeGestures: true
		});

		map.dragRotate.disable();
		map.touchZoomRotate.disableRotation();
		map.scrollZoom.disable();

		const navControl = new mapboxgl.NavigationControl({ showCompass: false });
		const popup = new mapboxgl.Popup({ closeButton: false, closeOnClick: false });
		let hoveredId: string | undefined;
		let mapInteractive = false;
		let currentStep = -1;

		map.on('style.load', () => {
			map.resize();

			const loader = document.getElementById('mapLoading');
			if (loader) loader.classList.add('hidden');

			const layerObj = map.getLayer(LAYER);
			if (!layerObj) {
				console.warn('Layer "' + LAYER + '" not found. Available layers:');
				map.getStyle()?.layers?.forEach((l) => console.log('  -', l.id, l.type));
				return;
			}

			map.setPaintProperty(LAYER, 'fill-opacity', [
				'case',
				['boolean', ['feature-state', 'hover'], false],
				1,
				0.7
			]);
			map.setPaintProperty(LAYER, 'fill-outline-color', [
				'case',
				['boolean', ['feature-state', 'hover'], false],
				'rgba(0,0,0,1)',
				'rgba(0,0,0,0.05)'
			]);

			map.on('mousemove', LAYER, (e) => {
				if (!e.features?.length) return;
				if (hoveredId !== undefined) {
					map.setFeatureState(
						{ source: SOURCE, sourceLayer: SOURCE_LAYER, id: hoveredId },
						{ hover: false }
					);
				}
				hoveredId = String(e.features[0].id);
				map.setFeatureState(
					{ source: SOURCE, sourceLayer: SOURCE_LAYER, id: hoveredId },
					{ hover: true }
				);

				const d = e.features[0].properties;
				if (!d || !(d.MEAN_ZORI || d.MEDIAN_ACS_RENT)) {
					map.getCanvas().style.cursor = '';
					popup.remove();
					return;
				}
				map.getCanvas().style.cursor = 'pointer';

				let html = '<div class="popup-content">';
				html +=
					'<strong>' +
					(d.PO_NAME || '') +
					', ' +
					(d.STATE || '') +
					': ' +
					(d.ZIP || '') +
					'</strong>';
				if (d.MEAN_ZORI)
					html +=
						'Zillow ZORI: <span class="popup-stat zori">' + fmtDollars(d.MEAN_ZORI) + '</span><br>';
				if (d.MEDIAN_ACS_RENT)
					html +=
						'ACS Median: <span class="popup-stat acs">' +
						fmtDollars(d.MEDIAN_ACS_RENT) +
						'</span><br>';
				if (d.MEAN_ZORI && d.MEDIAN_ACS_RENT) {
					const gap = (Number(d.MEAN_ZORI) - Number(d.MEDIAN_ACS_RENT)) / Number(d.MEDIAN_ACS_RENT);
					html += 'Disparity: <span class="popup-stat disp">' + fmtPercent(gap) + '</span>';
				}
				html += '</div>';
				popup.setLngLat(e.lngLat).setHTML(html).addTo(map);
			});

			map.on('mouseleave', LAYER, () => {
				if (hoveredId !== undefined) {
					map.setFeatureState(
						{ source: SOURCE, sourceLayer: SOURCE_LAYER, id: hoveredId },
						{ hover: false }
					);
				}
				hoveredId = undefined;
				map.getCanvas().style.cursor = '';
				popup.remove();
			});

			map.on('click', LAYER, (e) => {
				if (!e.features?.length) return;
				if (hoveredId !== undefined) {
					map.setFeatureState(
						{ source: SOURCE, sourceLayer: SOURCE_LAYER, id: hoveredId },
						{ hover: false }
					);
				}
				hoveredId = String(e.features[0].id);
				map.setFeatureState(
					{ source: SOURCE, sourceLayer: SOURCE_LAYER, id: hoveredId },
					{ hover: true }
				);

				const d = e.features[0].properties;
				if (!d || !(d.MEAN_ZORI || d.MEDIAN_ACS_RENT)) {
					popup.remove();
					return;
				}

				let html = '<div class="popup-content">';
				html +=
					'<strong>' +
					(d.PO_NAME || '') +
					', ' +
					(d.STATE || '') +
					': ' +
					(d.ZIP || '') +
					'</strong>';
				if (d.MEAN_ZORI)
					html +=
						'Zillow ZORI: <span class="popup-stat zori">' + fmtDollars(d.MEAN_ZORI) + '</span><br>';
				if (d.MEDIAN_ACS_RENT)
					html +=
						'ACS Median: <span class="popup-stat acs">' +
						fmtDollars(d.MEDIAN_ACS_RENT) +
						'</span><br>';
				if (d.MEAN_ZORI && d.MEDIAN_ACS_RENT) {
					const gap = (Number(d.MEAN_ZORI) - Number(d.MEDIAN_ACS_RENT)) / Number(d.MEDIAN_ACS_RENT);
					html += 'Disparity: <span class="popup-stat disp">' + fmtPercent(gap) + '</span>';
				}
				html += '</div>';
				popup.setLngLat(e.lngLat).setHTML(html).addTo(map);
			});

			map.on('click', (e) => {
				const features = map.queryRenderedFeatures(e.point, { layers: [LAYER] });
				if (!features?.length) {
					if (hoveredId !== undefined) {
						map.setFeatureState(
							{ source: SOURCE, sourceLayer: SOURCE_LAYER, id: hoveredId },
							{ hover: false }
						);
						hoveredId = undefined;
					}
					popup.remove();
				}
			});

			const steps = document.querySelectorAll('.scroll-step');
			const legend = document.getElementById('mapLegend');

			const observer = new IntersectionObserver(
				(entries) => {
					let bestEntry: IntersectionObserverEntry | null = null;
					let bestRatio = 0;

					for (const entry of entries) {
						const card = entry.target.querySelector('.step-card');
						if (entry.isIntersecting && card) {
							card.classList.add('visible');
							if (entry.intersectionRatio > bestRatio) {
								bestRatio = entry.intersectionRatio;
								bestEntry = entry;
							}
						}
					}

					if (bestEntry) {
						const stepIndex = parseInt(bestEntry.target.getAttribute('data-step') ?? '0', 10);
						if (stepIndex !== currentStep) {
							currentStep = stepIndex;
							const view = VIEWS[stepIndex];
							if (view) {
								map.flyTo({
									center: view.center,
									zoom: view.zoom,
									pitch: 0,
									bearing: 0,
									essential: true,
									duration: 2000,
									easing: (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t)
								});
							}
							if (legend) {
								if (stepIndex > 0) legend.classList.add('visible');
								else legend.classList.remove('visible');
							}
							if (stepIndex === 5) enableInteractive();
							else disableInteractive();
						}
					}
				},
				{
					threshold: [0, 0.3, 0.5, 0.7, 1],
					rootMargin: '0px 0px -30% 0px'
				}
			);

			steps.forEach((step) => observer.observe(step));
		});

		map.on('error', (e) => {
			console.error('Mapbox error:', e.error || e);
		});

		const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

		function enableInteractive() {
			if (mapInteractive) return;
			mapInteractive = true;
			// In an iframe, scroll-zoom steals wheel events and blocks scrolling the parent page.
			if (!embedded) {
				map.scrollZoom.enable();
			}
			if (isTouchDevice) {
				map.touchZoomRotate.enable();
				map.dragPan.enable();
			}
			map.addControl(navControl, 'bottom-right');
		}

		function disableInteractive() {
			if (!mapInteractive) return;
			mapInteractive = false;
			map.scrollZoom.disable();
			try {
				map.removeControl(navControl);
			} catch {
				/* already removed */
			}
			popup.remove();
		}

		const legendToggle = document.getElementById('legendToggle');
		const legendItems = document.getElementById('legendItems');
		legendToggle?.addEventListener('click', function (this: HTMLElement) {
			this.classList.toggle('open');
			legendItems?.classList.toggle('expanded');
		});

		let detachIframeWheel: (() => void) | undefined;
		if (embedded) {
			const origin = window.location.origin;
			let innerScrollAllowed = false;
			const onParentActivation = (e: MessageEvent) => {
				if (e.origin !== origin) return;
				if (e.data?.type === 'openrent-map-activation') {
					innerScrollAllowed = Boolean(e.data.active);
				}
			};
			window.addEventListener('message', onParentActivation);

			/** Parent may post activation before this listener exists (prod hydration timing). Ping so it resyncs. */
			const pingParentReady = () => {
				try {
					window.parent.postMessage({ type: 'openrent-map-ready' }, origin);
				} catch {
					/* ignore */
				}
			};
			queueMicrotask(pingParentReady);
			requestAnimationFrame(() => requestAnimationFrame(pingParentReady));
			setTimeout(pingParentReady, 120);

			const onWheelCapture = (e: WheelEvent) => {
				if (!innerScrollAllowed) {
					e.preventDefault();
					window.parent.postMessage({ type: 'openrent-iframe-scroll', deltaY: e.deltaY }, origin);
					return;
				}
				const root = document.documentElement;
				const scrollTop = window.scrollY || root.scrollTop;
				const maxScroll = Math.max(0, root.scrollHeight - window.innerHeight);
				const atBottom = maxScroll - scrollTop < 8;
				const atTop = scrollTop <= 0;
				if (atBottom && e.deltaY > 0) {
					e.preventDefault();
					window.parent.postMessage({ type: 'openrent-iframe-scroll', deltaY: e.deltaY }, origin);
				} else if (atTop && e.deltaY < 0) {
					e.preventDefault();
					window.parent.postMessage({ type: 'openrent-iframe-scroll', deltaY: e.deltaY }, origin);
				}
			};
			document.addEventListener('wheel', onWheelCapture, { capture: true, passive: false });
			detachIframeWheel = () => {
				document.removeEventListener('wheel', onWheelCapture, true);
				window.removeEventListener('message', onParentActivation);
			};
		}

		return () => {
			detachIframeWheel?.();
			map.remove();
		};
	});
</script>

<svelte:head>
	<title>Bay Area Rent Data Map — Scrollytelling Section</title>
</svelte:head>

{#if !mapboxToken}
	<p class="token-msg">
		Mapbox token missing: add <code>PUBLIC_MAPBOX_TOKEN=pk.&hellip;</code> to <code>.env</code> (see
		<code>.env.example</code>), then restart <code>npm run dev</code> or rebuild.
	</p>
{/if}

<section class="map-scrolly" id="rent-map">
	<div class="map-sticky">
		<div id="map" bind:this={mapEl}></div>
		<div class="map-loading" id="mapLoading">
			<span>Loading map&hellip;</span>
		</div>
	</div>

	<div class="map-legend" id="mapLegend">
		<button type="button" class="legend-toggle" id="legendToggle">
			Similarity of price data
			<svg width="12" height="12" viewBox="0 0 12 12" fill="none"
				><path
					d="M3 4.5L6 7.5L9 4.5"
					stroke="currentColor"
					stroke-width="1.5"
					stroke-linecap="round"
				/></svg
			>
		</button>
		<ul class="legend-items" id="legendItems">
			<li class="legend-item legend-similar">
				<span class="label">Similar</span><span class="detail"
					>Data sources are within ±30% of each other.</span
				>
			</li>
			<li class="legend-item legend-dissim">
				<span class="label">Dissimilar</span><span class="detail">ZORI is up to 100% above the ACS data.</span>
			</li>
			<li class="legend-item legend-verydiss">
				<span class="label">Very Dissimilar</span><span class="detail">ZORI is up to 200% above ACS data.</span>
			</li>
			<li class="legend-item legend-extreme">
				<span class="label">Extremely Dissimilar</span><span class="detail"
					>ZORI is more than 200% above ACS data.</span
				>
			</li>
			<li class="legend-item legend-onedata">
				<span class="label">One Source Available</span><span class="detail"
					>Only one data source exists for this zip code.</span
				>
			</li>
			<li class="legend-item legend-nodata">
				<span class="label">No Data Available</span><span class="detail"
					>Neither data source is available.</span
				>
			</li>
		</ul>
	</div>

	<div class="scroll-steps">
		<div class="scroll-step" data-step="0">
			<div class="step-card step-intro">
				<div class="step-eyebrow">Rent Data Explorer</div>
				<h2 class="step-title">Mapping the Bay Area's Rent Data Gaps</h2>
				<p class="step-body">
					Using the two most widely available public data sources — the <strong>Zillow Observed Rent Index</strong>
					and the <strong>American Community Survey</strong> — we can visualize where rent estimates agree, diverge,
					or are missing entirely across the Bay Area.
				</p>
				<div class="step-scroll-cue"><div class="scroll-arrow"></div>Scroll to explore</div>
			</div>
		</div>

		<div class="scroll-step" data-step="1">
			<div class="step-card">
				<div class="step-eyebrow">The Bay Area</div>
				<h2 class="step-title">Zooming into a region of critical need</h2>
				<p class="step-body">
					The Bay Area is one of the most expensive rental markets in the country — and one where data quality matters
					most. Across the nine-county region, rent estimates from different sources often paint
					<strong>strikingly different pictures</strong> of what tenants actually pay.
				</p>
			</div>
		</div>

		<div class="scroll-step" data-step="2">
			<div class="step-card">
				<div class="step-eyebrow">San Francisco</div>
				<h2 class="step-title">Bayview–Hunters Point: the widest gap in SF</h2>
				<p class="step-body">
					In San Francisco's Bayview neighborhood, the disparity between data sources is among the
					<strong>largest in the city</strong>. Colored in <span class="highlight highlight-extreme">deep brown</span>,
					this historically Black community faces ongoing gentrification pressures — and the data used to set housing
					assistance levels may not reflect what renters actually experience on the ground.
				</p>
			</div>
		</div>

		<div class="scroll-step" data-step="3">
			<div class="step-card">
				<div class="step-eyebrow">South Bay</div>
				<h2 class="step-title">San Jose &amp; Silicon Valley: data blind spots</h2>
				<p class="step-body">
					Moving south to <strong>San Jose</strong> and the broader Silicon Valley, notice the patchwork of
					<span class="highlight highlight-onedata">gray</span> and
					<span class="highlight highlight-nodata">white</span> zip codes where one or both data sources are entirely
					missing. In one of the most economically dynamic regions in the world, basic rental data remains incomplete.
				</p>
			</div>
		</div>

		<div class="scroll-step" data-step="4">
			<div class="step-card">
				<div class="step-eyebrow">East Bay</div>
				<h2 class="step-title">Oakland &amp; the East Bay: a pattern of disparity</h2>
				<p class="step-body">
					Across the bay in <strong>Oakland</strong> and surrounding communities, rent data disparities follow familiar
					patterns — with the largest gaps concentrated in neighborhoods experiencing the most rapid change. The
					<span class="highlight highlight-dissim">dark yellow</span> zip codes often overlap with areas where displacement
					risk is highest.
				</p>
			</div>
		</div>

		<div class="scroll-step" data-step="5">
			<div class="step-card step-explore">
				<div class="step-eyebrow">Explore</div>
				<h2 class="step-title">See your neighborhood</h2>
				<p class="step-body">
					Pan and zoom the map to explore rent data disparities across the Bay Area.
					<strong class="explore-hint-desktop">Hover over any zip code</strong><strong class="explore-hint-mobile"
						>Tap any zip code</strong
					> to see the Zillow ZORI estimate, the ACS median rent, and the gap between them.
				</p>
				<div class="explore-note explore-note-desktop">Use scroll + ctrl/⌘ to zoom · Click and drag to pan</div>
				<div class="explore-note explore-note-mobile">Pinch to zoom · Tap a zip code for details</div>
			</div>
		</div>
	</div>
</section>

<style>
	.token-msg {
		padding: 1rem;
		font-family: system-ui, sans-serif;
		background: #fff3cd;
		color: #333;
	}
</style>
