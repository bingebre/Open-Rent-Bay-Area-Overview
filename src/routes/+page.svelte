
<script lang="ts">
	import { onMount } from 'svelte';

	onMount(() => {
		const observerOptions = { threshold: 0.12, rootMargin: '0px 0px -30px 0px' };
		const observer = new IntersectionObserver((entries) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) {
					entry.target.classList.add('visible');
					const bars = entry.target.querySelectorAll('.funnel-bar[data-width]');
					bars.forEach((bar) => {
						setTimeout(() => {
							(bar as HTMLElement).style.width = (bar as HTMLElement).dataset.width ?? '';
						}, 300);
					});
				}
			});
		}, observerOptions);
		document.querySelectorAll('.reveal, .reveal-scale, .funnel-row').forEach((el) => observer.observe(el));

		const nav = document.getElementById('nav');
		const onScrollNav = () => {
			if (nav) nav.classList.toggle('scrolled', window.scrollY > 60);
		};
		window.addEventListener('scroll', onScrollNav, { passive: true });

		const countObserver = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						const el = entry.target as HTMLElement;
						const target = parseInt(el.dataset.target ?? '0', 10);
						const suffix = el.dataset.suffix || '';
						let current = 0;
						const step = target / 60;
						const interval = setInterval(() => {
							current += step;
							if (current >= target) {
								current = target;
								clearInterval(interval);
							}
							el.textContent = Math.floor(current) + suffix;
						}, 25);
						countObserver.unobserve(el);
					}
				});
			},
			{ threshold: 0.5 }
		);
		document.querySelectorAll('.count-up').forEach((el) => countObserver.observe(el));

		const container = document.querySelector('.img-overlay-container');
		let svg: SVGSVGElement | null = null;
		if (container) {
			svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
			svg.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1;';
			container.appendChild(svg);

			const connections: [number, number, number][] = [
				[0, 33, 28],
				[1, 28, 42],
				[2, 24, 52],
				[3, 22, 65],
				[4, 46, 18],
				[5, 54, 12],
				[6, 66, 20],
				[7, 65, 38],
				[8, 58, 52],
				[9, 38, 68],
			];

			function drawLines() {
				if (!svg || !container) return;
				const svgEl = svg;
				svgEl.innerHTML = '';
				const rect = container.getBoundingClientRect();
				const labels = container.querySelectorAll('.overlay-label');
				connections.forEach(([idx, tx, ty]) => {
					const label = labels[idx];
					if (!label || getComputedStyle(label).display === 'none') return;
					const lRect = label.getBoundingClientRect();
					const cRect = container.getBoundingClientRect();
					const targetX = (tx / 100) * rect.width;
					const targetY = (ty / 100) * rect.height;
					let startX: number;
					let startY: number;
					const lLeft = lRect.left - cRect.left;
					const lRight = lRect.right - cRect.left;
					const lTop = lRect.top - cRect.top;
					const lBottom = lRect.bottom - cRect.top;
					const lCenterY = (lTop + lBottom) / 2;
					if (lRight < targetX) {
						startX = lRight + 4;
						startY = lCenterY;
					} else if (lLeft > targetX) {
						startX = lLeft - 4;
						startY = lCenterY;
					} else {
						startX = (lLeft + lRight) / 2;
						startY = targetY < lTop ? lTop - 2 : lBottom + 2;
					}
					const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
					line.setAttribute('x1', String(startX));
					line.setAttribute('y1', String(startY));
					line.setAttribute('x2', String(targetX));
					line.setAttribute('y2', String(targetY));
					line.setAttribute('stroke', '#555');
					line.setAttribute('stroke-width', '1');
					line.setAttribute('stroke-dasharray', '3,2');
					svgEl.appendChild(line);
				});
			}
			window.addEventListener('load', () => setTimeout(drawLines, 500));
			window.addEventListener('resize', drawLines);
		}

		const parallaxDiv = document.querySelector('.parallax-divider');
		const contextMap = document.getElementById('contextMap');
		const contextParas = document.querySelectorAll('.context-para');
		const mapEmbed = document.getElementById('mapEmbed') as HTMLIFrameElement | null;

		const syncMapEmbedScrollActivation = () => {
			if (!mapEmbed?.contentWindow) return;
			const rect = mapEmbed.getBoundingClientRect();
			const navEl = document.getElementById('nav');
			const viewTop = navEl ? Math.ceil(navEl.getBoundingClientRect().bottom) + 4 : 88;

			const vv = window.visualViewport;
			const viewLeft = vv?.offsetLeft ?? 0;
			const viewRight = viewLeft + (vv?.width ?? window.innerWidth);
			const viewBottom = vv != null ? vv.offsetTop + vv.height : window.innerHeight;

			const usableH = Math.max(0, viewBottom - viewTop);

			const visibleTop = Math.max(rect.top, viewTop);
			const visibleBottom = Math.min(rect.bottom, viewBottom);
			const visibleHeight = Math.max(0, visibleBottom - visibleTop);
			const visibleLeft = Math.max(rect.left, viewLeft);
			const visibleRight = Math.min(rect.right, viewRight);
			const visibleWidth = Math.max(0, visibleRight - visibleLeft);

			const hRatio = rect.height > 0 ? visibleHeight / rect.height : 0;
			const wRatio = rect.width > 0 ? visibleWidth / rect.width : 0;

			/*
			 * Old check required visibleHeight ≈ min(iframe, viewport), which fails when the iframe top
			 * tucks under the fixed nav (common) — activation never flipped on production.
			 */
			const minWRatio = 0.85;
			const tallerThanUsable = rect.height > usableH + 24;
			let active: boolean;
			if (tallerThanUsable) {
				active =
					wRatio >= minWRatio &&
					rect.top <= viewTop + 20 &&
					rect.bottom >= viewBottom - 20;
			} else {
				active = hRatio >= 0.62 && wRatio >= minWRatio;
			}

			try {
				mapEmbed.contentWindow.postMessage(
					{ type: 'openrent-map-activation', active },
					window.location.origin
				);
			} catch {
				/* ignore */
			}
		};

		const onScrollFx = () => {
			if (parallaxDiv) {
				const rect = parallaxDiv.getBoundingClientRect();
				const bg = parallaxDiv.querySelector('.parallax-bg') as HTMLElement | null;
				if (bg) bg.style.transform = `translateY(${rect.top * 0.25}px)`;
			}

			if (contextMap) {
				const section = contextMap.parentElement;
				if (section) {
					const rect = section.getBoundingClientRect();
					const scrollProgress = -rect.top;
					contextMap.style.transform = `translateY(${scrollProgress * 0.15}px)`;
				}
			}

			contextParas.forEach((para) => {
				if (!para.classList.contains('visible')) return;
				const speed = parseFloat((para as HTMLElement).dataset.speed || '0.05');
				const rect = para.getBoundingClientRect();
				const center = window.innerHeight / 2;
				const offset = (rect.top - center) * speed;
				(para as HTMLElement).style.transform = `translateY(${offset}px)`;
			});
			syncMapEmbedScrollActivation();
		};
		window.addEventListener('scroll', onScrollFx, { passive: true });
		window.addEventListener('resize', syncMapEmbedScrollActivation, { passive: true });
		window.visualViewport?.addEventListener('resize', syncMapEmbedScrollActivation, { passive: true });
		window.visualViewport?.addEventListener('scroll', syncMapEmbedScrollActivation, { passive: true });
		mapEmbed?.addEventListener('load', syncMapEmbedScrollActivation);
		syncMapEmbedScrollActivation();

		const ioThresholds = Array.from({ length: 21 }, (_, i) => i / 20);
		let mapEmbedIo: IntersectionObserver | undefined;
		if (mapEmbed) {
			mapEmbedIo = new IntersectionObserver(() => syncMapEmbedScrollActivation(), {
				root: null,
				rootMargin: '-96px 0px 0px 0px',
				threshold: ioThresholds
			});
			mapEmbedIo.observe(mapEmbed);
		}

		const onIframeScrollMsg = (e: MessageEvent) => {
			if (e.origin !== window.location.origin) return;
			if (e.data?.type === 'openrent-map-ready') {
				syncMapEmbedScrollActivation();
				return;
			}
			if (e.data?.type === 'openrent-iframe-scroll' && typeof e.data.deltaY === 'number') {
				window.scrollBy({ top: e.data.deltaY, left: 0, behavior: 'auto' });
			}
		};
		window.addEventListener('message', onIframeScrollMsg);

		return () => {
			window.removeEventListener('scroll', onScrollNav);
			window.removeEventListener('scroll', onScrollFx);
			window.removeEventListener('message', onIframeScrollMsg);
			window.removeEventListener('resize', syncMapEmbedScrollActivation);
			window.visualViewport?.removeEventListener('resize', syncMapEmbedScrollActivation);
			window.visualViewport?.removeEventListener('scroll', syncMapEmbedScrollActivation);
			mapEmbed?.removeEventListener('load', syncMapEmbedScrollActivation);
			mapEmbedIo?.disconnect();
		};
	});
