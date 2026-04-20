
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
      <span class="hero-line hero-line--sans">The Open Rent Initiative —</span>
      <span class="hero-line hero-line--serif">parcel-level, timely rental data</span>
      <span class="hero-line hero-line--sans">for the public-interest sector.</span>
    </h1>
    <p class="hero-sub">
      Granular and timely rental housing data — so cities, affordable housing funders, and providers of housing
      stability programs can direct capital, target services, and shape policy in service of
      <strong>low and moderate income (LMI) families</strong>.
    </p>
    <dl class="hero-meta-grid">
      <div class="hero-meta-row">
        <dt>License</dt>
        <dd>Free, Open Source (MIT)</dd>
      </div>
      <div class="hero-meta-row">
        <dt>First pilot</dt>
        <dd>Mountain View, CA · June 2026</dd>
      </div>
      <div class="hero-meta-row">
        <dt>Geographic scope</dt>
        <dd>
          Bay Area / LA Metro → California → National<br />
          Twin Cities Metro → Minnesota → National
        </dd>
      </div>
      <div class="hero-meta-row">
        <dt>Fiscal sponsor</dt>
        <dd>501(c)(3) initiative, Policy Simulation Library Foundation</dd>
      </div>
    </dl>
    <div class="hero-ctas">
      <a class="hero-btn-primary" href="mailto:?subject=Request%3A%2030%2Dminute%20Open%20Rent%20briefing">Request a 30-min briefing →</a>
      <a class="hero-link-secondary" href="/map">See the Prototype →</a>
    </div>
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
    <div class="hero-scroll-cue">
      <span>Scroll to explore</span>
      <div class="scroll-line"></div>
    </div>
  </div>
</section>

<section class="context-section" id="problem">
  <!-- Bay Area Map Background -->
  <div class="context-map-bg" id="contextMap">
    <img src="/embedded/img-002.png" alt="" style="width: 100%; border-radius: 4px;" />
  </div>

  <div class="context-layout" style="position: relative; z-index: 2;">
    <aside class="context-rail reveal">
      <div class="context-rail-label">Context</div>
      <div class="context-rail-sub">The data gap</div>
    </aside>

    <div class="context-main">
      <div class="reveal">
        <div class="context-eyebrow">The landscape in 2026</div>
      </div>
      <div class="context-para reveal" data-speed="0.03">
        <h2 class="context-title">
          Housing decisions are being made on data that’s
          <em class="context-title-accent">too coarse, too old and highly fragmented.</em>
        </h2>
      </div>
      <div class="context-para reveal" data-speed="0.05">
        <p class="context-body">
          Cities, affordable housing funders, the federal government, tenant-counseling and legal-aid
          organizations, and researchers all need the same thing: rental market data that resolves to the parcel
          and the block, and that reflects what’s happening this quarter — not 2 years ago.
        </p>
      </div>
      <div class="context-para reveal" data-speed="0.07">
        <p class="context-body context-body--emphasis">They don’t have it.</p>
      </div>
      <div class="context-para reveal" data-speed="0.09">
        <p class="context-body">
          The data that sets federal voucher rates, triggers CRA investments, targets housing stability services,
          and shapes rental housing policy is reported at the county or tract level, runs 2–5 years behind the
          actual market, sits behind expensive paywalls and/or must be pieced together from many sources. By the
          time this data is usable, rents have moved, notices have been served, tenants have been displaced, and
          the intervention window has closed.
        </p>
      </div>
    </div>
  </div>
</section>

