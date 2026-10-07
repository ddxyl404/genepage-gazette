import Link from "next/link";
import { Suspense } from "react";
import { Colophon } from "@/components/Colophon";
import { LangSwitch } from "@/components/LangSwitch";
import { fetchIndex, fetchSearch } from "@/lib/api";
import type { SearchResult } from "@/lib/types";
import {
  pickDeck,
  resolveLocale,
  t,
  withLang,
  type Locale,
} from "@/lib/i18n";

export const dynamic = "force-dynamic";

function deckSnippet(text?: string, fallback = ""): string {
  if (!text) return fallback;
  const cut = text.slice(0, 42);
  return cut.length < text.length ? `${cut}…` : cut;
}

export default async function HomePage({
  searchParams,
}: {
  searchParams?: { q?: string; lang?: string };
}) {
  const lang: Locale = resolveLocale(searchParams);
  const q = (searchParams?.q || "").trim();
  let edition = "0.3.0-p35";
  let dataAsOf = "2026-09-29";
  let count = 0;
  let list: SearchResult[] = [];

  try {
    const index = await fetchIndex();
    edition = index.edition || edition;
    dataAsOf = index.data_as_of || dataAsOf;
    count = index.count ?? (index.genes?.length || 0);
    list = await fetchSearch(q);
    if (!q && count === 0) count = list.length;
  } catch {
    list = [];
  }

  return (
    <main className="page page--index page--p35" data-locale={lang}>
      <header className="masthead masthead--p35 index-hero">
        <div className="masthead__brand">
          <h1 className="masthead__title">
            GenePage Gazette
            <span className="masthead__title-zh">{t(lang, "title_zh_suffix")}</span>
          </h1>
          <div className="masthead__brand-right">
            <p className="masthead__meta">
              edition {edition}
              <span className="sep">·</span>
              {t(lang, "genes_count", { n: count })}
              <span className="sep">·</span>
              {t(lang, "data_as_of")} {dataAsOf}
              <span className="sep">·</span>
              <a className="catalog__csv" href="/api/export/genes.csv" download>
                {t(lang, "download_csv")}
              </a>
            </p>
            <Suspense
              fallback={
                <div className="lang-switch no-print" aria-hidden="true">
                  zh | en
                </div>
              }
            >
              <LangSwitch locale={lang} />
            </Suspense>
          </div>
        </div>
        <hr className="rule-double rule-double--heavy" />
        <p className="index-lead">{t(lang, "index_lead")}</p>
        <div className="index-search">
          <form className="search" action="/" method="get" role="search">
            <input type="hidden" name="lang" value={lang} />
            <input
              className="search__input"
              type="search"
              name="q"
              placeholder={t(lang, "search_placeholder_home")}
              defaultValue={q}
            />
            <button className="search__btn" type="submit">
              {t(lang, "search_btn")}
            </button>
          </form>
        </div>
      </header>

      <section className="catalog" aria-labelledby="catalog-label">
        <h2 className="section-label section-label--zh" id="catalog-label">
          {t(lang, "catalog_today")}
          {q
            ? t(lang, "catalog_query", { q })
            : t(lang, "catalog_n", { n: list.length })}
        </h2>
        <ul className="catalog__list">
          {list.map((g) => (
            <li key={g.symbol}>
              <Link
                href={withLang(`/g/${encodeURIComponent(g.symbol)}`, lang)}
              >
                <span className="cat-symbol">{g.symbol}</span>
                <span className="cat-desc">
                  {deckSnippet(
                    pickDeck(g, lang),
                    t(lang, "gene_demo")
                  )}
                </span>
                <span className="cat-loc">{g.location || g.id || ""}</span>
              </Link>
            </li>
          ))}
          {list.length === 0 && (
            <li>
              <span className="entry-plain">
                <span className="cat-symbol">—</span>
                <span className="cat-desc">{t(lang, "no_match")}</span>
                <span className="cat-badge">{t(lang, "not_in_edition")}</span>
              </span>
            </li>
          )}
        </ul>
        <p className="catalog__tools">
          <a className="catalog__csv" href="/api/export/genes.csv" download>
            {t(lang, "download_csv")}
          </a>
          <span className="catalog__count">
            {t(lang, "genes_count", { n: count || list.length })} · edition{" "}
            {edition}
          </span>
        </p>
      </section>

      <Colophon edition={edition} dataAsOf={dataAsOf} locale={lang} />
      <p className="footer-mini">GenePage Gazette · Style C · P3.6</p>
    </main>
  );
}
