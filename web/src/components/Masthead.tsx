import Link from "next/link";
import { Suspense } from "react";
import type { Gene } from "@/lib/types";
import { type Locale, t, withLang } from "@/lib/i18n";
import { LangSwitch } from "@/components/LangSwitch";

type Props = {
  gene?: Gene;
  dataAsOf?: string;
  edition?: string;
  showSearch?: boolean;
  printHref?: string;
  locale?: Locale;
  lang?: Locale;
  /** P3.9 ink masthead: black bar + tools strip; gene symbol lives in IssueHero */
  ink?: boolean;
};

export function Masthead({
  gene,
  dataAsOf = "2026-09-29",
  edition = "0.3.0-p35",
  showSearch = true,
  printHref,
  locale,
  lang,
  ink = false,
}: Props) {
  const L: Locale = locale || lang || "zh";
  const locationStat = gene?.headline_stats?.find((s) => s.key === "location");
  const locLabel =
    (typeof locationStat?.value === "string" && locationStat.value) ||
    (gene
      ? `${gene.location.chrom}:${gene.location.start}–${gene.location.end}`
      : "");
  const printLink = printHref ? withLang(printHref, L) : undefined;

  if (ink) {
    const sources = (gene?.sources || []).slice(0, 3);
    return (
      <header className="masthead masthead--p39 masthead--ink">
        <div className="masthead__inkbar">
          <h1 className="masthead__ink-title">
            <Link
              href={withLang("/", L)}
              style={{ color: "inherit", textDecoration: "none" }}
            >
              GenePage Gazette
              <span className="masthead__ink-zh">{t(L, "title_zh_suffix")}</span>
            </Link>
          </h1>
          <p className="masthead__ink-folio">
            <span>VOL</span>
            <span className="masthead__ink-dot">·</span>
            <span className="mono">{edition}</span>
            <span className="masthead__ink-dot">·</span>
            <span>{t(L, "data_as_of").toUpperCase()}</span>
            <span className="masthead__ink-dot">·</span>
            <span className="mono">{dataAsOf}</span>
          </p>
        </div>
        <div className="masthead__tools no-print">
          {showSearch && (
            <form
              className="search search--ink"
              action="/"
              method="get"
              role="search"
              aria-label={t(L, "search_aria")}
            >
              <input type="hidden" name="lang" value={L} />
              <input
                className="search__input"
                type="search"
                name="q"
                placeholder={t(L, "search_placeholder")}
                defaultValue=""
              />
              <button className="search__btn" type="submit">
                {t(L, "search_btn")}
              </button>
            </form>
          )}
          <div className="masthead__tools-links">
            {printLink && (
              <Link className="masthead__tool-link" href={printLink}>
                {t(L, "print_page")}
              </Link>
            )}
            {sources.map((s) => (
              <a
                key={s.url + s.name}
                className="masthead__tool-link"
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {s.name} ↗
              </a>
            ))}
          </div>
          <Suspense
            fallback={
              <div className="lang-switch" aria-hidden="true">
                zh | en
              </div>
            }
          >
            <LangSwitch locale={L} />
          </Suspense>
        </div>
      </header>
    );
  }

  return (
    <header className="masthead masthead--p35">
      <div className="masthead__top">
        <div className="masthead__brand">
          <h1 className="masthead__title">
            <Link
              href={withLang("/", L)}
              style={{ color: "inherit", textDecoration: "none" }}
            >
              GenePage Gazette
              <span className="masthead__title-zh">
                {t(L, "title_zh_suffix")}
              </span>
            </Link>
          </h1>
          <p className="masthead__meta masthead__meta--folio">
            <span className="masthead__folio">
              <span className="masthead__folio-k">
                {t(L, "edition_label")}
              </span>{" "}
              <span className="masthead__folio-v mono">{edition}</span>
            </span>
            <span className="sep">·</span>
            <span className="masthead__folio">
              <span className="masthead__folio-k">{t(L, "data_as_of")}</span>{" "}
              <span className="masthead__folio-v mono">{dataAsOf}</span>
            </span>
            {printLink && (
              <>
                <span className="sep">·</span>
                <Link className="no-print masthead__print" href={printLink}>
                  {t(L, "print_page")}
                </Link>
              </>
            )}
          </p>
        </div>
        <Suspense
          fallback={
            <div className="lang-switch no-print" aria-hidden="true">
              zh | en
            </div>
          }
        >
          <LangSwitch locale={L} />
        </Suspense>
      </div>
      <hr className="rule-double rule-double--heavy" />
      {gene && (
        <div className="masthead__gene-row">
          <div>
            <p className="masthead__gene" aria-label={gene.symbol}>
              {gene.symbol}
            </p>
            <p className="masthead__sub">
              {t(L, "aliases_prefix")}
              <span className="alias">
                {(gene.aliases || []).slice(0, 6).join(", ") || "—"}
              </span>
              <span className="dot">·</span>
              <span className="mono masthead__type">{locLabel}</span>
              <span className="dot">·</span>
              <span className="masthead__type">{gene.type}</span>
            </p>
          </div>
          {showSearch && (
            <form
              className="search no-print"
              action="/"
              method="get"
              role="search"
              aria-label={t(L, "search_aria")}
            >
              <input type="hidden" name="lang" value={L} />
              <input
                className="search__input"
                type="search"
                name="q"
                placeholder={t(L, "search_placeholder")}
                defaultValue=""
              />
              <button className="search__btn" type="submit">
                {t(L, "search_btn")}
              </button>
            </form>
          )}
        </div>
      )}
    </header>
  );
}
