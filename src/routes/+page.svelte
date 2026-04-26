
<script lang="ts">
	import { onMount } from 'svelte';

	onMount(() => {
		const observerOptions = { threshold: 0.12, rootMargin: '0px 0px -30px 0px' };
		const observer = new IntersectionObserver((entries) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) entry.target.classList.add('visible');
			});
		}, observerOptions);
		document.querySelectorAll('.reveal, .reveal-scale').forEach((el) => observer.observe(el));

		const nav = document.getElementById('nav');
		const onScrollNav = () => {
			if (nav) nav.classList.toggle('scrolled', window.scrollY > 60);
		};
		window.addEventListener('scroll', onScrollNav, { passive: true });

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
	<title>The Open Rent Initiative</title>
</svelte:head>

<nav id="nav">
  <div class="nav-links">
    <a href="#problem">Problem</a>
    <a href="#solution">Solution</a>
    <a href="#roadmap">Roadmap</a>
    <a href="#funding">Funding</a>
  </div>
</nav>

<section class="hero">
  <div class="hero-bg" aria-hidden="true"></div>
  <div class="hero-content">
    <h1 class="hero-headline">
      <span class="hero-line hero-line--sans">The Open Rent Initiative</span>
    </h1>
    <p class="hero-sub">
      Today, critical decisions — from how banks should invest community reinvestment resources, to where rental
      assistance is targeted, to which neighborhoods are experiencing housing instability — are made with data that
      is <em>years old, imprecise, and often incomplete.</em>
    </p>
    <p class="hero-sub hero-sub--emphasis">We’re building the platform to solve this, free and open.</p>
    <div class="hero-sponsors">
      <p class="hero-sponsors-label">Made possible by:</p>
      <div class="hero-sponsors-logos">
        <img src="/logos/SFF.png" alt="San Francisco Foundation" />
        <img src="/logos/CZI.png" alt="Chan Zuckerberg Initiative" />
        <img src="/logos/PSL.png" alt="Policy Simulation Library" />
        <img src="/logos/citizen codex.png" alt="Citizen Codex" />
        <img src="/logos/SVCF.png" alt="Silicon Valley Community Foundation" />
      </div>
    </div>
    <div class="hero-ctas">
      <a class="hero-btn-primary" href="mailto:rent@citizencodex.com?subject=Let%27s%20schedule%20a%2030%2Dminute%20Open%20Rent%20briefing">Let's schedule a 30-min briefing →</a>
      <a class="hero-link-secondary" href="https://open-rent-initiative.vercel.app/" target="_blank" rel="noopener noreferrer">See the Prototype →</a>
    </div>
    <div class="hero-scroll-cue">
      <span>Scroll to explore</span>
      <div class="scroll-line"></div>
    </div>
  </div>
</section>