<section class="the-problem-section">
  <div class="section-inner problem-inner">
    <div class="reveal">
      <div class="section-label problem-label">The Problem</div>
      <h3 class="problem-heading">Why the standard data sources fall short</h3>
    </div>

    <div class="problem-cards reveal" style="transition-delay: 0.1s;">
      <article class="problem-example-card">
        <h4>Too coarse</h4>
        <p>
          The American Community Survey reports at the tract or county level. The parcel-level variation where
          displacement actually happens is invisible.
        </p>
      </article>
      <article class="problem-example-card">
        <h4>Spatial gaps</h4>
        <p>
          Zillow’s Observed Rent Index, another widely used public data set, only covers markets in Zillow’s
          footprint.
        </p>
      </article>
      <article class="problem-example-card">
        <h4>Years behind</h4>
        <p>
          The ACS uses 5-year rolling averages, released 1–2 years after collection. By the time it’s published,
          the rents it describes are gone.
        </p>
      </article>
      <article class="problem-example-card">
        <h4>Highly fragmented</h4>
        <p>
          Other data sources sit behind expensive paywalls (e.g., CoStar), in multiple listing sites (e.g.,
          Craigslist), or in siloed databases (e.g., rent registries).
        </p>
      </article>
    </div>

    <figure class="evidence-figure reveal" style="transition-delay: 0.15s;" aria-labelledby="evidence-title">
      <div class="figure-header">
        <p class="figure-kicker">More than 50% of the rental stock in the Bay Area is invisible</p>
        <h3 id="evidence-title">Share of rental stock by property type, 2024</h3>
        <div class="figure-meta">Bay Area markets · Composition + data quality</div>
      </div>

      <div class="figure-body">
        <div
          class="chart-area"
          role="img"
          aria-label="Stacked bar chart. Rental stock composition by property type for National, San Francisco, San Jose, and Oakland."
        >
          <div class="chart-grid">
            <div class="y-labels" aria-hidden="true">
              <div class="y-label" style="flex: 13"><div>Townhomes</div></div>
              <div class="y-label" style="flex: 30"><div>Single family rentals</div></div>
              <div class="y-label" style="flex: 27">
                <div>Small multifamily<span class="label-sub">(5–20 units)</span></div>
              </div>
              <div class="y-label" style="flex: 30">
                <div>Large multifamily<span class="label-sub">(20+ units)</span></div>
              </div>
            </div>

            <div class="bars-row">
              <div class="bar-col">
                <div class="bar">
                  <div class="seg seg-th" style="flex: 8.5">8.5</div>
                  <div class="seg seg-sfr" style="flex: 31.1">31.1</div>
                  <div class="seg seg-sm" style="flex: 27.3">27.3</div>
                  <div class="seg seg-lm" style="flex: 33.1">33.1</div>
                </div>
              </div>

              <div class="bar-col">
                <div class="bar">
                  <div class="seg seg-th" style="flex: 8.6">8.6</div>
                  <div class="seg seg-sfr" style="flex: 15.6">15.6</div>
                  <div class="seg seg-sm" style="flex: 31.4">31.4</div>
                  <div class="seg seg-lm" style="flex: 44.5">44.5</div>
                </div>
              </div>

              <div class="bar-col">
                <div class="bar">
                  <div class="seg seg-th" style="flex: 11.9">11.9</div>
                  <div class="seg seg-sfr" style="flex: 24">24</div>
                  <div class="seg seg-sm" style="flex: 20.4">20.4</div>
                  <div class="seg seg-lm" style="flex: 43.7">43.7</div>
                </div>
              </div>

              <div class="bar-col">
                <div class="bar">
                  <div class="seg seg-th" style="flex: 10">10</div>
                  <div class="seg seg-sfr" style="flex: 28.8">28.8</div>
                  <div class="seg seg-sm" style="flex: 22.8">22.8</div>
                  <div class="seg seg-lm" style="flex: 38.4">38.4</div>
                </div>
              </div>
            </div>

            <div class="x-labels" aria-hidden="true">
              <div>National</div>
              <div>San Francisco</div>
              <div>San Jose</div>
              <div>Oakland</div>
            </div>
          </div>
        </div>

        <div class="quality-list">
          <div class="q-item" style="flex: 13">
            <p>
              <span class="q-tag q-poor">Poor</span>
              <span class="q-text">Reliance on ACS aggregate statistics and some government data.</span>
            </p>
          </div>
          <div class="q-item" style="flex: 30">
            <p>
              <span class="q-tag q-poor">Poor</span>
              <span class="q-text"
                >Most organizations rely on ACS and Zillow; other data is highly fragmented or nonexistent.</span>
            </p>
          </div>
          <div class="q-item" style="flex: 27">
            <p>
              <span class="q-tag q-poor">Poor</span>
              <span class="q-text"
                >Most organizations rely on ACS and Zillow; other sources highly fragmented (e.g., state data, rent
                registry, listings).</span>
            </p>
          </div>
          <div class="q-item" style="flex: 30">
            <p>
              <span class="q-tag q-ok">Okay</span>
              <span class="q-text"
                >Many organizations rely on ACS and Zillow; those that can afford it purchase data from CoStar and
                similar providers — and even then, the purchased data is only market-rate.</span>
            </p>
          </div>
        </div>
      </div>

      <div class="figure-source">
        Source: U.S. Census;
        <a
          href="https://www.redfin.com/news/rental-housing-multifamily-vs-single-family/"
          target="_blank"
          rel="noopener noreferrer">Redfin</a>
      </div>
    </figure>
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
      <div class="section-label impact-problem-label">Impact</div>
      <h3 class="impact-problem-title">
        What breaks when the data is <em>too coarse, too old, and fragmented</em>
      </h3>
    </div>

    <div class="impact-cards reveal" style="transition-delay: 0.1s;">
      <article class="impact-card">
        <div class="card-head">
          <h4>Invisible housing stock</h4>
          <span class="impact-tag impact-tag-terra">NOAH</span>
        </div>
        <p>
          Single-family rentals and Naturally Occurring Affordable Housing (NOAH) are buried inside tract-level
          averages when they show up at all. Preservation funders can't protect what they can't see at the parcel
          level, and the tenants in those units — often the most vulnerable to displacement — are invisible to the
          agencies trying to keep them housed.
        </p>
        <div class="metric">
          <div class="metric-label">Rental stock invisible</div>
          <div class="metric-value">&gt;50%<span class="metric-sub">Bay Area</span></div>
          <div class="metric-bar"><div class="metric-bar-fill" style="width: 100%"></div></div>
        </div>
      </article>

      <article class="impact-card">
        <div class="card-head">
          <h4>Imprecise government policy</h4>
          <span class="impact-tag impact-tag-terra">POLICY</span>
        </div>
        <p>
          HUD sets Fair Market Rents (FMRs) — which determine the value of a Section 8 voucher — using ACS data
          plus CPI adjustments, at the metro or county level. In tight markets, FMRs are typically below actual
          rents, leading property owners to stop accepting vouchers. In softening markets, FMRs set too high waste
          federal subsidy dollars. Either way, fewer people are housed.
        </p>
        <div class="metric">
          <div class="metric-label">ACS vs. market-rent gap</div>
          <div class="metric-value">10–200%</div>
          <div class="metric-bar"><div class="metric-bar-fill" style="width: 100%"></div></div>
        </div>
      </article>

      <article class="impact-card">
        <div class="card-head">
          <h4>One-sided information</h4>
          <span class="impact-tag impact-tag-red">POWER</span>
        </div>
        <p>
          Institutional property owners pay for CoStar, RealPage, and Yardi, which give them parcel-by-parcel
          intelligence in near-real time. Tenants, city housing departments, legal-aid clinics, and community
          lenders don't have anything comparable. The data gap is a power gap.
        </p>
        <div class="metric">
          <div class="metric-label">Cost to access data</div>
          <div class="metric-value">$10K+<span class="metric-sub">per user / yr</span></div>
          <div class="metric-bar"><div class="metric-bar-fill metric-bar-fill--gold" style="width: 100%"></div></div>
        </div>
      </article>

      <article class="impact-card">
        <div class="card-head">
          <h4>Reactive, not proactive</h4>
          <span class="impact-tag impact-tag-gold">TIMING</span>
        </div>
        <p>
          Without parcel-level signals, service providers and agencies can only respond after communities have
          already been impacted. By then, the moment when emergency rental assistance or new policies could
          benefit communities has already passed.
        </p>
        <div class="metric">
          <div class="metric-label">Intervention window</div>
          <div class="metric-phrase">After the fact.</div>
          <div class="metric-caption">
            Public agencies see displacement only after it's already happened.
          </div>
          <div class="metric-bar"><div class="metric-bar-fill metric-bar-fill--gold" style="width: 100%"></div></div>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="solution-section" id="solution">
  <div class="section-inner solution-v2">
    <div class="reveal sv2-intro">
      <span class="sv2-eyebrow">The solution</span>
      <h2 class="sv2-title"><em>What we're building with Open Rent</em></h2>
      <p class="sv2-lede">
        A single, open-source, parcel-level view of rental housing in California —
        <span class="sv2-lede-accent">refreshed continuously</span>, starting in the Bay Area.
      </p>
    </div>

    <div class="reveal sv2-layout" style="transition-delay: 0.1s;">
      <aside class="sv2-rail" aria-hidden="true">
        <span class="sv2-rail-name">What it is</span>
        <span class="sv2-rail-meta">Parcel-level · Continuous</span>
      </aside>

      <div class="sv2-content">
        <p class="sv2-body">
          Open Rent aggregates data — including rent registries, tax assessor and parcel data, HUD programs, state
          and local affordable housing, building permits, rent listings, and licensed market data — into one
          harmonized, queryable layer at the parcel level.
        </p>
        <p class="sv2-body">
          On top of that layer we build tools — maps, dashboards, and APIs — that let non-technical users answer
          many questions.
        </p>

        <div class="sv2-questions">
          <span class="sv2-questions-eyebrow">Example questions</span>
          <ul class="sv2-questions-list">
            <li>
              <span class="sv2-check" aria-hidden="true">✓</span>
              <span>Which parcels on this block are showing signals consistent with growing housing instability?</span>
            </li>
            <li>
              <span class="sv2-check" aria-hidden="true">✓</span>
              <span>Where are our NOAH units, parcel by parcel, most at risk of flipping in the next 12 months?</span>
            </li>
            <li>
              <span class="sv2-check" aria-hidden="true">✓</span>
              <span
                >What is the actual 30th-percentile rent for a 2-bedroom in this HUD assessment area today, and how
                does it vary block by block?</span>
            </li>
          </ul>
        </div>

        <p class="sv2-pillars-intro">Three pillars:</p>

        <ol class="sv2-pillars">
          <li>
            <div class="sv2-pillar-label">
              <span>#1 /</span>
              <span>Data</span>
            </div>
            <div>
              <strong>Parcel-level data, continuously refreshed.</strong>
              <p>
                We link multiple data sources at the parcel level. Users can drill from region → city →
                neighborhood → block → individual parcel, and see current conditions in addition to five-year
                averages, trends, and more.
              </p>
            </div>
          </li>
          <li>
            <div class="sv2-pillar-label">
              <span>#2 /</span>
              <span>Tools</span>
            </div>
            <div>
              <strong>Tools, not just dashboards.</strong>
              <p>
                Designed for program officers, city staff, case workers, and community organizations — and doesn't
                require data or technical skills to access.
              </p>
            </div>
          </li>
          <li>
            <div class="sv2-pillar-label">
              <span>#3 /</span>
              <span>Partners</span>
            </div>
            <div>
              <strong>Built <em>with</em> cities and local organizations.</strong>
              <p>Every feature is co-designed with a named partner. First partner: City of Mountain View.</p>
            </div>
          </li>
        </ol>
      </div>

      <aside class="sv2-visual" aria-label="California coverage map">
        <img
          src="/ca-coverage-mockup.svg"
          alt="Browser window mockup showing California rent registry coverage map"
          class="sv2-visual-img"
          loading="lazy"
        />
      </aside>
    </div>
  </div>
  <div class="section-inner section-inner--light da-v2">
    <div class="reveal da-layout">
      <aside class="da-rail" aria-hidden="true">
        <span class="da-rail-name">01</span>
        <span class="da-rail-rule"></span>
        <span class="da-rail-meta">Data</span>
      </aside>

      <div class="da-content">
        <span class="da-eyebrow">Data aggregation</span>
        <h3 class="da-title">How we get the data — and how we get it to the parcel level</h3>
        <p class="da-body">Open Rent combines three data layers and links them at the parcel:</p>

        <ol class="da-numbered">
          <li>
            <div>
              <strong>Public sources</strong>
              <p>
                e.g., assessor parcels, building permits, rent registries, HUD administrative data, state data,
                US Census, Zillow ZORI.
              </p>
            </div>
          </li>
          <li>
            <div>
              <strong>Scraped listing and licensed market data</strong>
              <p>e.g., Dwellsy, Rentcast, Craigslist.</p>
            </div>
          </li>
          <li>
            <div>
              <strong>Partner-city feeds</strong>
              <p>Specific to our pilot jurisdictions.</p>
            </div>
          </li>
        </ol>

        <p class="da-body da-body--space">
          Parcel-level linkage is the core technical work: it's what lets a city, a case worker, or a CRA analyst
          ask a question about a specific parcel rather than a tract average.
        </p>
        <p class="da-body">
          Where coverage gaps exist — most notably single-family rentals and small multifamily — we build
          estimation models published alongside the data. Every source is documented. Every estimate has a
          confidence level and a geographic resolution stated plainly.
        </p>
      </div>

      <aside class="da-visual" aria-label="Parcel-level data pipeline mockup">
        <div class="da-mockup">
          <div class="da-mockup-header">
            <h4>Parcel-level data pipeline</h4>
            <span class="da-mockup-meta">v0.4 · Bay Area</span>
          </div>
          <div class="da-pipeline-sources">
            <span class="da-pill">Assessor parcels</span>
            <span class="da-pill">Building permits</span>
            <span class="da-pill">City rent registries</span>
            <span class="da-pill">HUD admin data</span>
            <span class="da-pill">Rentcast · Dwellsy</span>
            <span class="da-pill">Partner-city feeds</span>
          </div>
          <div class="da-pipeline-arrow" aria-hidden="true">↓</div>
          <div class="da-pipeline-linker">
            <strong>Parcel-level linker</strong>
            <span class="da-pipeline-linker-sub">Normalize · dedupe · geocode · confidence-weight</span>
          </div>
          <div class="da-pipeline-arrow" aria-hidden="true">↓</div>
          <div class="da-pipeline-output">Open Rent · Parcel-level queryable layer</div>
        </div>
      </aside>
    </div>
  </div>
