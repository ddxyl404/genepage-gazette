import type { Gene } from "@/lib/types";
import { type Locale } from "@/lib/i18n";
import { ChromIdeogram } from "@/components/ChromIdeogram";
import { ExpressionBars } from "@/components/ExpressionBars";
import { DomainStrip } from "@/components/DomainStrip";
import { StructurePreview } from "@/components/StructurePreview";

type Props = { gene: Gene; locale?: Locale; lang?: Locale };

/** Full-bleed magazine figure stack: chrom → expression bars → domains → structure. */
export function FigureStack({ gene, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";

  return (
    <div className="figure-stack" data-layout="figure-stack">
      <ChromIdeogram gene={gene} locale={L} />
      <ExpressionBars gene={gene} locale={L} />
      <DomainStrip gene={gene} locale={L} />
      <StructurePreview gene={gene} locale={L} />
    </div>
  );
}