<section class="the-problem-section" id="problem" aria-labelledby="problem-headline">
  <div class="section-inner problem-v3">
    <div class="problem-v3__rule" aria-hidden="true"></div>
    <div class="problem-v3__eyebrow">The Problem</div>
    <h2 id="problem-headline" class="problem-v3__headline">
      Housing policy and investment decisions are made <strong class="problem-v3__headline-accent">blind</strong> to the facts on the ground.
    </h2>

    <div class="problem-v3-chart-block">
      <header class="problem-v3-chart-block__hdr">
        <p class="problem-v3-chart-block__finding">More than 50% of the rental stock in the Bay Area is invisible.</p>
        <p class="problem-v3-chart-block__title">Share of rental stock by property type, 2024</p>
        <p class="problem-v3-chart-block__subtitle">Bay Area Markets · Composition + Data Quality</p>
      </header>

      <div class="problem-v3-chart">
      <svg
        class="problem-v3-chart-embed"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewBox="0 0 1505 812"
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label="Rental stock composition chart for San Francisco, San Jose, and Oakland with poor and okay visibility callouts"
      >
        <image
          href="/problem-chart-overview-v3.svg"
          xlink:href="/problem-chart-overview-v3.svg"
          width="1505"
          height="812"
          preserveAspectRatio="xMidYMid meet"
        />
      </svg>
    </div>

    <div class="problem-v3-shortfall">
      <h2 class="problem-v3-shortfall__title">Problems with current rent data.</h2>

      <div class="problem-v3-shortfall__grid">
        <article class="problem-v3-reason">
          <h3 class="problem-v3-reason__title">Too Coarse</h3>
          <p class="problem-v3-reason__body">The American Community Survey reports at the census tract or county level. Property-level variation — the site at which displacement actually happens — is invisible.</p>
        </article>

        <article class="problem-v3-reason">
          <h3 class="problem-v3-reason__title">Missing Communities</h3>
          <p class="problem-v3-reason__body">Zillow's Observed Rent Index, another widely used public data set, only covers markets within Zillow's footprint.</p>
        </article>

        <article class="problem-v3-reason">
          <h3 class="problem-v3-reason__title">Years Behind</h3>
          <p class="problem-v3-reason__body">The ACS — the U.S. Census's most precise measurement of rent — uses 5-year rolling averages, released one to two years after collection. By the time it's published, the rents it describes are gone.</p>
        </article>

        <article class="problem-v3-reason">
          <h3 class="problem-v3-reason__title">Highly Fragmented</h3>
          <p class="problem-v3-reason__body">Other data sources sit behind expensive paywalls (e.g., CoStar costing over $10K per user on average), in multiple listing sites (e.g., Craigslist), or in siloed databases (e.g., rent registries).</p>
        </article>
      </div>
    </div>
    </div>
  </div>
</section>

<section class="disparity-section" style="padding: 0;">
  <div style="width: 100%; height: 80vh; min-height: 600px;">
    <iframe id="mapEmbed" src="/map" title="Bay Area rent data map" style="width: 100%; height: 100%; border: none;" loading="lazy"></iframe>
  </div>
</section>