</script>

<svelte:head>
	<title>The Open Rent Initiative — Citizen Codex</title>
</svelte:head>

<nav id="nav">
  <div class="nav-links">
    <a href="#problem">Problem</a>
    <a href="#solution">Solution</a>
    <a href="#features">Features</a>
    <a href="#impact">Impact</a>
    <a href="#roadmap">Roadmap</a>
  </div>
</nav>

<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-content">
    <h1>The Open Rent Initiative</h1>
    <p class="hero-sub">Open, trusted rent data that powers economic opportunity.</p>
    <div class="hero-scroll-cue">
      <span>Scroll to explore</span>
      <div class="scroll-line"></div>
    </div>
  </div>
</section>

<section class="context-section" id="problem">
  <!-- Bay Area Map Background -->
  <div class="context-map-bg" id="contextMap">
    <img src="/embedded/img-002.png" alt="Collecting Data From Multiple Sources To Create A Comprehensive Picture" style="width: 100%; border-radius: 4px;" />
  </div>

  <div class="section-inner context-inner" style="position: relative; z-index: 2;">
    <div class="reveal">
      <div class="section-label context-label">The Context</div>
    </div>
    <div class="context-para reveal" data-speed="0.03">
      <h2 class="context-title">
        The challenge of
        <span>fragmented rent data.</span>
      </h2>
    </div>
    <div class="context-para reveal" data-speed="0.05">
      <p class="context-body">
        Across the Bay Area, organizations working to preserve and build affordable housing, protect tenants from displacement and shape smarter housing policy share a common need: timely, granular, and trustworthy insights on rental markets...
      </p>
    </div>
    <div class="context-para reveal" data-speed="0.07">
      <p class="context-quote">
        "Unfortunately, none of these organizations are getting the
        <span>data they need</span> to inform sound decisions."
      </p>
    </div>
  </div>
