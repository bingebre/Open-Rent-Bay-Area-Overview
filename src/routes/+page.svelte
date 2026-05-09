
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
      Today, critical decisions — like where and how rental assistance is targeted and how to intervene in
      neighborhoods experiencing housing instability — are made with data that is years old, imprecise, and often
      incomplete.
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
      Housing policy and investment decisions are made with <strong class="problem-v3__headline-accent">poor information</strong>.
    </h2>

    <div class="problem-v3-chart-block">
      <div class="problem-v3-map-wrap">
        <iframe
          id="mapEmbed"
          src="/map"
          title="Bay Area rent data map"
          style="width: 100%; height: 100%; border: none;"
          loading="lazy"
        ></iframe>
      </div>
    </div>
  </div>
</section>

<section class="the-problem-section" id="problem-b" aria-labelledby="problem-headline-b">
  <div class="section-inner problem-v3">
    <div class="problem-v3__rule" aria-hidden="true"></div>
    <div class="problem-v3__eyebrow">The Problem</div>
    <h2 id="problem-headline-b" class="problem-v3__headline">
      Highly Fragmented Rent Data Creates Big Blind Spots
    </h2>
    <p class="problem-v3__subheadline">
      Beyond the gaps in ACS and Zillow, other sources are paywalled (e.g., CoStar), scattered across listing sites (e.g., Craigslist), or siloed in rent registries and other government databases. All of them miss single-family rentals and small buildings entirely.
    </p>

    <div class="problem-v3-chart-block">
      <header class="problem-v3-chart-block__hdr">
        <p class="problem-v3-chart-block__title">More than 50% of rental stock in the Bay Area is invisible.</p>
        <p class="problem-v3-chart-block__subtitle">Share of rental stock by property type, 2024</p>
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

      <figure class="problem-v3-chart-after">
        <h3 class="problem-v3-chart-after__title">High data fragmentation across types of properties</h3>
        <img
          src="/rent-data-fragmentation.jpg"
          alt="Data fragmentation: isometric neighborhood map showing housing types and the many separate data sources needed to describe rental stock, including listings, paywalled sources, rent registry, and public assessor data."
          width="1024"
          height="551"
          loading="lazy"
          decoding="async"
        />
      </figure>
    </div>
  </div>
</section>

<section class="solution-section" id="solution" aria-labelledby="solution-headline">
  <div class="section-inner sol-v2">
    <header class="sol3-header reveal">
      <span class="sol3-yellow-bar" aria-hidden="true"></span>
      <span class="sol3-tag">The Solution - City of Mountain View Case Study</span>
      <h2 id="solution-headline" class="sol3-headline">How Open Rent solves this problem</h2>
      <p class="sol3-subheadline">
        The Open Rent Initiative is building the nation's first open, public rent data infrastructure, connecting and standardizing building-level rent information across regions so governments and nonprofits can act quickly to help families find homes and stay housed.
      </p>
    </header>

    <div class="sol3-comparison reveal" style="transition-delay: 0.1s;">
      <article class="sol3-card sol3-card--dark">
        <h3 class="sol3-card-title">How we are working with the City of Mountain View</h3>

        <ul class="sol3-bullets">
          <li>Compiling a holistic view of their rental housing stock - Consolidated data offering a full view of rental stock across all market types (affordable, market-rate, stabilized, single family rentals, etc.) to inform policymaking and addressing housing affordability.</li>
          <li>Visualization tools that let staff explore rental stock at multiple levels of geographic granularity, from individual unit to citywide to inform key decisionmakers.</li>
          <li>Analytical tools for longitudinal and comparative market analysis so that limited local resources can be focused to where they are most needed.</li>
        </ul>

        <div class="sol3-dashboard-pair">
          <figure class="sol3-dashboard-pair__fig">
            <img
              src="/solution-mv-rental-overview.png"
              alt="Open Rent dashboard: Mountain View rental stock overview with key metrics, rent comparison, and distribution by program type."
              width="721"
              height="664"
              loading="lazy"
              decoding="async"
            />
          </figure>
          <figure class="sol3-dashboard-pair__fig">
            <img
              src="/solution-mv-rental-composition.png"
              alt="Open Rent dashboard: Mountain View rental stock composition by program type across ZIP codes."
              width="718"
              height="637"
              loading="lazy"
              decoding="async"
            />
          </figure>
        </div>
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
        Overview of the Open Rent Initiative
      </h2>
    </header>

    <div class="feat-principles reveal" style="transition-delay: 0.08s;">
      <article class="feat-principle">
        <span class="feat-principle-num">01 / What</span>
        <h3 class="feat-principle-title">What we're building</h3>
        <p class="feat-principle-body">
          A comprehensive open-data platform with engagement tools and products that make rental data and
          insight readily accessible to policymakers, researchers, and the public.
        </p>
      </article>

      <article class="feat-principle">
        <span class="feat-principle-num">02 / How</span>
        <h3 class="feat-principle-title">How we're building it</h3>
        <p class="feat-principle-body">
          Integrating granular data from diverse channels at the property level, or at the
          finest geographic resolution available within each market.
        </p>
      </article>

      <article class="feat-principle">
        <span class="feat-principle-num">03 / Principle</span>
        <h3 class="feat-principle-title">Our guiding principle</h3>
        <p class="feat-principle-body">
          Partner <em>locally</em> with those who know the community and its data well — leaning on
          creative sourcing and model estimation where direct data is unavailable.
        </p>
      </article>
    </div>
  </div>
</section>

<section class="uc-section" id="usecases" aria-labelledby="usecases-headline">
  <div class="section-inner uc-v2">
    <header class="uc3-header reveal">
      <span class="uc3-yellow-bar" aria-hidden="true"></span>
      <span class="uc3-tag">Use Cases</span>
      <h2 id="usecases-headline" class="uc3-headline">What Open Rent Offers</h2>
      <p class="uc3-subheadline">
        Open Rent closes the information gap for organizations supporting low- and moderate-income families
      </p>
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
        <h3 class="uc3-case-title">Community Reinvestment Act (CRA) teams at community banks and lenders.</h3>
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
        <p>Extend data pipelines to cover the entire Bay Area, including building estimation models where relevant (rent prices, vacancy, displacement risk). Launch Los Angeles Metro and deepen and expand existing collaboration with HousingLink in Minnesota.</p>
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