<section class="impact-problem-section" aria-labelledby="impact-problem-headline">
  <div class="section-inner impact-problem-inner">
    <header class="reveal">
      <div class="impact-problem-rule" aria-hidden="true"></div>
      <div class="impact-problem-eyebrow">Impact of Data Deficiencies</div>
      <h3 id="impact-problem-headline" class="impact-problem-headline">
        Unable to target early interventions, limited resources are misallocated, and housing stability is poorly
        managed.
      </h3>
    </header>

    <div class="impact-problem-grid reveal" style="transition-delay: 0.1s;">
      <article class="impact-problem-card">
        <div class="impact-problem-card-glyph" aria-hidden="true">
          <svg viewBox="0 0 70 48" width="70" height="48">
            <rect x="0"  y="0"  width="13" height="13" rx="1.5" fill="#F5F5F5" opacity="0.85"/>
            <rect x="19" y="0"  width="13" height="13" rx="1.5" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.28"/>
            <rect x="38" y="0"  width="13" height="13" rx="1.5" fill="#F5F5F5" opacity="0.85"/>
            <rect x="57" y="0"  width="13" height="13" rx="1.5" fill="#F5C529"/>
            <rect x="0"  y="18" width="13" height="13" rx="1.5" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.28"/>
            <rect x="19" y="18" width="13" height="13" rx="1.5" fill="#F5F5F5" opacity="0.85"/>
            <rect x="38" y="18" width="13" height="13" rx="1.5" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.28"/>
            <rect x="57" y="18" width="13" height="13" rx="1.5" fill="#F5F5F5" opacity="0.85"/>
            <rect x="0"  y="36" width="13" height="13" rx="1.5" fill="#F5F5F5" opacity="0.85"/>
            <rect x="19" y="36" width="13" height="13" rx="1.5" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.28"/>
            <rect x="38" y="36" width="13" height="13" rx="1.5" fill="#F5F5F5" opacity="0.85"/>
            <rect x="57" y="36" width="13" height="13" rx="1.5" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.28"/>
          </svg>
        </div>
        <h4 class="impact-problem-card-title">Invisible Housing Stock</h4>
        <p class="impact-problem-card-lead">Preservation funders cannot protect what they cannot see.</p>
        <p class="impact-problem-card-body">Tenants in unsubsidized affordable units — often those most at risk of displacement — remain invisible to the agencies working to keep them housed.</p>
      </article>

      <article class="impact-problem-card">
        <div class="impact-problem-card-glyph" aria-hidden="true">
          <svg viewBox="0 0 70 70" width="70" height="70">
            <circle cx="26" cy="44" r="24" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.28"/>
            <circle cx="26" cy="44" r="17" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.42"/>
            <circle cx="26" cy="44" r="10" fill="none" stroke="#F5F5F5" stroke-width="0.8" opacity="0.58"/>
            <circle cx="26" cy="44" r="3"  fill="#F5F5F5" opacity="0.85"/>
            <line x1="26" y1="44" x2="58" y2="12" stroke="#F5F5F5" stroke-width="0.6" stroke-dasharray="2,2.5" opacity="0.4"/>
            <circle cx="58" cy="12" r="4.5" fill="#F5C529"/>
          </svg>
        </div>
        <h4 class="impact-problem-card-title">Imprecise Policy Tools</h4>
        <p class="impact-problem-card-lead">Rules built on coarse data miss their mark — and the failure is hard to diagnose.</p>
        <p class="impact-problem-card-body">Rent stabilization, subsidy rates, and analogous instruments are calibrated against outdated inputs, producing over- and under-correction the underlying data cannot explain.</p>
      </article>

      <article class="impact-problem-card">
        <div class="impact-problem-card-glyph" aria-hidden="true">
          <svg viewBox="0 0 72 60" width="72" height="60">
            <line x1="0" y1="59.5" x2="72" y2="59.5" stroke="#F5F5F5" stroke-width="0.6" opacity="0.35"/>
            <rect x="0"  y="0"  width="14" height="60" rx="1" fill="#F5C529"/>
            <rect x="20" y="44" width="14" height="16" rx="1" fill="#F5F5F5" opacity="0.32"/>
            <rect x="40" y="48" width="14" height="12" rx="1" fill="#F5F5F5" opacity="0.32"/>
            <rect x="58" y="46" width="14" height="14" rx="1" fill="#F5F5F5" opacity="0.32"/>
          </svg>
        </div>
        <h4 class="impact-problem-card-title">An Unfair Playing Field</h4>
        <p class="impact-problem-card-lead">The data gap is a power gap.</p>
        <p class="impact-problem-card-body">Corporate owners purchase property-level intelligence from CoStar and RealPage and convert it into acquisition strategy. Tenants, city housing departments, legal-aid clinics, and community lenders have no equivalent.</p>
      </article>

      <article class="impact-problem-card impact-problem-card--accent">
        <div class="impact-problem-card-glyph" aria-hidden="true">
          <svg viewBox="0 0 96 48" width="96" height="48">
            <line x1="0" y1="24" x2="96" y2="24" stroke="#303334" stroke-width="0.6" opacity="0.32"/>
            <path d="M 22 24 Q 48 6, 74 24" fill="none" stroke="#303334" stroke-width="0.6" stroke-dasharray="2.5,2.5" opacity="0.45"/>
            <circle cx="17" cy="24" r="6" fill="#F5C529"/>
            <circle cx="78" cy="24" r="6" fill="none" stroke="#303334" stroke-width="1.2" opacity="0.7"/>
            <text x="17" y="44" text-anchor="middle" font-size="7" fill="#858585" font-family="Roboto Mono, monospace" letter-spacing="1">HARM</text>
            <text x="78" y="44" text-anchor="middle" font-size="7" fill="#858585" font-family="Roboto Mono, monospace" letter-spacing="1">RESPONSE</text>
          </svg>
        </div>
        <h4 class="impact-problem-card-title">Reactive, Not Proactive</h4>
        <p class="impact-problem-card-lead">Without property-level signals, intervention arrives only after harm.</p>
        <p class="impact-problem-card-body">Agencies and service providers can respond, but only downstream — long after emergency rental assistance or targeted policy could have shifted the outcome.</p>
      </article>
    </div>
  </div>
</section>

