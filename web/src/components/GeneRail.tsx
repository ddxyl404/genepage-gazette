import Link from "next/link";
import type { Gene } from "@/lib/types";
import { t, withLang, type Locale } from "@/lib/i18n";
import { HeadlineStats } from "@/components/HeadlineStats";
import { SidebarTOC } from "@/components/SidebarTOC";

type Props = {
  gene: Gene;
  lang: Locale;
  printHref: string;
  /** Print / narrow: static, not sticky */
  sticky?: boolean;
  /** Narrow screens: fold TOC behind details */
  foldToc?: boolean;
};

export function GeneRail({
  gene,
  lang,
  printHref,
  sticky = true,
  foldToc = false,
}: Props) {
  const sources = (gene.sources || []).slice(0, 4);

  return (
    <aside
      className={sticky ? "rail rail--sticky" : "rail"}
      aria-label={t(lang, "rail_aria")}
    >
      <div className="rail__block">
        <p className="rail__label">{t(lang, "headline_aria")}</p>
        <hr className="rule-double rail__rule" />
        <HeadlineStats gene={gene} lang={lang} variant="rail" />
      </div>

      <div className="rail__block">
        {!foldToc && <p className="rail__label">{t(lang, "toc_label")}</p>}
        {!foldToc && <hr className="rule-double rail__rule" />}
        <SidebarTOC lang={lang} compact={foldToc} />
      </div>

      <div className="rail__block rail__tools">
        <p className="rail__label">{t(lang, "rail_links")}</p>
        <hr className="rule-double rail__rule" />
        <ul className="rail__link-list">
          <li>
            <Link href={withLang(printHref, lang)}>{t(lang, "print_page")}</Link>
          </li>
          {sources.map((s) => (
            <li key={s.url + s.name}>
              <a href={s.url} target="_blank" rel="noopener noreferrer">
                {s.name} ↗
              </a>
            </li>
          ))}
        </ul>
        <p className="rail__lang-hint mono">{t(lang, "rail_lang_hint")}</p>
      </div>
    </aside>
  );
}
