import type { Gene, ProteinDomain } from "@/lib/types";
import { t, type Locale } from "@/lib/i18n";
import { FigureCaption } from "@/components/FigureCaption";

type Props = { gene: Gene; locale?: Locale; lang?: Locale };

/** Ink, gray, one rust. Repeats are disambiguated by the legend, not by hue. */
const INKS = ["#1A1A1A", "#8A8478", "#8B3A2F"] as const;

function domainName(d: ProteinDomain, locale: Locale): string {
  if (locale === "en") return d.name || d.id || "—";
  return d.name_zh || d.name || d.id || "—";
}

function usable(list: ProteinDomain[] | null | undefined): ProteinDomain[] {
  if (!Array.isArray(list)) return [];
  return list.filter(
    (d) =>
      d &&
      typeof d.start === "number" &&
      typeof d.end === "number" &&
      Number.isFinite(d.start) &&
      Number.isFinite(d.end) &&
      d.end > d.start,
  );
}

function assignLanes(domains: ProteinDomain[]): number[] {
  const order = domains
    .map((d, i) => ({ i, d }))
    .sort((a, b) => a.d.start - b.d.start || a.d.end - b.d.end);
  const laneEnds: number[] = [];
  const lanes = new Array<number>(domains.length).fill(0);
  for (const { i, d } of order) {
    let lane = laneEnds.findIndex((end) => end < d.start);
    if (lane < 0) {
      lane = laneEnds.length;
      laneEnds.push(d.end);
    } else {
      laneEnds[lane] = d.end;
    }
    lanes[i] = lane;
  }
  return lanes;
}

export function DomainStrip({ gene, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";
  const domains = usable(gene.domains);
  const lanes = assignLanes(domains);
  const laneCount = Math.max(1, lanes.reduce((m, n) => Math.max(m, n + 1), 1));
  const proteinEnd = domains.reduce((m, d) => Math.max(m, d.end), 1);
  const proteinStart = 1;

  return (
    <section id="domains" className="domain-strip block reveal" aria-labelledby="domain-strip-label">
      <h2 className="section-label section-label--zh" id="domain-strip-label">
        {t(L, "section_domains")}
      </h2>
      {domains.length === 0 ? (
        <p className="domain-strip__empty">{t(L, "domains_empty")}</p>
      ) : (
        <>
          <div
            className="domain-strip__board"
            role="img"
            aria-label={t(L, "domains_aria")}
          >
            <div className="domain-strip__axis">
              <span>{t(L, "domain_axis_n")}</span>
              <span className="mono">
                {proteinStart}–{proteinEnd}
              </span>
              <span>{t(L, "domain_axis_c")}</span>
            </div>
            <div
              className="domain-strip__track"
              style={{ height: `${laneCount * 1.35}rem` }}
            >
              {domains.map((d, i) => {
                const left = ((d.start - 1) / proteinEnd) * 100;
                const width = Math.max(0.8, ((d.end - d.start) / proteinEnd) * 100);
                const ink = INKS[i % INKS.length];
                const fg = i % INKS.length === 1 ? "#1A1A1A" : "#F4F0E6";
                const label = domainName(d, L);
                return (
                  <span
                    key={d.id || `${d.name}-${d.start}`}
                    className="domain-strip__seg"
                    style={{
                      left: `${left}%`,
                      width: `${Math.min(width, 100 - left)}%`,
                      top: `${lanes[i] * 1.35}rem`,
                      background: ink,
                      color: fg,
                    }}
                    title={`${label} ${d.start}–${d.end}`}
                  >
                    {width >= 12 ? label : ""}
                  </span>
                );
              })}
            </div>
          </div>
          <ul className="domain-strip__legend">
            {domains.map((d, i) => (
              <li key={(d.id || d.name) + i}>
                <i
                  className="domain-strip__swatch"
                  style={{ background: INKS[i % INKS.length] }}
                  aria-hidden="true"
                />
                <span className="domain-strip__name">{domainName(d, L)}</span>
                <span className="mono domain-strip__range">
                  {d.start}–{d.end}
                </span>
                {d.url ? (
                  <a href={d.url} target="_blank" rel="noopener noreferrer">
                    {d.source || t(L, "ext_link")}
                  </a>
                ) : (
                  <span>{d.source || ""}</span>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
      <FigureCaption
        figureNo={3}
        titleKey="fig_domain_title"
        bodyFallback={t(
          L,
          domains.length ? "fig_domain_body" : "fig_domain_empty_body",
        )}
        locale={L}
      />
    </section>
  );
}