<section class="solution-section" id="solution" aria-labelledby="solution-headline">
  <div class="section-inner sol-v2">
    <header class="sol3-header reveal">
      <span class="sol3-yellow-bar" aria-hidden="true"></span>
      <span class="sol3-tag">The Solution</span>
      <h2 id="solution-headline" class="sol3-headline">How Open Rent solves this problem.</h2>
      <p class="sol3-subtitle">A City of Mountain View case study.</p>
    </header>

    <div class="sol3-comparison reveal" style="transition-delay: 0.1s;">
      <article class="sol3-card sol3-card--light">
        <div class="sol3-card-tag">Current State</div>
        <h3 class="sol3-card-title">A patchwork of sources.</h3>

        <div class="sol3-files-canvas" aria-hidden="true">
          <svg viewBox="0 0 600 180" preserveAspectRatio="none">
            <g stroke="rgba(48,51,52,0.25)" stroke-width="1" stroke-dasharray="3 4" fill="none">
              <path d="M 110 28 L 220 62" />
              <path d="M 220 62 L 130 100" />
              <path d="M 130 100 L 200 138" />
              <path d="M 220 62 L 470 40" />
              <path d="M 470 40 L 510 90" />
              <path d="M 510 90 L 480 135" />
              <path d="M 200 138 L 480 135" />
            </g>
          </svg>
          <span class="sol3-file-chip sol3-file-chip--f1">rent_registry.xlsx</span>
          <span class="sol3-file-chip sol3-file-chip--f2">section8.pdf</span>
          <span class="sol3-file-chip sol3-file-chip--f3">zillow_zori.csv</span>
          <span class="sol3-file-chip sol3-file-chip--f4">assessor.csv</span>
          <span class="sol3-file-chip sol3-file-chip--f5">LIHTC_2024.csv</span>
          <span class="sol3-file-chip sol3-file-chip--f6">parcels.geojson</span>
          <span class="sol3-file-chip sol3-file-chip--f7">acs_2023.xlsx</span>
        </div>

        <ul class="sol3-bullets">
          <li>Rental data is fragmented across disconnected systems, requiring teams to manually download and reconcile files.</li>
          <li>Key rental categories are missing — single-family rentals, duplexes, BMR units, and fully affordable housing (LIHTC, Section&nbsp;8).</li>
          <li>Reporting is heavily manual; spreadsheet updates and infographics consume staff capacity each cycle.</li>
          <li>Unit-level rent changes cannot be tracked over time, nor can actual rents be compared against market rates.</li>
        </ul>
      </article>

      <article class="sol3-card sol3-card--dark">
        <div class="sol3-card-tag">City of Mountain View and Open Rent</div>
        <h3 class="sol3-card-title">Unified Canvas and Dataset.</h3>

        <div class="sol3-screenshot-frame">
          <img
            src="/open-rent-mountain-view-case-study.jpg"
            alt="Open Rent Mountain View case study: data tools and platform showing property-level map with selected property and rent benchmarks."
            width="1024"
            height="720"
            loading="lazy"
            decoding="async"
          />
        </div>

        <ul class="sol3-bullets">
          <li>Consolidated data offering a full view of rental stock across all market types — affordable, market-rate, stabilized, single-family rentals.</li>
          <li>Visualization tools that allow staff to explore rental stock at every level of geographic granularity, from individual unit to citywide.</li>
          <li>Analytical tools for longitudinal and comparative market analysis, with full audit history for every data point.</li>
        </ul>
      </article>
    </div>
  </div>
</section>

