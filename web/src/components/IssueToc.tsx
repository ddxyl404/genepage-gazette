"use client";

import type { MouseEvent } from "react";
import { t, type Locale } from "@/lib/i18n";

const SECTIONS = [
  { id: "lede", key: "toc_lede", fig: "toc_fig_lede" },
  { id: "cyto", key: "toc_cyto", fig: "toc_fig_cyto" },
  { id: "expression", key: "toc_expression", fig: "toc_fig_expr" },
  { id: "domains", key: "toc_domains", fig: "toc_fig_domain" },
  { id: "structure", key: "toc_structure", fig: "toc_fig_struct" },
  { id: "variants", key: "toc_variants", fig: "toc_fig_var" },
] as const;

type Props = {
  lang: Locale;
  /** Static list (print); no JS scroll */
  static?: boolean;
  pieceCount?: number;
};

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

function goTo(id: string, e: MouseEvent<HTMLAnchorElement>) {
  e.preventDefault();
  const el = document.getElementById(id);
  if (!el) {
    window.location.hash = id;
    return;
  }
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  el.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
  if (typeof history !== "undefined" && history.replaceState) {
    history.replaceState(null, "", `#${id}`);
  }
}

export function IssueToc({
  lang,
  static: isStatic = false,
  pieceCount = 6,
}: Props) {
  return (
    <nav
      className={isStatic ? "issue-toc issue-toc--static" : "issue-toc"}
      aria-label={t(lang, "issue_toc_label")}
    >
      <div className="issue-toc__head">
        <p className="issue-toc__title">{t(lang, "issue_toc_label")}</p>
        <p className="issue-toc__count mono">
          {pad(pieceCount)} / {t(lang, "issue_toc_pieces")}
        </p>
      </div>
      <hr className="issue-toc__rule" />
      <ol className="issue-toc__list">
        {SECTIONS.map((s, i) => (
          <li key={s.id} className="issue-toc__item">
            <a
              href={`#${s.id}`}
              className="issue-toc__link"
              onClick={isStatic ? undefined : (e) => goTo(s.id, e)}
            >
              <span className="issue-toc__num">{pad(i + 1)}</span>
              <span className="issue-toc__name">{t(lang, s.key)}</span>
              <span className="issue-toc__leader" aria-hidden="true" />
              <span className="issue-toc__fig mono">{t(lang, s.fig)}</span>
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
