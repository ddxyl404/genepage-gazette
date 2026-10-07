import Link from "next/link";
import { notFound } from "next/navigation";
import { Masthead } from "@/components/Masthead";
import { IssueHero } from "@/components/IssueHero";
import { PullBand } from "@/components/PullBand";
import { DualColumns } from "@/components/DualColumns";
import { FigureStack } from "@/components/FigureStack";
import { VariantsTable } from "@/components/VariantsTable";
import { Colophon } from "@/components/Colophon";
import { RevealInit } from "@/components/RevealInit";
import { fetchGene } from "@/lib/api";
import { pickDeck, resolveLocale, t, withLang } from "@/lib/i18n";

export const revalidate = 60;

type Props = {
  params: { symbol: string };
  searchParams?: { lang?: string };
};

export async function generateMetadata({ params, searchParams }: Props) {
  const symbol = decodeURIComponent(params.symbol).toUpperCase();
  const lang = resolveLocale(searchParams);
  return {
    title: `${symbol} · GenePage Gazette ${t(lang, "title_zh_suffix")}`,
  };
}

export default async function GenePage({ params, searchParams }: Props) {
  const symbol = decodeURIComponent(params.symbol);
  const lang = resolveLocale(searchParams);
  const gene = await fetchGene(symbol);
  if (!gene) notFound();

  const printHref = `/g/${encodeURIComponent(gene.symbol)}/print`;
  const deck = pickDeck(gene, lang);

  return (
    <article
      className="page page--gene page--p39"
      data-gene-id={gene.id}
      data-symbol={gene.symbol}
      data-lang={lang}
      data-layout="p39"
    >
      <RevealInit />
      <Masthead
        gene={gene}
        dataAsOf={gene.colophon?.data_as_of}
        edition={gene.colophon?.edition}
        printHref={printHref}
        lang={lang}
        ink
      />
      <div className="page-frame">
        <IssueHero gene={gene} lang={lang} />
        <PullBand deck={deck} lang={lang} />
        <div className="page-flow">
          <DualColumns gene={gene} lang={lang} />
          <FigureStack gene={gene} lang={lang} />
          <VariantsTable gene={gene} lang={lang} />
        </div>
      </div>
      <Colophon gene={gene} printHref={printHref} lang={lang} />
      <p className="footer-mini no-print">
        <Link href={withLang(printHref, lang)}>{t(lang, "print_page")}</Link>
        <span className="sep"> · </span>
        {t(lang, "footer_style")}
      </p>
    </article>
  );
}