<section class="feat-section" id="features" aria-labelledby="feat-headline">
  <div class="section-inner feat-inner">
    <header class="feat-header reveal">
      <span class="feat-rule" aria-hidden="true"></span>
      <span class="feat-eyebrow">The Solution</span>
      <h2 id="feat-headline" class="feat-headline">
        Overview of the<br><em>Open Rent Initiative.</em>
      </h2>
    </header>

    <div class="feat-principles reveal" style="transition-delay: 0.08s;">
      <article class="feat-principle">
        <span class="feat-principle-num">01 / What</span>
        <h3 class="feat-principle-title">What we are building</h3>
        <p class="feat-principle-body">
          A comprehensive open-data platform with engagement tools and products that make rental data and
          insight readily accessible to policymakers, researchers, and the public.
        </p>
      </article>

      <article class="feat-principle">
        <span class="feat-principle-num">02 / How</span>
        <h3 class="feat-principle-title">How we are building it</h3>
        <p class="feat-principle-body">
          Comprehensive and granular: integrating data from diverse channels at the property level, or at the
          finest geographic resolution available within each market.
        </p>
      </article>

      <article class="feat-principle">
        <span class="feat-principle-num">03 / Principle</span>
        <h3 class="feat-principle-title">Our guiding principle</h3>
        <p class="feat-principle-body">
          Partner <em>locally</em> with those who know the regional market and its data well — leaning on
          creative sourcing and model estimation where direct data is unavailable.
        </p>
      </article>
    </div>

    <div class="feat-demo reveal" style="transition-delay: 0.16s;">
      <div class="feat-demo-caption">
        <span class="feat-demo-caption-lhs"><em>See the platform in motion.</em></span>
        <span class="feat-demo-caption-rhs">Platform Preview · v0.1</span>
      </div>

      <figure class="feat-frame">
        <div class="feat-frame-topbar">
          <span class="feat-frame-brand">Open Rent</span>
          <span class="feat-frame-lang">English ⌄</span>
        </div>
        <video autoplay loop muted playsinline class="feat-frame-media">
          <source src="/Rent%20Tool%20Video.mov" type="video/quicktime" />
          <source src="/Rent%20Tool%20Video.mov" type="video/mp4" />
        </video>

        <figcaption class="feat-demo-footer">
          <span>Fig. 01 · Interactive property-level rental canvas</span>
          <span class="feat-demo-footer-src">Source: Open Rent prototype, 2026</span>
        </figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="uc-section" id="usecases">
  <div class="section-inner uc-v2">
    <header class="uc3-header reveal">
      <span class="uc3-yellow-bar" aria-hidden="true"></span>
      <span class="uc3-tag">Use Cases</span>
      <h2 class="uc3-title">Where Open Rent could add value <em>for stakeholders.</em></h2>
    </header>

    <div class="uc3-grid reveal" style="transition-delay: 0.08s;">
      <article class="uc3-case">
        <div class="uc3-case-meta">
          <span class="uc3-case-meta-lhs">Use Case 01</span>
          <span class="uc3-case-meta-rhs">Frontline Services</span>
        </div>
        <h3 class="uc3-case-title">Direct service providers.</h3>
        <p class="uc3-problem">
          Case workers at tenant-counseling clinics, legal-aid offices, and homelessness-prevention programs
          triage limited resources without knowing which parcels and blocks face the greatest housing-stability risk.
        </p>
        <div class="uc3-callout">
          <div class="uc3-callout-tag">With Open Rent</div>
          <p>
            Property-level signals from rent spikes, ownership changes, and eviction-filing patterns — so frontline
            teams can deploy outreach, emergency rental assistance, and right-to-counsel services to the specific
            parcels where tenants are at risk.
          </p>
        </div>
      </article>

      <article class="uc3-case">
        <div class="uc3-case-meta">
          <span class="uc3-case-meta-lhs">Use Case 02</span>
          <span class="uc3-case-meta-rhs">Local Government</span>
        </div>
        <h3 class="uc3-case-title">City housing staff and local government.</h3>
        <p class="uc3-problem">
          Cities lack visibility into the full rental stock, making it difficult to develop sound policy, enforce
          existing regulations, and provide the public with credible transparency.
        </p>
        <div class="uc3-callout">
          <div class="uc3-callout-tag">With Open Rent</div>
          <p>
            A live, property-level view of rental stock and rental data — so cities can move from reactive enforcement
            to proactive, property-level compliance monitoring and targeted housing-stability policy.
          </p>
        </div>
      </article>

      <article class="uc3-case">
        <div class="uc3-case-meta">
          <span class="uc3-case-meta-lhs">Use Case 03</span>
          <span class="uc3-case-meta-rhs">Community Finance</span>
        </div>
        <h3 class="uc3-case-title">CRA teams at community banks and lenders.</h3>
        <p class="uc3-problem">
          CRA investment decisions rely on HUD assessment-area data that is both too coarse to locate specific LMI
          investment opportunities and too stale to reflect current market conditions. By the time a CRA team has
          current FMRs, the tight-market window has closed and LMI households have already been priced out.
        </p>
        <div class="uc3-callout">
          <div class="uc3-callout-tag">With Open Rent</div>
          <p>
            Real-time LMI rental stock and rent data at the property level within each assessment area — so CRA
            teams can target capital to specific parcels and neighborhoods where it qualifies, and document impact
            their examiners and boards can defend.
          </p>
        </div>
      </article>

      <article class="uc3-case">
        <div class="uc3-case-meta">
          <span class="uc3-case-meta-lhs">Use Case 04</span>
          <span class="uc3-case-meta-rhs">Preservation</span>
        </div>
        <h3 class="uc3-case-title">Affordable-housing preservation funders and developers.</h3>
        <p class="uc3-problem">
          NOAH (naturally occurring affordable housing) is invisible in tract-level data; preservation funds cannot
          prioritize individual parcels they cannot see, and the tenants in unsubsidized affordable units are often
          at the highest risk of displacement.
        </p>
        <div class="uc3-callout">
          <div class="uc3-callout-tag">With Open Rent</div>
          <p>
            A property-level inventory of NOAH and at-risk affordable stock, parcel by parcel, with risk signals
            from ownership changes, permit activity, and rent trajectories.
          </p>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="roadmap-v2 dark centered" id="roadmap">
  <div class="section-inner rm-inner">
    <span class="rm-eyebrow">Roadmap</span>
    <h2 class="rm-title">An 18-month plan to expand across <em class="rm-accent">California and Minnesota.</em></h2>

    <div class="rm-phases">
      <div class="rm-phase">
        <div class="rm-when">Oct 2025 → Jun 2026</div>
        <h3 class="rm-phase-title">Foundation &amp; Mountain View pilot</h3>
        <p>Build the core data infrastructure. Integrate Bay Area foundational datasets. Launch the Mountain View pilot in June 2026.</p>
      </div>
      <div class="rm-phase">
        <div class="rm-when">Summer 2026 → Winter 2026/27</div>
        <h3 class="rm-phase-title">Broaden &amp; deepen</h3>
        <p>Extend data pipelines to cover the entire Bay Area, including building estimation models where relevant (rent prices, vacancy, displacement risk). Launch Los Angeles Metro and Twin Cities Metro expansions and pilots.</p>
      </div>
      <div class="rm-phase">
        <div class="rm-when">2027 and beyond</div>
        <h3 class="rm-phase-title">Scale &amp; expand</h3>
        <p>Expand data sets and user features. Expand across California and Minnesota. Begin expansion to other states.</p>
      </div>
    </div>
  </div>
