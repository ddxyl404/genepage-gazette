import Link from "next/link";
import { notFound } from "next/navigation";
import { Masthead } from "@/components/Masthead";
import { IssueHero } from "@/components/IssueHero";
import { PullBand } from "@/components/PullBand";
import { DualColumns } from "@/components/DualColumns";
import { FigureStack } from "@/components/FigureStack";
import { VariantsTable } from "@/components/VariantsTable";
import { Colophon } from "@/components/Colophon";
import { PrintBar } from "@/components/PrintBar";
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
    title: `${symbol} · ${t(lang, "footer_print")} · GenePage Gazette`,
  };
}

export default async function GenePrintPage({ params, searchParams }: Props) {
  const symbol = decodeURIComponent(params.symbol);
  const lang = resolveLocale(searchParams);
  const gene = await fetchGene(symbol);
  if (!gene) notFound();

  const screenHref = `/g/${encodeURIComponent(gene.symbol)}`;
  const deck = pickDeck(gene, lang);

  return (
    <article
      className="page page--gene page--print page--p39"
      data-gene-id={gene.id}
      data-symbol={gene.symbol}
      data-layout="print-p39"
      data-lang={lang}
    >
      <div className="print-toolbar no-print">
        <Link href={withLang(screenHref, lang)}>{t(lang, "back_screen")}</Link>
        <PrintBar lang={lang} />
      </div>
      <Masthead
        gene={gene}
        dataAsOf={gene.colophon?.data_as_of}
        edition={gene.colophon?.edition}
        showSearch={false}
        lang={lang}
        ink
      />
      <div className="page-frame">
        <IssueHero gene={gene} lang={lang} print />
        <PullBand deck={deck} lang={lang} />
        <div className="page-flow">
          <DualColumns gene={gene} lang={lang} />
          <FigureStack gene={gene} lang={lang} />
          <VariantsTable gene={gene} lang={lang} defaultOpen />
        </div>
      </div>
      <Colophon gene={gene} lang={lang} />
      <p className="footer-mini">
        GenePage Gazette · Style C · P3.9 · {t(lang, "footer_print")} ·{" "}
        {gene.symbol}
      </p>
    </article>
  );
}