</section>

<section class="the-problem-section">
  <div class="section-inner problem-inner">
    <div class="reveal">
      <div class="section-label problem-label">The Problem</div>
      <h3 class="problem-heading">An Example</h3>
    </div>

    <div class="reveal" style="transition-delay: 0.1s;">
      <p class="problem-intro">
        To illustrate, consider the most widely used data sources: the
        <em>American Community Survey (ACS)</em> and the
        <em>Zillow Observed Rent Index (ORI)</em>. These sources have numerous limitations.
      </p>
    </div>

    <div class="problem-cards reveal" style="transition-delay: 0.2s;">
      <article class="problem-example-card">
        <h4>Aggregate Obscurity</h4>
        <p>Both sources provide only aggregate data which obscure neighborhood-level details, preventing precise local intervention.</p>
      </article>
      <article class="problem-example-card">
        <h4>Spatial Gaps</h4>
        <p>ORI only covers markets within Zillow's footprint, leaving many communities without timely rental visibility.</p>
      </article>
      <article class="problem-example-card">
        <h4>Temporal Lag</h4>
        <p>ACS is based on historical, lagging data - describing the past, not the present.</p>
      </article>
    </div>

    <div class="reveal" style="transition-delay: 0.3s;">
      <p class="problem-conclusion">
        As a result, the most widely used public data sources for research and policymaking become
        <span>quickly unreliable</span> at the granular, timely level needed for decisions.
      </p>
    </div>
  </div>
</section>

<section class="disparity-section" style="padding: 0;">
  <div style="width: 100%; height: 80vh; min-height: 600px;">
    <iframe id="mapEmbed" src="/map" title="Bay Area rent data map" style="width: 100%; height: 100%; border: none;" loading="lazy"></iframe>
  </div>
</section>

