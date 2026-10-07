import type { Gene } from "@/lib/types";
import { pickCaption, t, type Locale } from "@/lib/i18n";
import { FigureCaption } from "@/components/FigureCaption";

type Props = { gene: Gene; locale?: Locale; lang?: Locale };

/**
 * preview_image in gene JSON is a cache-relative path (cache/alphafold/TP53.png).
 * Never use that string as an img src. The public route is
 * GET /api/figures/alphafold/{SYMBOL}, which Next rewrites to the API.
 * Null / empty → journal empty state (BRCA2).
 */
export function structurePreviewSrc(gene: Gene): string | null {
  const raw = (gene.structure?.preview_image || "").trim();
  if (!raw) return null;
  if (/^https?:\/\//i.test(raw)) return raw;
  if (raw.startsWith("/") && !raw.startsWith("//")) return raw;
  const symbol = (gene.symbol || "").trim();
  if (!symbol) return null;
  return `/api/figures/alphafold/${encodeURIComponent(symbol)}`;
}

export function StructurePreview({ gene, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";
  const src = structurePreviewSrc(gene);
  const afUrl = gene.structure?.alphafold_url;
  const afId = afUrl ? afUrl.split("/").filter(Boolean).pop() : null;

  return (
    <section
      id="structure"
      className="structure-preview structure structure--p35 block reveal"
      aria-labelledby="struct-label"
    >
      <h2 className="section-label section-label--zh" id="struct-label">
        {t(L, "section_structure")}
      </h2>
      <div className="structure-preview__frame structure__frame">
        {src ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            className="structure-preview__img"
            src={src}
            alt={`${gene.symbol} AlphaFold`}
          />
        ) : (
          <div className="structure-preview__empty structure__placeholder">
            <em>{t(L, "structure_empty_title")}</em>
            {t(L, "structure_empty_body")}
          </div>
        )}
      </div>
      <div className="structure__footer">
        <span className="mono">{afId || "—"}</span>
        {afUrl ? (
          <a href={afUrl} target="_blank" rel="noopener noreferrer">
            {t(L, "open_alphafold")}
          </a>
        ) : (
          <span>{t(L, "no_structure_link")}</span>
        )}
      </div>
      <FigureCaption
        dataCaption={pickCaption(gene.structure, L, "")}
        figureNo={4}
        titleKey="fig_struct_title"
        bodyFallback={t(L, "fig_struct_body")}
        locale={L}
      />
    </section>
  );
}
