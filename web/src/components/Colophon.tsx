import Link from "next/link";
import type { Gene } from "@/lib/types";
import {
  type Locale,
  disclaimerText,
  t,
  withLang,
} from "@/lib/i18n";

type Props = {
  gene?: Gene;
  edition?: string;
  dataAsOf?: string;
  disclaimer?: string;
  apiHint?: string;
  printHref?: string;
  lang?: Locale;
  locale?: Locale;
};

export function Colophon({
  gene,
  edition,
  dataAsOf,
  disclaimer,
  apiHint,
  printHref,
  lang,
  locale,
}: Props) {
  const L: Locale = locale || lang || "zh";
  const ed = gene?.colophon?.edition || edition || "0.3.0-p35";
  const asOf = gene?.colophon?.data_as_of || dataAsOf || "2026-09-29";
  const disc = disclaimer || disclaimerText(gene, L);
  const api =
    apiHint ||
    (gene ? `GET /api/gene/${gene.symbol}` : "GET /api/search?q=");
  const sources = gene?.sources?.map((s) => s.name).join(" · ");
  const printLink = printHref ? withLang(printHref, L) : undefined;

  return (
    <footer className="colophon">
      <p className="colophon__disclaimer">{disc}</p>
      <p className="colophon__meta">
        <span>edition {ed}</span>
        <span>data_as_of {asOf}</span>
        <a href={gene ? `/api/gene/${gene.symbol}` : "/api/search?q="}>{api}</a>
        {printLink && (
          <Link className="no-print" href={printLink}>
            {t(L, "print_page")}
          </Link>
        )}
      </p>
      {sources && (
        <p className="colophon__sources">
          {t(L, "sources_prefix")}
          {sources}
        </p>
      )}
    </footer>
  );
}