</section>

<section class="funding-v2" id="funding">
  <div class="funding-inner">
    <span class="funding-yellow-bar" aria-hidden="true"></span>
    <span class="funding-eyebrow">Funding</span>
    <h2 class="funding-title">Funding the <em>next phase.</em></h2>
    <p class="funding-lead">
      Open Rent is welcoming new funders to support its expansion across the Bay Area and the launch of a
      Los&nbsp;Angeles pilot.
    </p>
    <p class="funding-lead">
      We are also open to partnerships focused on a specific jurisdiction — Oakland, L.A.&nbsp;City, or another market — or
      on a specific question, such as estimating housing-stability risk or building tools for local government housing
      staff.
    </p>
    <p class="funding-closing">We would value the conversation.</p>
    <div class="funding-actions">
      <a class="funding-link funding-link--primary" href="mailto:rent@citizencodex.com?subject=Let%27s%20schedule%20%E2%80%94%20Open%20Rent%20funding%20conversation">
        <span class="funding-link-label">Let's schedule a briefing</span>
        <span class="funding-link-arrow">→</span>
      </a>
      <a class="funding-link funding-link--secondary" href="/funder-brief.pdf">
        <span class="funding-link-label">Download the funder brief</span>
        <span class="funding-link-arrow">→</span>
      </a>
    </div>
  </div>
</section>

<footer>
  <div class="footer-bottom">
    The Open Rent Initiative &middot; A 501(c)(3) fiscally-sponsored project of the Policy Simulation Library Foundation
    &middot; 2026
  </div>
</footer>
