import type { Gene, TissueExpr } from "@/lib/types";
import { pickCaption, pickTissueName, t, type Locale } from "@/lib/i18n";
import { FigureCaption } from "@/components/FigureCaption";

type Props = { gene: Gene; locale?: Locale; lang?: Locale };

const TOP_N = 12;

export function ExpressionMultiples({ gene, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";
  const source = gene.expression?.source || "GTEx";
  const unit = gene.expression?.unit || "TPM";
  const ranked: TissueExpr[] = [...(gene.expression?.tissues || [])]
    .filter((ti) => ti && typeof ti.value === "number" && Number.isFinite(ti.value))
    .sort((a, b) => b.value - a.value)
    .slice(0, TOP_N);
  const maxVal = Math.max(1e-9, ...ranked.map((ti) => ti.value));

  return (
    <section className="expr-multiples block" aria-labelledby="expr-label">
      <h2 className="section-label section-label--zh" id="expr-label">
        {t(L, "section_expression", { source })}
      </h2>
      {ranked.length === 0 ? (
        <p className="expr-multiples__empty">{t(L, "empty_expression")}</p>
      ) : (
        <>
          <div
            className="expr-multiples__grid"
            role="img"
            aria-label={t(L, "expr_multiples_aria")}
          >
            {ranked.map((ti, i) => {
              const pct = Math.max(2, Math.round((ti.value / maxVal) * 1000) / 10);
              return (
                <figure className="expr-multiples__cell" key={`${ti.name}-${i}`}>
                  <div className="expr-multiples__plot">
                    <div
                      className={
                        i === 0
                          ? "expr-multiples__bar expr-multiples__bar--top"
                          : "expr-multiples__bar"
                      }
                      style={{ height: `${pct}%` }}
                    />
                  </div>
                  <figcaption>
                    <span className="expr-multiples__name">
                      {pickTissueName(ti, L)}
                    </span>
                    <span className="expr-multiples__val mono">
                      {Number(ti.value).toFixed(1)}
                    </span>
                  </figcaption>
                </figure>
              );
            })}
          </div>
          <div className="legend">
            <span>
              <span
                className="legend__swatch legend__swatch--ink"
                aria-hidden="true"
              />
              {t(L, "legend_other")}
            </span>
            <span>
              <span className="legend__swatch" aria-hidden="true" />
              {t(L, "legend_top")}
            </span>
            <span>{t(L, "legend_source", { source, unit })}</span>
          </div>
        </>
      )}
      <FigureCaption
        dataCaption={pickCaption(gene.expression, L, "")}
        figureNo={2}
        titleKey="fig_expr_title"
        bodyFallback={t(L, "fig_expr_body", { unit, source })}
        locale={L}
      />
    </section>
  );
}