</section>

<section class="case-study-section it-section" id="features">
  <div class="section-inner it-v2">
    <div class="it-layout">
      <aside class="it-rail">
        <span class="it-rail-name">02</span>
        <span class="it-rail-rule"></span>
        <span class="it-rail-meta">Tools</span>
      </aside>
      <div class="it-content">
        <span class="it-eyebrow">Interactive tools</span>
        <h3 class="it-title">Built for people who make decisions</h3>
        <p>
          A program officer at a community foundation shouldn't need a data scientist to answer a question about a
          single parcel in her portfolio. A case worker at a legal-aid clinic shouldn't need to wait for an ACS
          release to know which blocks need outreach. A CRA analyst shouldn't need to argue with examiners using data
          that doesn't resolve below the county.
        </p>
        <p>
          Our tools turn parcel-level, continuously updated data into something you can put in a board memo, a case
          file, a grant application, or a city council packet — with the geographic resolution required for good
          decision-making.
        </p>
        <div class="it-ph it-ph--media">
          <video autoplay loop muted playsinline class="it-media">
            <source src="/Rent%20Tool%20Video.mov" type="video/quicktime" />
            <source src="/Rent%20Tool%20Video.mov" type="video/mp4" />
          </video>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="partners-section" id="impact">
  <div class="section-inner partners-v2">
    <div class="partners-layout">
      <aside class="partners-rail">
        <span class="partners-rail-name">03</span>
        <span class="partners-rail-rule"></span>
        <span class="partners-rail-meta">Partners</span>
      </aside>

      <div class="partners-content">
        <span class="partners-eyebrow">Local partnerships</span>
        <h3 class="partners-title">Building Open Rent with the City of Mountain&nbsp;View</h3>
        <p class="partners-body">
          Our first city partner is the City of Mountain View. Working directly with the Housing Department,
          we're co-designing Open Rent to support Mountain View's rental market data needs, including:
        </p>
        <ul class="partner-needs">
          <li>Integrating fragmented data sources into a single unified system.</li>
          <li>Expanding analytical capabilities for longitudinal and comparative market reporting.</li>
          <li>Quantifying rental program impacts for policy and public transparency.</li>
        </ul>
        <p class="partners-body">
          By June 2026, Mountain View staff will be able to use Open Rent for these operational and strategic needs.
        </p>

        <div class="or-widget">
          <div class="or-details light">
            <div class="or-details-col">
              <h4 class="or-label">Data</h4>
              <div class="or-pills">
                <span class="or-pill">Rent registry</span>
                <span class="or-pill">LIHTC, Section 8</span>
                <span class="or-pill">State and city programs</span>
                <span class="or-pill">Licensed market data</span>
                <span class="or-pill">Rentcast rent listing</span>
                <span class="or-pill">Dwellsy rent listing</span>
                <span class="or-pill">Zillow ZORI</span>
                <span class="or-pill">US Census ACS</span>
                <span class="or-pill">Open Street Maps</span>
                <span class="or-pill">Parcels</span>
                <span class="or-pill">Assessor records</span>
              </div>
            </div>

            <div class="or-details-col">
              <h4 class="or-label">Tools</h4>
              <div class="or-tools">
                <div class="or-tool">
                  <div class="or-tool-title">Base map holistic view</div>
                  <p class="or-tool-desc">Every parcel and every unit rendered on one continuous canvas.</p>
                </div>
                <div class="or-tool">
                  <div class="or-tool-title">Area rental stock overview</div>
                  <p class="or-tool-desc">Totals, medians, and affordability rolled up by zip, city, or neighborhood.</p>
                </div>
                <div class="or-tool">
                  <div class="or-tool-title">Rental segment comparison panel</div>
                  <p class="or-tool-desc">Compare rent bands across geographies and bedroom counts, side by side.</p>
                </div>
              </div>
            </div>

            <div class="or-details-col">
              <h4 class="or-label">Go-live</h4>
              <div class="or-date-wrap">
                <div class="or-date">
                  June <span class="or-date-year">2026</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <p class="partners-cta"><a href="#funding" class="btn-ghost">Read the Mountain View pilot brief →</a></p>
      </div>

      <aside class="partners-visual" aria-label="Open Rent product preview">
        <div class="or-widget">
          <div class="or-frame">
            <div class="or-chrome">
              <div class="or-lights"><span></span><span></span><span></span></div>
              <div class="or-url">open-rent-initiative.org<strong>/mountain-view/94041/251-chiquita</strong></div>
            </div>

            <div class="or-app">
              <header class="or-app-header">
                <div class="or-logo">Open Rent</div>
              </header>

              <div class="or-search">
                <input class="or-search-input" placeholder="Search a city, zipcode, or address" readonly />
                <button class="or-filters" type="button">Filters</button>
              </div>

              <div class="or-cities">
                <div class="or-city">Mountain View</div>
                <div class="or-city">Minneapolis</div>
                <div class="or-city">St. Paul</div>
                <div class="or-city">East Los Angeles</div>
                <div class="or-city">Koreatown, Los Angeles</div>
              </div>

              <div class="or-stats">
                <div><span class="or-stat-key">Zip:</span> 94041</div>
                <div><span class="or-stat-key">Buildings:</span> 2,681</div>
                <div><span class="or-stat-key">Total Units:</span> 1,984</div>
                <div><span class="or-stat-key">Median:</span> $2,532</div>
              </div>

              <div class="or-main">
                <div class="or-map">
                  <svg viewBox="0 0 700 430" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" aria-label="Parcel map of Mountain View, 94041">
                    <rect width="700" height="430" fill="#F5F1E3" />
                    <g transform="rotate(-22 350 215)">
                      <g fill="#DFD9C6">
                        <rect x="-300" y="84" width="1300" height="22" />
                        <rect x="-300" y="206" width="1300" height="28" />
                        <rect x="-300" y="332" width="1300" height="22" />
                        <rect x="138" y="-300" width="22" height="1000" />
                        <rect x="378" y="-300" width="26" height="1000" />
                        <rect x="580" y="-300" width="22" height="1000" />
                      </g>
                      <g fill="#EBCD7E" stroke="#4678B2" stroke-width="0.6">
                        <rect x="-170" y="108" width="32" height="46" /><rect x="-134" y="108" width="32" height="46" />
                        <rect x="-98" y="108" width="32" height="46" /><rect x="-62" y="108" width="32" height="46" />
                        <rect x="-26" y="108" width="32" height="46" /><rect x="10" y="108" width="32" height="46" />
                        <rect x="46" y="108" width="32" height="46" /><rect x="82" y="108" width="28" height="46" />
                        <rect x="112" y="108" width="24" height="46" />
                        <rect x="164" y="108" width="36" height="46" /><rect x="204" y="108" width="36" height="46" />
                        <rect x="244" y="108" width="36" height="46" /><rect x="284" y="108" width="36" height="46" />
                        <rect x="324" y="108" width="52" height="46" />
                        <rect x="406" y="108" width="30" height="46" /><rect x="440" y="108" width="30" height="46" />
                        <rect x="474" y="108" width="30" height="46" /><rect x="508" y="108" width="30" height="46" />
                        <rect x="542" y="108" width="36" height="46" />
                        <rect x="604" y="108" width="32" height="46" /><rect x="640" y="108" width="32" height="46" />
                        <rect x="676" y="108" width="32" height="46" /><rect x="712" y="108" width="32" height="46" />
                        <rect x="748" y="108" width="32" height="46" /><rect x="784" y="108" width="32" height="46" />
                        <rect x="820" y="108" width="32" height="46" />
                        <rect x="-170" y="158" width="32" height="46" /><rect x="-134" y="158" width="32" height="46" />
                        <rect x="-98" y="158" width="32" height="46" /><rect x="-62" y="158" width="32" height="46" />
                        <rect x="-26" y="158" width="32" height="46" /><rect x="10" y="158" width="32" height="46" />
                        <rect x="46" y="158" width="32" height="46" /><rect x="82" y="158" width="28" height="46" />
                        <rect x="112" y="158" width="24" height="46" />
                        <rect x="164" y="158" width="36" height="46" /><rect x="204" y="158" width="36" height="46" />
                        <rect x="244" y="158" width="36" height="46" /><rect x="284" y="158" width="36" height="46" />
                        <rect x="324" y="158" width="52" height="46" />
                        <rect x="406" y="158" width="30" height="46" /><rect x="440" y="158" width="30" height="46" />
                        <rect x="474" y="158" width="30" height="46" /><rect x="508" y="158" width="30" height="46" />
                        <rect x="542" y="158" width="36" height="46" />
                        <rect x="604" y="158" width="32" height="46" /><rect x="640" y="158" width="32" height="46" />
                        <rect x="676" y="158" width="32" height="46" /><rect x="712" y="158" width="32" height="46" />
                        <rect x="748" y="158" width="32" height="46" /><rect x="784" y="158" width="32" height="46" />
                        <rect x="820" y="158" width="32" height="46" />
                        <rect x="-170" y="236" width="32" height="46" /><rect x="-134" y="236" width="32" height="46" />
                        <rect x="-98" y="236" width="32" height="46" /><rect x="-62" y="236" width="32" height="46" />
                        <rect x="-26" y="236" width="32" height="46" /><rect x="10" y="236" width="32" height="46" />
                        <rect x="46" y="236" width="32" height="46" /><rect x="82" y="236" width="28" height="46" />
                        <rect x="112" y="236" width="24" height="46" />
                        <rect x="164" y="236" width="36" height="46" /><rect x="204" y="236" width="36" height="46" />
                        <rect x="244" y="236" width="36" height="46" />
                        <rect x="324" y="236" width="52" height="46" />
                        <rect x="406" y="236" width="30" height="46" /><rect x="440" y="236" width="30" height="46" />
                        <rect x="474" y="236" width="30" height="46" /><rect x="508" y="236" width="30" height="46" />
                        <rect x="542" y="236" width="36" height="46" />
                        <rect x="604" y="236" width="32" height="46" /><rect x="640" y="236" width="32" height="46" />
                        <rect x="676" y="236" width="32" height="46" /><rect x="712" y="236" width="32" height="46" />
                        <rect x="748" y="236" width="32" height="46" /><rect x="784" y="236" width="32" height="46" />
                        <rect x="-170" y="286" width="32" height="44" /><rect x="-134" y="286" width="32" height="44" />
                        <rect x="-98" y="286" width="32" height="44" /><rect x="-62" y="286" width="32" height="44" />
                        <rect x="-26" y="286" width="32" height="44" /><rect x="10" y="286" width="32" height="44" />
                        <rect x="46" y="286" width="32" height="44" /><rect x="82" y="286" width="28" height="44" />
                        <rect x="112" y="286" width="24" height="44" />
                        <rect x="164" y="286" width="36" height="44" /><rect x="204" y="286" width="36" height="44" />
                        <rect x="244" y="286" width="36" height="44" /><rect x="284" y="286" width="36" height="44" />
                        <rect x="324" y="286" width="52" height="44" />
                        <rect x="406" y="286" width="30" height="44" /><rect x="440" y="286" width="30" height="44" />
                        <rect x="474" y="286" width="30" height="44" /><rect x="508" y="286" width="30" height="44" />
                        <rect x="542" y="286" width="36" height="44" />
                        <rect x="604" y="286" width="32" height="44" /><rect x="640" y="286" width="32" height="44" />
                        <rect x="676" y="286" width="32" height="44" /><rect x="712" y="286" width="32" height="44" />
                        <rect x="748" y="286" width="32" height="44" /><rect x="784" y="286" width="32" height="44" />
                        <rect x="-170" y="356" width="32" height="44" /><rect x="-134" y="356" width="32" height="44" />
                        <rect x="-98" y="356" width="32" height="44" /><rect x="-62" y="356" width="32" height="44" />
                        <rect x="-26" y="356" width="32" height="44" /><rect x="10" y="356" width="32" height="44" />
                        <rect x="46" y="356" width="32" height="44" /><rect x="82" y="356" width="28" height="44" />
                        <rect x="112" y="356" width="24" height="44" />
                        <rect x="164" y="356" width="36" height="44" /><rect x="204" y="356" width="36" height="44" />
                        <rect x="244" y="356" width="36" height="44" /><rect x="284" y="356" width="36" height="44" />
                        <rect x="324" y="356" width="52" height="44" />
                        <rect x="406" y="356" width="30" height="44" /><rect x="440" y="356" width="30" height="44" />
                        <rect x="474" y="356" width="30" height="44" /><rect x="508" y="356" width="30" height="44" />
                        <rect x="542" y="356" width="36" height="44" />
                        <rect x="604" y="356" width="32" height="44" /><rect x="640" y="356" width="32" height="44" />
                        <rect x="676" y="356" width="32" height="44" /><rect x="712" y="356" width="32" height="44" />
                        <rect x="748" y="356" width="32" height="44" /><rect x="784" y="356" width="32" height="44" />
                        <rect x="-170" y="30" width="32" height="54" /><rect x="-134" y="30" width="32" height="54" />
                        <rect x="-98" y="30" width="32" height="54" /><rect x="-62" y="30" width="32" height="54" />
                        <rect x="-26" y="30" width="32" height="54" /><rect x="10" y="30" width="32" height="54" />
                        <rect x="46" y="30" width="32" height="54" /><rect x="82" y="30" width="28" height="54" />
                        <rect x="112" y="30" width="24" height="54" />
                        <rect x="164" y="30" width="36" height="54" /><rect x="204" y="30" width="36" height="54" />
                        <rect x="244" y="30" width="36" height="54" /><rect x="284" y="30" width="36" height="54" />
                        <rect x="324" y="30" width="52" height="54" />
                        <rect x="406" y="30" width="30" height="54" /><rect x="440" y="30" width="30" height="54" />
                        <rect x="474" y="30" width="30" height="54" /><rect x="508" y="30" width="30" height="54" />
                        <rect x="542" y="30" width="36" height="54" />
                        <rect x="604" y="30" width="32" height="54" /><rect x="640" y="30" width="32" height="54" />
                        <rect x="676" y="30" width="32" height="54" /><rect x="712" y="30" width="32" height="54" />
                      </g>
                      <rect x="284" y="236" width="36" height="46" fill="#D85A4A" stroke="#8A3025" stroke-width="0.8" opacity="0.9" />
                      <g fill="#8C8573" font-size="7" font-family="Arial, Helvetica, sans-serif">
                        <text x="-90" y="130" transform="rotate(22 -90 130)">263</text>
                        <text x="20" y="130" transform="rotate(22 20 130)">218</text>
                        <text x="170" y="180" transform="rotate(22 170 180)">271</text>
                        <text x="340" y="180" transform="rotate(22 340 180)">260</text>
                        <text x="440" y="130" transform="rotate(22 440 130)">1705</text>
                        <text x="620" y="130" transform="rotate(22 620 130)">1720</text>
                        <text x="250" y="260" transform="rotate(22 250 260)">245</text>
                        <text x="340" y="260" transform="rotate(22 340 260)">250</text>
                        <text x="440" y="260" transform="rotate(22 440 260)">1640</text>
                        <text x="620" y="260" transform="rotate(22 620 260)">1585</text>
                        <text x="170" y="310" transform="rotate(22 170 310)">309</text>
                        <text x="340" y="310" transform="rotate(22 340 310)">275</text>
                        <text x="-90" y="310" transform="rotate(22 -90 310)">291</text>
                      </g>
                      <g fill="#6E6A5C" font-size="10" font-family="Georgia, 'Times New Roman', serif" font-style="italic">
                        <text x="295" y="100" transform="rotate(90 295 100)">Chiquita Ave</text>
                        <text x="-40" y="198">Escuela Ave</text>
                        <text x="390" y="328">Villa St</text>
                      </g>
                    </g>
                  </svg>
                  <div class="or-map-attr">mapbox</div>
                </div>

                <div class="or-panel">
                  <h2 class="or-property-name">251 CHIQUITA AVE</h2>
                  <div class="or-property-addr">MOUNTAIN VIEW, 94041</div>
                  <a href="#funding" class="or-more">+1 more address</a>
                  <div class="or-meta">2 units</div>
                  <div class="or-meta">0.0% affordable</div>
                  <div class="or-meta bold">Property Type: Not Available</div>

                  <div class="or-tabs" role="tablist">
                    <div class="or-tab active" role="tab">Building</div>
                    <div class="or-tab" role="tab">Zipcode</div>
                    <div class="or-tab" role="tab">City</div>
                  </div>

                  <div class="or-section-heading">Average Rent By Bedroom</div>
                  <div class="or-rent-row">
                    <div class="br">2 BR</div>
                    <div class="or-bar"><div class="or-bar-fill" style="width: 80%"></div></div>
                    <div class="or-rent-val">$3,968</div>
                  </div>
                  <div class="or-rent-row">
                    <div class="br">3 BR</div>
                    <div class="or-bar"><div class="or-bar-fill" style="width: 96%"></div></div>
                    <div class="or-rent-val">$4,620</div>
                  </div>

                  <div class="or-section-heading" style="margin-top: 12px;">Unit Level Data (summarized)</div>
                  <table class="or-table">
                    <thead>
                      <tr>
                        <th>BR</th>
                        <th>Total</th>
                        <th>Available</th>
                        <th>Avg Rent</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>2 BR</td><td>1</td><td>1</td><td>$3,968</td></tr>
                      <tr><td>3 BR</td><td>1</td><td>1</td><td>$4,620</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div class="or-breadcrumb">
                California <em>›</em> Santa Clara <em>›</em> Mountain View <em>›</em> <strong>94041</strong>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</section>

