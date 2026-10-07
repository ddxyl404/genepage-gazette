import type { Gene, HeadlineStat } from "@/lib/types";
import { headlineLabel, pickDeck, t, type Locale } from "@/lib/i18n";
import { IssueToc } from "@/components/IssueToc";

type Props = {
  gene: Gene;
  lang: Locale;
  /** Print: static TOC */
  print?: boolean;
};

function topTissueTpm(gene: Gene): string | null {
  const tissues = gene.expression?.tissues || [];
  if (!tissues.length) return null;
  const top = [...tissues]
    .filter((ti) => ti && typeof ti.value === "number" && Number.isFinite(ti.value))
    .sort((a, b) => b.value - a.value)[0];
  if (!top) return null;
  const unit = gene.expression?.unit || "TPM";
  return `${Number(top.value).toFixed(1)} ${unit}`;
}

function displayValue(stat: HeadlineStat, locale: Locale, gene: Gene): string {
  if (stat.key === "top_tissue") {
    return topTissueTpm(gene) || (stat.value != null ? String(stat.value) : "—");
  }
  if (stat.value == null) return "—";
  if (typeof stat.value === "number") {
    if (Number.isInteger(stat.value)) return stat.value.toLocaleString("en-US");
    return Number(stat.value).toFixed(1);
  }
  return String(stat.value);
}

function statNote(stat: HeadlineStat, locale: Locale, gene: Gene): string {
  if (stat.key === "top_tissue") {
    if (locale === "en") {
      return stat.detail?.split(" - ").pop() || String(stat.value || "");
    }
    return String(stat.value || stat.detail || "");
  }
  if (stat.key === "location") {
    const loc = gene.location;
    return `${loc.assembly}`;
  }
  if (stat.as_of) return `${t(locale, "as_of_prefix")} ${stat.as_of}`;
  return "";
}

function pickAlias(gene: Gene): string {
  const aliases = (gene.aliases || []).filter(
    (a) => a && a.toUpperCase() !== gene.symbol.toUpperCase(),
  );
  if (!aliases.length) return "";
  // Prefer short familiar symbols (e.g. P53) over obscure locus codes (BCC7).
  const scored = [...aliases].sort((a, b) => {
    const score = (s: string) => {
      let n = 0;
      if (/^p\d+$/i.test(s) || /^[A-Z]{1,4}\d{0,2}$/i.test(s)) n += 3;
      if (s.length <= 5) n += 2;
      if (/^[A-Z]/i.test(s) && !/^[A-Z]{2,}\d{2,}$/.test(s)) n += 1;
      if (/^(BMFS|BCC|LFS|C\d)/i.test(s)) n -= 2;
      return n;
    };
    return score(b) - score(a) || a.length - b.length;
  });
  return scored[0] || "";
}

function subtitle(gene: Gene, lang: Locale): string {
  const band =
    gene.cytoband?.band_label ||
    gene.headline_stats?.find((s) => s.key === "location")?.value ||
    "";
  const alias = pickAlias(gene);
  const typeLabel =
    gene.type === "protein_coding"
      ? lang === "zh"
        ? "蛋白编码"
        : "protein coding"
      : gene.type;
  return [alias, typeLabel, band ? String(band) : ""].filter(Boolean).slice(0, 3).join(" · ");
}

export function IssueHero({ gene, lang, print = false }: Props) {
  const deck = pickDeck(gene, lang);
  const stats = gene.headline_stats || [];
  const sub = subtitle(gene, lang);

  return (
    <section
      id="lede"
      className="issue-hero reveal"
      aria-label={t(lang, "issue_hero_aria")}
    >
      <div className="issue-hero__grid">
        <div className="issue-hero__cover">
          <p className="issue-hero__kicker">{t(lang, "cover_kicker")}</p>
          <h2 className="issue-hero__symbol">{gene.symbol}</h2>
          {sub ? <p className="issue-hero__sub">{sub}</p> : null}
          <p className="issue-hero__lede">{deck}</p>
          {stats.length > 0 && (
            <div
              className="issue-hero__stats"
              aria-label={t(lang, "headline_aria")}
            >
              {stats.map((stat) => (
                <div className="issue-stat" key={stat.key}>
                  <p className="issue-stat__label">{headlineLabel(lang, stat)}</p>
                  <p className="issue-stat__value">
                    {displayValue(stat, lang, gene)}
                  </p>
                  <p className="issue-stat__note">{statNote(stat, lang, gene)}</p>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="issue-hero__toc">
          <IssueToc lang={lang} static={print} />
        </div>
      </div>
    </section>
  );
}
