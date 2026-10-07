"use client";

import { useEffect, useRef, useState } from "react";
import type { TissueExpr } from "@/lib/types";
import { pickTissueName, t, type Locale } from "@/lib/i18n";

type Props = {
  ranked: TissueExpr[];
  maxVal: number;
  locale: Locale;
};

export function ExprBarsChart({ ranked, maxVal, locale }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [on, setOn] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const printPage = !!el.closest(".page--print");
    if (reduced || printPage) {
      setOn(true);
      return;
    }
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setOn(true);
          io.disconnect();
        }
      },
      { threshold: 0.2 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={on ? "expr-bars__chart expr-bars__chart--on" : "expr-bars__chart"}
      role="img"
      aria-label={t(locale, "expr_bars_aria")}
      data-animate={on ? "on" : "off"}
    >
      {ranked.map((ti, i) => {
        const pct = Math.max(1.5, Math.round((ti.value / maxVal) * 1000) / 10);
        return (
          <div
            className={
              i === 0 ? "expr-bars__row expr-bars__row--top" : "expr-bars__row"
            }
            key={`${ti.name}-${i}`}
          >
            <span className="expr-bars__name">{pickTissueName(ti, locale)}</span>
            <div className="expr-bars__track">
              <div
                className="expr-bars__bar"
                style={{ ["--bar-pct" as string]: `${pct}%`, width: on ? `${pct}%` : "0%" }}
              />
            </div>
            <span className="expr-bars__val mono">
              {Number(ti.value).toFixed(1)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
