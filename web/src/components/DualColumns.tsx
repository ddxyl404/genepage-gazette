import type { Gene } from "@/lib/types";
import { type Locale, t } from "@/lib/i18n";

type Props = { gene: Gene; locale?: Locale; lang?: Locale };

function pathwayLinkLabel(
  pw: { name: string; url: string; source?: string },
  locale: Locale,
): string {
  if (pw.source) return pw.source;
  const u = (pw.url || "").toLowerCase();
  if (u.includes("kegg")) return "KEGG";
  if (u.includes("reactome")) return "Reactome";
  if (u.includes("wikipathways")) return "WikiPathways";
  if (u.includes("geneontology") || u.includes("amigo")) return "GO";
  return t(locale, "ext_link");
}

/** Short dual column: identity/naming · pathways (text only; no figures). */
export function DualColumns({ gene, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";

  return (
    <div className="columns columns--p35 columns--short columns--p37">
      <div className="col col--identity">
        <section className="block" aria-labelledby="id-label">
          <h2 className="section-label section-label--zh" id="id-label">
            {t(L, "section_identity")}
          </h2>
          <dl className="identity-dl">
            <dt>Ensembl</dt>
            <dd>
              <span className="mono">{gene.id}</span>
            </dd>
            <dt>HGNC</dt>
            <dd>{gene.symbol}</dd>
            <dt>{t(L, "dt_aliases")}</dt>
            <dd>{(gene.aliases || []).join(", ") || "—"}</dd>
            <dt>{t(L, "dt_assembly")}</dt>
            <dd>
              <span className="mono">
                {gene.location.assembly} · {gene.location.chrom}:
                {gene.location.start}–{gene.location.end}
              </span>
            </dd>
            <dt>{t(L, "dt_gene_type")}</dt>
            <dd>{gene.type}</dd>
          </dl>
        </section>
      </div>

      <div className="col col--pathways">
        <section className="block" aria-labelledby="pw-label">
          <h2 className="section-label section-label--zh" id="pw-label">
            {t(L, "section_pathways")}
          </h2>
          <ul className="pathways">
            {(gene.pathways || []).slice(0, 6).map((pw) => (
              <li key={pw.url + pw.name}>
                <span>{pw.name.replace(/ - Homo sapiens \(human\)$/, "")}</span>
                <a
                  className="ext"
                  href={pw.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {pathwayLinkLabel(pw, L)} ↗
                </a>
              </li>
            ))}
            {(gene.pathways || []).length === 0 && (
              <li>
                <span>{t(L, "empty_pathways")}</span>
              </li>
            )}
          </ul>
        </section>
      </div>
    </div>
  );
}
