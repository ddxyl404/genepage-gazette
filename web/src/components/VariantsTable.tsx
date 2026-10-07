import type { Gene, VariantRow } from "@/lib/types";
import { t, type Locale } from "@/lib/i18n";

type Props = {
  gene: Gene;
  locale?: Locale;
  lang?: Locale;
  /** Print: open details by default */
  defaultOpen?: boolean;
};

function significanceClass(sig?: string | null): string {
  if (!sig) return "";
  const s = sig.toLowerCase();
  if (s.includes("pathogenic")) return "sig-plp";
  return "sig-vus";
}

export function VariantsTable({
  gene,
  locale,
  lang,
  defaultOpen = false,
}: Props) {
  const L: Locale = locale || lang || "zh";
  const vs = gene.variants_summary;
  const p = vs?.clinvar_pathogenic ?? 0;
  const lp = vs?.clinvar_likely_pathogenic ?? 0;
  const total = p + lp;
  const rows: VariantRow[] = vs?.rows || [];
  const note =
    (L === "en" ? (vs as { note_en?: string } | undefined)?.note_en : undefined) ||
    vs?.note_zh ||
    t(L, "variants_note_fallback");

  return (
    <section id="variants" className="variants variants--p35 reveal" aria-labelledby="var-label">
      <h2 className="section-label section-label--zh" id="var-label">
        {t(L, "section_variants")}
      </h2>

      <div
        className="variants-strip"
        aria-label={t(L, "variants_strip_aria")}
      >
        <div className="variants-strip__item">
          <span className="variants-strip__label">Pathogenic</span>
          <span className="variants-strip__value mono sig-plp">{p}</span>
        </div>
        <div className="variants-strip__item">
          <span className="variants-strip__label">Likely pathogenic</span>
          <span className="variants-strip__value mono sig-plp">{lp}</span>
        </div>
        <div className="variants-strip__item">
          <span className="variants-strip__label">P + LP</span>
          <span className="variants-strip__value mono">{total}</span>
        </div>
      </div>

      <details className="variants-details" open={defaultOpen || undefined}>
        <summary className="variants-details__summary">
          <span>{t(L, "variants_details")}</span>
          <span className="variants-details__count mono">
            {rows.length > 0 ? rows.length : "—"}
          </span>
        </summary>
        <div className="table-wrap">
          <table className="variants-table">
            <thead>
              <tr>
                <th scope="col">{t(L, "th_rsid")}</th>
                <th scope="col">{t(L, "th_hgvs")}</th>
                <th scope="col">{t(L, "th_sig")}</th>
                <th scope="col">{t(L, "th_note")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={4} className="variants-empty">
                    {t(L, "variants_details_empty")}
                  </td>
                </tr>
              ) : (
                rows.map((row, i) => (
                  <tr key={`${row.rsid || ""}-${row.hgvs_p || ""}-${i}`}>
                    <td className="mono">{row.rsid || "—"}</td>
                    <td className="mono">{row.hgvs_p || "—"}</td>
                    <td className={significanceClass(row.significance)}>
                      {row.significance || "—"}
                    </td>
                    <td>
                      {L === "en"
                        ? (row as { note_en?: string }).note_en ||
                          row.note_zh ||
                          "—"
                        : row.note_zh || "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </details>

      <p className="table-note">
        {t(L, "variants_summary", { p, lp, total })}
        {rows.length === 0
          ? t(L, "variants_only_counts")
          : t(L, "variants_excerpt")}{" "}
        {note}
      </p>
    </section>
  );
}
