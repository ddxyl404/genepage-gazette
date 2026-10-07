"use client";

import { useEffect } from "react";

/** Observes .reveal nodes under .page--p39 / .page--p38 and toggles .reveal--in. */
export function RevealInit() {
  useEffect(() => {
    const root =
      document.querySelector(".page--p39") ||
      document.querySelector(".page--p38");
    if (!root) return;
    const nodes = Array.from(root.querySelectorAll<HTMLElement>(".reveal"));
    if (!nodes.length) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || root.classList.contains("page--print")) {
      for (const el of nodes) el.classList.add("reveal--in");
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add("reveal--in");
            io.unobserve(e.target);
          }
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 },
    );
    for (const el of nodes) io.observe(el);
    return () => io.disconnect();
  }, []);

  return null;
}
