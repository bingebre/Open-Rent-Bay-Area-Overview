#!/usr/bin/env python3
"""Emit src/routes/+page.svelte from legacy/index.cleaned.html (body only)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "legacy" / "index.cleaned.html").read_text(encoding="utf-8")
m = re.search(r"<body>\s*(.*)\s*</body>", html, re.DOTALL | re.IGNORECASE)
if not m:
    raise SystemExit("Could not find <body> in legacy/index.cleaned.html")
frag = m.group(1)

# Fix solution section: drop premature </section> before the Data Aggregation block
lines = frag.splitlines(keepends=True)
out_lines = []
i = 0
while i < len(lines):
    if (
        lines[i].strip() == "</section>"
        and i + 1 < len(lines)
        and "section-inner" in lines[i + 1]
        and "F9F5F0" in lines[i + 1]
    ):
        i += 1
        continue
    out_lines.append(lines[i])
    i += 1
frag = "".join(out_lines)

replacements = [
    ('src="Bay%20Area%20Map.html"', 'src="/map" title="Bay Area rent data map"'),
    ('<section class="case-study-section">', '<section class="case-study-section" id="features">'),
    ('src="Rent%20Tool%20Video.mov"', 'src="/Rent%20Tool%20Video.mov"'),
    ('src="Mountain-view.png"', 'src="/Mountain-view.png"'),
    ('src="logos/', 'src="/logos/'),
]
for a, b in replacements:
    frag = frag.replace(a, b)

script = r"""
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
				svg.innerHTML = '';
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
					svg.appendChild(line);
				});
			}
			window.addEventListener('load', () => setTimeout(drawLines, 500));
			window.addEventListener('resize', drawLines);
		}

		const parallaxDiv = document.querySelector('.parallax-divider');
		const contextMap = document.getElementById('contextMap');
		const contextParas = document.querySelectorAll('.context-para');

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
		};
		window.addEventListener('scroll', onScrollFx, { passive: true });

		return () => {
			window.removeEventListener('scroll', onScrollNav);
			window.removeEventListener('scroll', onScrollFx);
		};
	});
</script>

<svelte:head>
	<title>The Open Rent Initiative — Citizen Codex</title>
</svelte:head>
"""

out = ROOT / "src" / "routes" / "+page.svelte"
out.write_text(script + "\n" + frag + "\n", encoding="utf-8")
print(f"Wrote {out}")
