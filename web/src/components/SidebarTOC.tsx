"use client";

import { useEffect, useState } from "react";
import { t, type Locale } from "@/lib/i18n";

const SECTION_IDS = [
  "lede",
  "cyto",
  "expression",
  "domains",
  "structure",
  "variants",
] as const;

type SectionId = (typeof SECTION_IDS)[number];

const TOC_KEYS: Record<SectionId, string> = {
  lede: "toc_lede",
  cyto: "toc_cyto",
  expression: "toc_expression",
  domains: "toc_domains",
  structure: "toc_structure",
  variants: "toc_variants",
};

type Props = { lang: Locale; compact?: boolean };

export function SidebarTOC({ lang, compact = false }: Props) {
  const [current, setCurrent] = useState<SectionId>("lede");

  useEffect(() => {
    const nodes = SECTION_IDS.map((id) => document.getElementById(id)).filter(
      (el): el is HTMLElement => !!el,
    );
    if (!nodes.length) return;

    const ratios = new Map<string, number>();
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          ratios.set(e.target.id, e.isIntersecting ? e.intersectionRatio : 0);
        }
        let best: SectionId = "lede";
        let bestRatio = -1;
        for (const id of SECTION_IDS) {
          const r = ratios.get(id) ?? 0;
          if (r > bestRatio) {
            bestRatio = r;
            best = id;
          }
        }
        // Prefer the last section whose top is above mid-viewport when ratios tie.
        if (bestRatio <= 0) {
          const mid = window.innerHeight * 0.35;
          let fallback: SectionId = "lede";
          for (const el of nodes) {
            const top = el.getBoundingClientRect().top;
            if (top <= mid) fallback = el.id as SectionId;
          }
          setCurrent(fallback);
        } else {
          setCurrent(best);
        }
      },
      { rootMargin: "-12% 0px -55% 0px", threshold: [0, 0.1, 0.25, 0.5, 0.75, 1] },
    );

    for (const el of nodes) io.observe(el);
    return () => io.disconnect();
  }, []);

  const list = (
    <nav className={compact ? "toc toc--compact" : "toc"} aria-label={t(lang, "toc_label")}>
      <ul className="toc__list">
        {SECTION_IDS.map((id) => (
          <li key={id}>
            <a
              href={`#${id}`}
              className={
                current === id ? "toc__item toc__item--current" : "toc__item"
              }
              aria-current={current === id ? "location" : undefined}
            >
              {t(lang, TOC_KEYS[id])}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );

  if (!compact) return list;

  return (
    <details className="toc-fold">
      <summary className="toc-fold__summary">{t(lang, "toc_label")}</summary>
      {list}
    </details>
  );
}
