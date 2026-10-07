import type { Gene } from "@/lib/types";
import { fetchCytobandFigure } from "@/lib/api";
import { pickCaption, t, type Locale } from "@/lib/i18n";
import {
  bandAt,
  chromKey,
  chromLength,
  parseCytobandPayload,
  schematicBands,
  stainFill,
  stainIsAcen,
  type NormBand,
} from "@/lib/ideogram";
import { FigureCaption } from "@/components/FigureCaption";

type Props = { gene: Gene; locale?: Locale; lang?: Locale };

const VB_W = 600;
const PAD_X = 18;
const PLOT_Y = 28;
const PLOT_H = 36;
const PLOT_W = VB_W - PAD_X * 2;

function fmtInt(n: number): string {
  return Math.round(n).toLocaleString("en-US");
}

export async function ChromIdeogram({ gene, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";
  const loc = gene.location;
  const meta = gene.cytoband || null;
  const key = chromKey(meta?.chrom || loc?.chrom || "");
  const start = loc?.start ?? meta?.start ?? 0;
  const end = loc?.end ?? meta?.end ?? start;
  const assembly = loc?.assembly || meta?.assembly || "GRCh38";

  let bands: NormBand[] | null = null;
  let source: "file" | "gene" | "schematic" = "schematic";
  if (meta?.bands?.length) {
    bands = parseCytobandPayload(meta);
    if (bands) source = "gene";
  }
  if (!bands && key) {
    try {
      const raw = await fetchCytobandFigure(key);
      bands = parseCytobandPayload(raw);
      if (bands) source = "file";
    } catch {
      bands = null;
    }
  }
  const chromLen = chromLength(key, bands || [], end);
  if (!bands) {
    bands = schematicBands(key || "?", chromLen);
    source = "schematic";
  }

  const mid = (start + end) / 2;
  const xOf = (bp: number) =>
    PAD_X + (Math.min(chromLen, Math.max(0, bp)) / chromLen) * PLOT_W;
  const pinX = xOf(mid);
  const hit = bandAt(bands, mid);
  const bandLabel =
    (meta?.band_label || "").trim() ||
    (hit?.id ? `${key}${hit.id.startsWith("p") || hit.id.startsWith("q") ? "" : " "}${hit.id}` : "");
  const clipId = `ideo-${gene.symbol || "gene"}-${key || "x"}`;

  const aria = t(L, "chrom_ideogram_aria", {
    assembly,
    chrom: key || "?",
    band: bandLabel || "—",
  });

  const captionBody =
    t(L, "fig_chrom_body", {
      assembly,
      chrom: key || "?",
      start: fmtInt(start),
      end: fmtInt(end),
      band: bandLabel || "—",
    }) + (source === "schematic" ? ` ${t(L, "ideogram_schematic")}` : "");

  return (
    <section
      id="cyto"
      className="chrom-ideogram block reveal"
      data-ideogram={source}
      data-band={bandLabel || undefined}
      aria-labelledby="chrom-ideogram-label"
    >
      <h2 className="section-label section-label--zh" id="chrom-ideogram-label">
        {t(L, "section_chrom")}
      </h2>
      <div className="chrom-ideogram__board">
        <div className="chrom-ideogram__head">
          <span className="chrom-ideogram__chrom mono">chr{key || "?"}</span>
          {bandLabel ? (
            <span className="chrom-ideogram__band mono">{bandLabel}</span>
          ) : null}
          <span className="chrom-ideogram__assembly mono">{assembly}</span>
        </div>
        <svg
          className="chrom-ideogram__svg"
          viewBox={`0 0 ${VB_W} 96`}
          role="img"
          aria-label={aria}
        >
          <title>{aria}</title>
          <defs>
            <clipPath id={clipId}>
              <rect
                x={PAD_X}
                y={PLOT_Y}
                width={PLOT_W}
                height={PLOT_H}
                rx={PLOT_H / 2}
              />
            </clipPath>
          </defs>
          <g clipPath={`url(#${clipId})`}>
            {bands.map((b) => {
              const x = xOf(b.start);
              const w = Math.max(0.4, xOf(b.end) - x);
              const acen = stainIsAcen(b.stain);
              const y = acen ? PLOT_Y + 8 : PLOT_Y;
              const h = acen ? PLOT_H - 16 : PLOT_H;
              return (
                <rect
                  key={`${b.id}-${b.start}`}
                  className="chrom-ideogram__band"
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  fill={stainFill(b.stain)}
                >
                  <title>{`${b.id} ${b.stain}`}</title>
                </rect>
              );
            })}
          </g>
          <rect
            x={PAD_X}
            y={PLOT_Y}
            width={PLOT_W}
            height={PLOT_H}
            rx={PLOT_H / 2}
            fill="none"
            stroke="#1A1A1A"
            strokeWidth="1"
          />
          <line
            className="chrom-ideogram__pin"
            x1={pinX}
            y1={12}
            x2={pinX}
            y2={PLOT_Y}
            stroke="#8B3A2F"
            strokeWidth="1.4"
          />
          <circle
            className="chrom-ideogram__pin"
            cx={pinX}
            cy={9}
            r="3.3"
            fill="#8B3A2F"
          />
          <text x={PAD_X} y={86} className="chrom-ideogram__tick">
            pter
          </text>
          <text
            x={VB_W - PAD_X}
            y={86}
            textAnchor="end"
            className="chrom-ideogram__tick"
          >
            qter
          </text>
        </svg>
        <div className="chrom-ideogram__coords mono">
          {fmtInt(start)} – {fmtInt(end)}
        </div>
      </div>
      <FigureCaption
        dataCaption={pickCaption(meta, L, "")}
        figureNo={1}
        titleKey="fig_chrom_title"
        bodyFallback={captionBody}
        locale={L}
      />
    </section>
  );
}
