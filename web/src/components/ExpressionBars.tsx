import type { Gene, TissueExpr } from "@/lib/types";
import { pickCaption, t, type Locale } from "@/lib/i18n";
import { FigureCaption } from "@/components/FigureCaption";
import { ExprBarsChart } from "@/components/ExprBarsChart";

type Props = { gene: Gene; locale?: Locale; lang?: Locale };

const TOP_N = 12;

export function ExpressionBars({ gene, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";
  const source = gene.expression?.source || "GTEx";
  const unit = gene.expression?.unit || "TPM";
  const ranked: TissueExpr[] = [...(gene.expression?.tissues || [])]
    .filter((ti) => ti && typeof ti.value === "number" && Number.isFinite(ti.value))
    .sort((a, b) => b.value - a.value)
    .slice(0, TOP_N);
  const maxVal = Math.max(1e-9, ...ranked.map((ti) => ti.value));

  return (
    <section
      id="expression"
      className="expr-bars block reveal"
      aria-labelledby="expr-bars-label"
    >
      <h2 className="section-label section-label--zh" id="expr-bars-label">
        {t(L, "section_expression", { source })}
      </h2>
      {ranked.length === 0 ? (
        <p className="expr-bars__empty">{t(L, "empty_expression")}</p>
      ) : (
        <>
          <ExprBarsChart ranked={ranked} maxVal={maxVal} locale={L} />
          <div className="legend">
            <span>
              <span className="legend__swatch" aria-hidden="true" />
              {t(L, "legend_median", { unit })}
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