<section class="impact-problem-section">
  <div class="section-inner impact-problem-inner">
    <div class="reveal">
      <div class="section-label impact-problem-label">The Problem</div>
      <h3 class="impact-problem-title">Impact of Data Deficiencies</h3>
    </div>
    <div class="reveal" style="transition-delay: 0.1s;">
      <p class="impact-problem-intro">
        Widely used sources like ACS and Zillow provide aggregate data that obscure neighborhood-level details, resulting in unreliable insights.
      </p>
    </div>
    <div class="impact-problem-grid">
      <article class="impact-problem-card reveal" style="--i:0">
        <h4>Undercounting Stock</h4>
        <p>Single-family rentals and Naturally Occurring Affordable Housing (NOAH) are often invisible, hindering preservation risks identification.</p>
      </article>
      <article class="impact-problem-card reveal" style="--i:1">
        <h4>Reactive Posture</h4>
        <p>Without real-time tracking, advocates react to displacement only after it occurs rather than deploying early interventions.</p>
      </article>
      <article class="impact-problem-card reveal" style="--i:2">
        <h4>Information Asymmetry</h4>
        <p>Well-resourced orgs have sophisticated analytics, while renters and policymakers operate with poor data, worsening inequities.</p>
      </article>
      <article class="impact-problem-card reveal" style="--i:3">
        <h4>Operational Friction</h4>
        <p>Manually aggregating disparate data sources is a high-cost process that few organizations can afford. If done poorly, it is both a cost of resources that many organizations can't spare and/or can result in poor decision making.</p>
      </article>
    </div>
    <div class="reveal" style="transition-delay: 0.2s;">
      <p class="impact-problem-conclusion">
        Ultimately, this information gap means policies are implemented
        <span>without strong empirical grounding.</span>
      </p>
    </div>
  </div>
</section>

<section class="solution-section" id="solution">
  <div class="section-inner">
    <div class="reveal">
      <div class="solution-title-block">
        <div class="section-label solution-title-label">The Solution</div>
        <h2 class="solution-title-main">The Open Rent<br />Initiative</h2>
      </div>
    </div>
    <div class="solution-layout">
      <div class="solution-text">
        <div class="reveal" style="margin-top: 1.2rem;">
          <p class="solution-intro-copy">
            Building comprehensive public data infrastructure starting with the State of California. We aggregate and harmonize fragmented sources into a single, open platform.
          </p>
        </div>
        <div class="reveal solution-pillars-list" style="transition-delay: 0.1s;">
          <div class="solution-pillar-item">
            <div class="solution-pillar-num">01.</div>
            <div>
              <h4>Data Aggregation</h4>
              <p>Property-level parcel mapping.</p>
            </div>
          </div>
          <div class="solution-pillar-item">
            <div class="solution-pillar-num">02.</div>
            <div>
              <h4>Interactive Tools</h4>
              <p>Visual interfaces for non-technical users.</p>
            </div>
          </div>
          <div class="solution-pillar-item">
            <div class="solution-pillar-num">03.</div>
            <div>
              <h4>Local Partnerships</h4>
              <p>Participatory design with city leaders.</p>
            </div>
          </div>
        </div>
      </div>
      <div class="reveal solution-map">
        <img
          src="/california-rent-registry-map-new.png"
          alt="California rent registry map"
          class="solution-map-img"
        />
      </div>
    </div>
  </div>
  <div class="section-inner section-inner--light" style="background: #F9F5F0;">
    <div class="reveal">
      <h2 class="section-title" style="color: var(--near-black); margin-bottom: 1.1rem; text-align: left; font-style: italic; font-weight: 500; max-width: 760px;">1. Data Aggregation</h2>
      <p class="section-body" style="margin-top: 0; text-align: left; max-width: 760px; font-size: clamp(1.15rem, 2.2vw, 1.9rem); line-height: 1.38; color: #6f7074;">Multiple sources are knit together to get a full picture of rental housing. Connecting disparate data at the parcel level allows for precise affordability analysis.</p>
    </div>
    <div class="reveal" style="display: flex; flex-direction: column; align-items: center; gap: 2rem;">
      <div class="data-aggregation-row">
        <div class="data-aggregation-frame">
          <img
            class="data-aggregation-img"
            src="/embedded/img-004.png"
            alt="Data Aggregation diagram"
          />
        </div>
        <div class="data-aggregation-frame data-aggregation-frame--shadow">
          <img
            class="data-aggregation-img"
            src="/embedded/img-005.png"
            alt="Open Rent tool interface"
          />
        </div>
      </div>
    </div>
  </div>
</section>

<section class="case-study-section" id="features">
  <div class="section-inner">
    <div class="reveal">
      <h2 class="section-title" style="color: var(--near-black); margin-bottom: 1.1rem; text-align: left; font-style: italic; font-weight: 500; max-width: 760px;">2. Interactive Tools</h2>
      <p class="section-body" style="margin-top: 0; text-align: left; max-width: 760px; font-size: clamp(1.15rem, 2.2vw, 1.9rem); line-height: 1.38; color: #6f7074;">Designed for non-technical users such as program officers who need to work with complex data without specialized expertise.</p>

    </div>
    <div class="reveal" style="margin-top: 2.5rem; display: flex; justify-content: center;">
      <div style="max-width: 675px; width: 100%; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 2px solid #d8d5ce; background: #f3f1ec; padding: 8px;">
        <video autoplay loop muted playsinline style="width: 100%; display: block;">
          <source src="/Rent%20Tool%20Video.mov" type="video/quicktime" />
          <source src="/Rent%20Tool%20Video.mov" type="video/mp4" />
        </video>
      </div>
    </div>
  </div>
