import type { Gene, HeadlineStat } from "@/lib/types";
import { headlineLabel, t, type Locale } from "@/lib/i18n";

type Props = {
  gene: Gene;
  locale?: Locale;
  lang?: Locale;
  /** Default full-width strip; rail = condensed vertical in sticky sidebar */
  variant?: "default" | "rail";
};

function asofLine(stat: HeadlineStat, gene: Gene, locale: Locale): string {
  if (stat.key === "location") {
    const loc = gene.location;
    return `${loc.assembly} · chr${loc.chrom}:${loc.start.toLocaleString()}–${loc.end.toLocaleString()}`;
  }
  if (stat.key === "top_tissue") {
    const bits: string[] = [];
    if (stat.detail) bits.push(stat.detail);
    if (stat.as_of) bits.push(`${t(locale, "as_of_prefix")} ${stat.as_of}`);
    return bits.join(" · ");
  }
  if (stat.as_of) {
    if (stat.key === "clinvar_plp")
      return `${t(locale, "as_of_prefix")} ${stat.as_of} · P+LP`;
    return `${t(locale, "as_of_prefix")} ${stat.as_of}`;
  }
  return "";
}

function displayValue(stat: HeadlineStat, locale: Locale): string {
  if (stat.value == null) return "—";
  if (typeof stat.value === "number") {
    // Integers → toLocaleString; fractional TPM-like → one decimal
    if (Number.isInteger(stat.value)) {
      return stat.value.toLocaleString("en-US");
    }
    return Number(stat.value).toFixed(1);
  }
  if (locale === "en" && stat.key === "top_tissue" && stat.detail) {
    const short = stat.detail.split(" - ").pop() || stat.detail;
    return short.length > 28 ? String(stat.value) : short;
  }
  return String(stat.value);
}

/** Optional TPM footnote for top_tissue from existing expression.tissues */
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

export function HeadlineStats({
  gene,
  locale,
  lang,
  variant = "default",
}: Props) {
  const L: Locale = locale || lang || "zh";
  const stats = gene.headline_stats || [];
  const isRail = variant === "rail";
  const tpmNote = isRail ? topTissueTpm(gene) : null;

  return (
    <section
      className={
        isRail
          ? "headline-stats headline-stats--rail"
          : "headline-stats headline-stats--p35"
      }
      aria-label={t(L, "headline_aria")}
    >
      {stats.map((stat) => {
        const value = displayValue(stat, L);
        const isLong = value.length > 10;
        return (
          <div className="stat" key={stat.key}>
            <p className="stat__label">{headlineLabel(L, stat)}</p>
            <p
              className={
                isLong ? "stat__value stat__value--sm" : "stat__value"
              }
            >
              {value}
            </p>
            {isRail && stat.key === "top_tissue" && tpmNote ? (
              <p className="stat__asof mono">{tpmNote}</p>
            ) : (
              <p className="stat__asof">{asofLine(stat, gene, L)}</p>
            )}
          </div>
        );
      })}
    </section>
  );
}