<section class="uc-section" id="usecases">
  <div class="section-inner uc-v2">
    <span class="uc-eyebrow">Use cases</span>
    <h2 class="uc-title">Where Open Rent could add value <em>for stakeholders</em></h2>

    <div class="uc-grid">
      <article class="uc-card">
        <div class="uc-header">
          <span class="uc-number">Use case 01</span>
          <span class="uc-category">Frontline services</span>
        </div>
        <h4 class="uc-card-title">Direct service providers</h4>
        <p class="uc-problem">
          Case workers at tenant-counseling clinics, legal-aid offices, and homelessness-prevention programs
          triage limited resources without knowing which parcels and blocks are facing housing stability risks.
        </p>
        <div class="uc-response">
          <div class="uc-response-header">
            <span class="uc-check" aria-hidden="true">✓</span>
            With Open Rent
          </div>
          <p>
            Parcel-level signals from rent spikes, ownership changes, and eviction-filing patterns — so frontline
            teams can deploy outreach, emergency rental assistance, and right-to-counsel services to the specific
            parcels where tenants are at risk.
          </p>
        </div>
      </article>

      <article class="uc-card">
        <div class="uc-header">
          <span class="uc-number">Use case 02</span>
          <span class="uc-category">Local government</span>
        </div>
        <h4 class="uc-card-title">City housing staff and local government</h4>
        <p class="uc-problem">
          Lack visibility into the entire rental stock, making it difficult to develop the right policies,
          enforce existing policies, and provide transparency.
        </p>
        <div class="uc-response">
          <div class="uc-response-header">
            <span class="uc-check" aria-hidden="true">✓</span>
            With Open Rent
          </div>
          <p>
            A live parcel-level view of rental stock and rental data — so cities can move from reactive policies
            and enforcement to proactive, parcel-level compliance monitoring, and target housing stability policies.
          </p>
        </div>
      </article>

      <article class="uc-card">
        <div class="uc-header">
          <span class="uc-number">Use case 03</span>
          <span class="uc-category">Community finance</span>
        </div>
        <h4 class="uc-card-title">CRA teams at community banks and community lenders</h4>
        <p class="uc-problem">
          CRA investment decisions rely on HUD assessment-area data that's both too coarse to locate specific LMI
          investment opportunities and too stale to reflect current market conditions. By the time a CRA team has
          current FMRs, the tight-market window has closed and LMI households have already been priced out.
        </p>
        <div class="uc-response">
          <div class="uc-response-header">
            <span class="uc-check" aria-hidden="true">✓</span>
            With Open Rent
          </div>
          <p>
            Real-time LMI rental stock and rent data at the parcel level within each assessment area — so CRA
            teams can target capital to specific parcels and neighborhoods where it qualifies and document impact
            their examiners and boards can defend.
          </p>
        </div>
      </article>

      <article class="uc-card">
        <div class="uc-header">
          <span class="uc-number">Use case 04</span>
          <span class="uc-category">Preservation</span>
        </div>
        <h4 class="uc-card-title">Affordable housing preservation funders and developers</h4>
        <p class="uc-problem">
          NOAH is invisible in tract-level data; preservation funds can't prioritize individual parcels they
          can't see, and the tenants in unsubsidized affordable units are often the most at risk of displacement.
        </p>
        <div class="uc-response">
          <div class="uc-response-header">
            <span class="uc-check" aria-hidden="true">✓</span>
            With Open Rent
          </div>
          <p>
            A parcel-level inventory of NOAH and at-risk affordable stock, parcel by parcel, with risk signals
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
    <span class="funding-eyebrow">Funding</span>
    <h2 class="funding-title">Funding the <em>next phase</em></h2>
    <p class="funding-lead">
      We are excited to welcome new funders in support of expanding Open Rent across the Bay Area and to launch
      a Los Angeles pilot. Please reach out if you are interested in expanding Open Rent to a particular
      jurisdiction (e.g., Oakland, Los Angeles) or tackling a specific issue (e.g., estimating housing stability
      risk, providing tools to support CRA teams).
    </p>
    <p class="funding-lead">We'd love your support and to hear from you!</p>
    <div class="funding-actions">
      <a class="funding-btn" href="mailto:?subject=Open%20Rent%20—%20Funding%20conversation">Book a briefing →</a>
      <a class="funding-btn-ghost" href="/funder-brief.pdf">Download the 2-page funder brief (PDF) →</a>
    </div>
  </div>
</section>

<footer>
  <div class="footer-bottom">
    The Open Rent Initiative &middot; A 501(c)(3) fiscally-sponsored project of the Policy Simulation Library Foundation
    &middot; 2026
  </div>
</footer>