</section>

<section class="impact-section" id="impact">
  <div class="section-inner">
    <div class="reveal">
      <h2 class="section-title" style="color: var(--near-black); text-align: center; margin-bottom: 2.5rem;">3. Local Partnerships and Engagement</h2>
    </div>
    <div class="reveal impact-partner-layout" style="display: grid; grid-template-columns: minmax(0, 560px) minmax(0, 360px); gap: 0.5rem; justify-content: center; align-items: center;">
      <div style="text-align: left;">
        <p class="section-body" style="text-align: center; font-size: 0.97rem; line-height: 1.75;">The power of Open Rent lies in what it enables for the organizations using it. We are creating the platform using a participatory design approach, working alongside local governments and organizations to ensure the platform addresses real operational needs rather than assumed ones.</p>
        <p class="section-body" style="margin-top: 1rem; text-align: center; font-size: 0.97rem; line-height: 1.75;">In the Bay Area, we are engaged with the Mountain View Housing Department as a founding design partner. Their rent registry is robust, but covers only a portion of the local market, making cross-analysis difficult. Open Rent is working to combine that registry with market-rate and affordable housing data across the city, giving city leaders a fuller picture of rental conditions and enabling more targeted policy decisions.</p>
      </div>
      <div>
        <img src="/Mountain-view.png" alt="City of Mountain View map" style="width: 56%; border-radius: 8px; display: block; margin: 0 auto;" />
      </div>
    </div>
  </div>
</section>

<section style="background: #F9F5F0; border-bottom: 1px solid var(--border); padding: 5rem 0;">
  <div class="section-inner">
    <div class="reveal">
      <h2 class="section-title" style="color: var(--near-black); text-align: center; margin-bottom: 1.5rem;">3. Local Partnerships and Engagement</h2>
      <p class="section-body" style="text-align: center; margin-bottom: 3rem; max-width: 700px; margin-left: auto; margin-right: auto;">Discussions with many local organizations in the Bay Area have and will continue to inform numerous use cases that drive how Open Rent is built, including the following.</p>
    </div>

    <div class="reveal use-cases-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
      <!-- Use Case 1 -->
      <div style="background: var(--white); border-radius: 8px; padding: 1.8rem; border: 1px solid var(--border);">
        <h4 style="font-family: var(--font-sans); font-size: 0.82rem; font-weight: 700; color: var(--near-black); margin-bottom: 1rem;">Use Case 1: Proactive Eviction Prevention and Targeted Resource Allocation</h4>
        <p style="font-size: 0.72rem; color: var(--dark-gray); margin-bottom: 0.8rem; line-height: 1.7;"><strong style="color: var(--near-black);">The User:</strong> Direct Service Providers and Housing Navigators</p>
        <p style="font-size: 0.72rem; color: var(--dark-gray); margin-bottom: 0.8rem; line-height: 1.7;"><strong style="color: var(--near-black);">The Issue:</strong> Lack real-time, neighborhood-level rent data, forcing them to react to imminent evictions rather than proactively distributing emergency assistance.</p>
        <p style="font-size: 0.72rem; color: var(--dark-gray); line-height: 1.7;"><strong style="color: var(--near-black);">Using Open Rent:</strong> Use interactive maps and predictive models to identify eviction risk and target outreach/emergency assistance.</p>
      </div>

      <!-- Use Case 2 -->
      <div style="background: var(--white); border-radius: 8px; padding: 1.8rem; border: 1px solid var(--border);">
        <h4 style="font-family: var(--font-sans); font-size: 0.82rem; font-weight: 700; color: var(--near-black); margin-bottom: 1rem;">Use Case 2: Strategic Investment and Affordable Housing Preservation</h4>
        <p style="font-size: 0.72rem; color: var(--dark-gray); margin-bottom: 0.8rem; line-height: 1.7;"><strong style="color: var(--near-black);">The User:</strong> Philanthropic Program Officers, Housing Agency Program Officers, and Affordable Housing Developers.</p>
        <p style="font-size: 0.72rem; color: var(--dark-gray); margin-bottom: 0.8rem; line-height: 1.7;"><strong style="color: var(--near-black);">The Issue:</strong> Struggle to evaluate affordable housing projects strategically because the necessary market and community data is expensive, fragmented, and proprietary.</p>
        <p style="font-size: 0.72rem; color: var(--dark-gray); line-height: 1.7;"><strong style="color: var(--near-black);">Using Open Rent:</strong> Overlay real-time rent and neighborhood data to identify affordable housing at risk of conversion, allowing them to prioritize capital investments for preservation.</p>
      </div>

      <!-- Use Case 3 -->
      <div style="background: var(--white); border-radius: 8px; padding: 1.8rem; border: 1px solid var(--border);">
        <h4 style="font-family: var(--font-sans); font-size: 0.82rem; font-weight: 700; color: var(--near-black); margin-bottom: 1rem;">Use Case 3: Data-Driven Policy Advocacy and Civic Engagement</h4>
        <p style="font-size: 0.72rem; color: var(--dark-gray); margin-bottom: 0.8rem; line-height: 1.7;"><strong style="color: var(--near-black);">The User:</strong> Housing Policy Advocates, Community Organizers, and Civic Leaders.</p>
        <p style="font-size: 0.72rem; color: var(--dark-gray); margin-bottom: 0.8rem; line-height: 1.7;"><strong style="color: var(--near-black);">The Issue:</strong> Rely on outdated or anecdotal information, lacking the current, standardized rental data needed to effectively drive systemic policy change.</p>
        <p style="font-size: 0.72rem; color: var(--dark-gray); line-height: 1.7;"><strong style="color: var(--near-black);">Using Open Rent:</strong> Use the integrated dataset to create localized visualizations and reports on affordability of rents at a neighborhood level and for specific occupations to inform policy changes.</p>
      </div>
    </div>

    <div class="reveal" style="margin-top: 3rem; text-align: center;">
      <p style="font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--mid-gray); margin-bottom: 1.2rem;">Based on learnings and inspiration shared by</p>
      <p class="partner-credits">
        Bay Area Metro · Palo Alto Forward · Mercy Housing · Terner Center · Federal Reserve Bank of San Francisco · Housing Authority of Santa Clara County · City of Palo Alto · Partnership for the Bay’s Future · Urban Habitat
      </p>
    </div>
  </div>
</section>

<section class="roadmap-section" id="roadmap">
  <div class="section-inner">
    <div class="reveal">
      <div class="section-label">Roadmap</div>
      <h2 class="section-title">18-month plan to expand across <em style="color: #1a1a1a; background: #FFD700; padding: 0.05em 0.15em; font-style: italic;">the Bay Area</em>.</h2>
    </div>
    <div class="timeline">
      <div class="timeline-item reveal" style="--i:0"><div class="timeline-dot" style="background: var(--near-black);">P1</div><div class="timeline-content"><div class="time-range">Oct 2025 – June 2026</div><h4>Foundation &amp; Bay Area Pilot</h4><p>Design and build data infrastructure, integrate metro-area-wide foundational data sets, integrate deep-dive data from Santa Clara, and build core user features. Launch the Bay Area pilot in June 2026.</p></div></div>
      <div class="timeline-item reveal" style="--i:1"><div class="timeline-dot" style="background: var(--accent);">P2</div><div class="timeline-content"><div class="time-range">Summer 2026 – Winter 2026/27</div><h4>Broaden &amp; Deepen</h4><p>Broaden and deepen data pipelines to cover the entire Bay Area, build estimation models (e.g., rent prices, vacancy), and expand user features (e.g., real time displacement risk heatmap) to tackle more use cases and support broader groups of stakeholders.</p></div></div>
      <div class="timeline-item reveal" style="--i:2"><div class="timeline-dot" style="background: var(--warm-accent);">P3</div><div class="timeline-content"><div class="time-range">2027 and Beyond</div><h4>Scale &amp; Expand</h4><p>Continue to expand data sets and additional user features. Explore replication in other metro areas beyond the Bay Area.</p></div></div>
    </div>
  </div>
</section>

<footer>
  <h2>Thank <em>you</em></h2>
  <p>Open, trusted rent data that powers economic opportunity.</p>
  <div class="footer-line"></div>
  <div class="footer-bottom">The Open Rent Initiative &middot; A 501(c)3 fiscally-sponsored project of the Policy Simulation Library Foundation &middot; 2026</div>
</footer>
