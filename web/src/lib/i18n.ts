import type { Gene, TissueExpr } from "./types";

/** Canonical locale type; `Lang` is an alias used by P3.5 shell components. */
export type Locale = "zh" | "en";
export type Lang = Locale;

export const LANG_STORAGE_KEY = "genepage_lang";
export const DEFAULT_LOCALE: Locale = "zh";

type Dict = Record<string, string>;

const zh: Dict = {
  title_zh_suffix: "基因简报",
  data_as_of: "数据截至",
  print_page: "印刷本页",
  aliases_prefix: "别名：",
  search_aria: "基因搜索",
  search_placeholder: "搜索基因符号…",
  search_placeholder_home: "输入基因符号，如 TP53、BRCA1…",
  search_btn: "检索",
  deck_label: "导语",
  genes_count: "{n} 基因",
  download_csv: "下载 CSV",
  index_lead:
    "把每个基因做成一份可印刷感的科研短讯页。检索符号或 Ensembl ID，读完一页：导语、要闻三数、身份与通路、表达与结构、变异摘要。",
  catalog_today: "今日目录",
  catalog_query: " · 「{q}」",
  catalog_n: " · {n} 条",
  no_match: "无匹配基因",
  not_in_edition: "本期未收录",
  sources_prefix: "来源：",
  colophon_sources: "来源",
  disclaimer:
    "科研/教学信息工具，非医疗器械，不提供诊断建议。",
  colophon_disclaimer:
    "科研/教学信息工具，非医疗器械，不提供诊断建议。",
  back_screen: "← 返回屏幕版",
  print_btn: "打印 / 存为 PDF",
  print_hint: "使用浏览器打印对话框，版式按一页纸新闻纸简报优化",
  print_aria: "打印",
  section_identity: "身份 / 命名",
  section_pathways: "通路（节选）",
  section_expression: "表达（{source}）",
  section_structure: "结构",
  section_variants: "变异摘要",
  variants_section: "变异摘要",
  dt_aliases: "别名",
  dt_assembly: "组装 / 坐标",
  dt_gene_type: "基因类型",
  ext_link: "外链",
  empty_pathways: "本期未收录",
  empty_expression: "本期未收录表达数据。",
  expr_aria: "组织表达水平条形图",
  legend_median: "中位 {unit}",
  legend_source: "来源：{source} · unit: {unit}",
  fig1_title: "图 1 · 组织表达格局",
  fig1_body:
    "水平条为选定组织中位转录水平（单位：{unit}）。来源：{source} 本机汇总缓存。",
  structure_empty_title: "本期未收录预览图",
  structure_empty_body:
    "本期未附静态预览。可经外链在 AlphaFold DB 查看预测模型。",
  structure_empty_body_p35:
    "本期未附静态预览。可经外链在 AlphaFold DB 查看预测模型。",
  open_alphafold: "在 AlphaFold DB 打开 ↗",
  no_structure_link: "本期无结构外链",
  fig2_title: "图 2 · 结构外链",
  fig2_body:
    "静态缩略或 AlphaFold 外链；三维交互为增强，不挡首屏阅读。无预览图时写「本期未附结构图」。",
  chrom_ruler: "染色体标尺",
  section_chrom: "染色体带型",
  fig3_title: "图 3 · 染色体位置示意",
  fig3_body:
    "示意基因在 {assembly} chr{chrom} 上的相对位置（{start}–{end}）；非精确比例尺。",
  variants_strip_aria: "ClinVar P/LP 计数",
  th_rsid: "rsID / 标识",
  th_hgvs: "HGVS（蛋白）",
  th_sig: "ClinVar 意义",
  th_note: "备注",
  variants_col_rsid: "rsID / 标识",
  variants_col_hgvs: "HGVS（蛋白）",
  variants_col_sig: "ClinVar 意义",
  variants_col_note: "备注",
  variants_empty: "本期无逐条收录",
  variants_details_empty: "本期无逐条收录",
  variants_details: "展开明细",
  variants_summary:
    "摘要：ClinVar 致病 {p} · 可能致病 {lp}（合计 P/LP ≈ {total}，与要闻数字对齐）。",
  variants_only_counts: "本期仅提供 P/LP 计数，无逐条位点。",
  variants_excerpt: "本表仅列节选位点，非完整目录。",
  variants_note_fallback: "非诊断结论",
  headline_aria: "要闻三数",
  as_of_prefix: "as_of",
  not_found_lead: "本期未收录该基因。",
  back_catalog: "返回今日目录",
  footer_print: "印刷本",
  gene_demo: "本期示范基因",
  lang_aria: "语言",
  label_location: "基因组位置",
  label_clinvar_plp: "ClinVar 致病/可能致病",
  label_top_tissue: "GTEx 最高表达",
  aliases_label: "别名",
  edition_label: "卷期",

  section_domains: "蛋白结构域",
  domains_empty: "本期未收录",
  domains_aria: "蛋白结构域色带",
  domain_axis_n: "N",
  domain_axis_c: "C",
  fig_chrom_title: "图 1 · 染色体带型",
  fig_chrom_body:
    "墨色深浅为 G 带（{assembly} chr{chrom}，{band}）；铁锈红钉标基因中点 {start}–{end}。示意定位，非基因组浏览器。",
  fig_expr_title: "图 2 · 组织表达",
  fig_expr_body:
    "水平排行条按中位 TPM 降序（至多 12 个；单位 {unit}）。来源：{source} 本机汇总。",
  fig_domain_title: "图 3 · 蛋白结构域",
  fig_domain_body:
    "横条按氨基酸坐标从 N 端排到 C 端。色板仅墨、灰与一道铁锈红，见图例。",
  fig_domain_empty_body: "本期未收录结构域。",
  fig_struct_title: "图 4 · 结构预览",
  fig_struct_body:
    "AlphaFold 静态预览；无预览图时作空态，并保留数据库外链。三维交互不挡阅读。",
  expr_multiples_aria: "组织表达小倍数图",
  expr_bars_aria: "组织表达水平排行条",
  chrom_ideogram_aria: "{assembly} chr{chrom} 带型，位点 {band}",
  ideogram_schematic: "无带型底图时为简版深浅条。",
  legend_top: "最高",
  legend_other: "其余",
  footer_style: "GenePage Gazette · Style C · P3.9",

  toc_label: "本页目录",
  toc_lede: "要闻",
  toc_cyto: "基因组",
  toc_expression: "表达",
  toc_domains: "蛋白",
  toc_structure: "结构",
  toc_variants: "变异",
  rail_aria: "侧栏",
  rail_links: "外链与工具",
  rail_lang_hint: "语言：顶栏 zh | en",

  issue_toc_label: "本期目录",
  issue_toc_pieces: "篇",
  issue_hero_aria: "本期封面与目录",
  cover_kicker: "封面故事",
  pull_aria: "本期引语",
  pull_by: "— 本期导语",
  pull_emphasis: "供科研与教学查阅。",
  pull_fallback: "把每个基因做成一份可印刷感的科研短讯页。",
  toc_fig_lede: "要闻",
  toc_fig_cyto: "图 1",
  toc_fig_expr: "图 2",
  toc_fig_domain: "图 3",
  toc_fig_struct: "图 4",
  toc_fig_var: "表",

};

const en: Dict = {
  title_zh_suffix: "基因简报",
  data_as_of: "data as of",
  print_page: "Print page",
  aliases_prefix: "Aliases: ",
  search_aria: "Gene search",
  search_placeholder: "Search gene symbol…",
  search_placeholder_home: "Enter a gene symbol, e.g. TP53, BRCA1…",
  search_btn: "Search",
  deck_label: "Deck",
  genes_count: "{n} genes",
  download_csv: "Download CSV",
  index_lead:
    "One printable research brief per gene. Search by symbol or Ensembl ID; read the deck, headline stats, identity & pathways, expression & structure, and variant summary on a single page.",
  catalog_today: "Today's catalog",
  catalog_query: " · “{q}”",
  catalog_n: " · {n} entries",
  no_match: "No matching genes",
  not_in_edition: "Not in this edition",
  sources_prefix: "Sources: ",
  colophon_sources: "Sources",
  disclaimer:
    "Research/education information tool — not a medical device; no diagnostic advice.",
  colophon_disclaimer:
    "Research/education information tool — not a medical device; no diagnostic advice.",
  back_screen: "← Back to screen view",
  print_btn: "Print / Save as PDF",
  print_hint:
    "Use the browser print dialog; layout is tuned for a one-page newsprint brief",
  print_aria: "Print",
  section_identity: "Identity / naming",
  section_pathways: "Pathways (selected)",
  section_expression: "Expression ({source})",
  section_structure: "Structure",
  section_variants: "Variant summary",
  variants_section: "Variant summary",
  dt_aliases: "Aliases",
  dt_assembly: "Assembly / coordinates",
  dt_gene_type: "Gene type",
  ext_link: "Link",
  empty_pathways: "Not in this edition",
  empty_expression: "No expression data in this edition.",
  expr_aria: "Tissue expression bar chart",
  legend_median: "Median {unit}",
  legend_source: "Source: {source} · unit: {unit}",
  fig1_title: "Fig. 1 · Tissue expression",
  fig1_body:
    "Bars show median transcript level in selected tissues (unit: {unit}). Source: {source} local cache.",
  structure_empty_title: "Preview not in this edition",
  structure_empty_body:
    "No static preview in this edition. The link opens the predicted model in AlphaFold DB.",
  structure_empty_body_p35:
    "No static preview in this edition. The link opens the predicted model in AlphaFold DB.",
  open_alphafold: "Open in AlphaFold DB ↗",
  no_structure_link: "No structure link this edition",
  fig2_title: "Fig. 2 · Structure link",
  fig2_body:
    "Static thumbnail or AlphaFold link; 3D interaction is an enhancement and must not block first-screen reading.",
  chrom_ruler: "Chromosome ruler",
  section_chrom: "Chromosome ideogram",
  fig3_title: "Fig. 3 · Chromosomal locus (schematic)",
  fig3_body:
    "Schematic placement on {assembly} chr{chrom} ({start}–{end}); not to exact scale.",
  variants_strip_aria: "ClinVar P/LP counts",
  th_rsid: "rsID / ID",
  th_hgvs: "HGVS (protein)",
  th_sig: "ClinVar significance",
  th_note: "Note",
  variants_col_rsid: "rsID / ID",
  variants_col_hgvs: "HGVS (protein)",
  variants_col_sig: "ClinVar significance",
  variants_col_note: "Note",
  variants_empty: "No per-variant rows this edition",
  variants_details_empty: "No per-variant rows this edition",
  variants_details: "Show details",
  variants_summary:
    "Summary: ClinVar pathogenic {p} · likely pathogenic {lp} (P/LP total ≈ {total}, aligned with headline stats).",
  variants_only_counts:
    "This edition provides P/LP counts only; no per-locus rows.",
  variants_excerpt: "Table lists selected loci only, not a complete catalog.",
  variants_note_fallback: "Not a diagnostic conclusion",
  headline_aria: "Headline stats",
  as_of_prefix: "as_of",
  not_found_lead: "This gene is not in the current edition.",
  back_catalog: "Back to today's catalog",
  footer_print: "Print edition",
  gene_demo: "Demo gene this edition",
  lang_aria: "Language",
  label_location: "Genomic locus",
  label_clinvar_plp: "ClinVar pathogenic / likely pathogenic",
  label_top_tissue: "GTEx top tissue",
  aliases_label: "Aliases",
  edition_label: "edition",

  section_domains: "Protein domains",
  domains_empty: "Not in this edition",
  domains_aria: "Protein domain strip",
  domain_axis_n: "N",
  domain_axis_c: "C",
  fig_chrom_title: "Fig. 1 · Chromosome ideogram",
  fig_chrom_body:
    "Ink shades are G-bands on {assembly} chr{chrom} ({band}); the rust pin marks the gene midpoint {start}–{end}. Schematic, not a genome browser.",
  fig_expr_title: "Fig. 2 · Tissue expression",
  fig_expr_body:
    "Horizontal ranking bars by median TPM descending (at most 12; unit {unit}). Source: {source} local cache.",
  fig_domain_title: "Fig. 3 · Protein domains",
  fig_domain_body:
    "The strip runs N-terminus to C-terminus in amino-acid coordinates. Palette is ink, gray, and a single rust — see the legend.",
  fig_domain_empty_body: "No domains in this edition.",
  fig_struct_title: "Fig. 4 · Structure preview",
  fig_struct_body:
    "Static AlphaFold preview. When none is included, the empty state keeps the database link. 3D interaction must not block reading.",
  expr_multiples_aria: "Tissue expression small multiples",
  expr_bars_aria: "Tissue expression horizontal ranking bars",
  chrom_ideogram_aria: "{assembly} chr{chrom} ideogram, locus {band}",
  ideogram_schematic: "Schematic bands are used when no cytoband file is available.",
  legend_top: "highest",
  legend_other: "others",
  footer_style: "GenePage Gazette · Style C · P3.9",

  toc_label: "On this page",
  toc_lede: "Headlines",
  toc_cyto: "Genome",
  toc_expression: "Expression",
  toc_domains: "Protein",
  toc_structure: "Structure",
  toc_variants: "Variants",
  rail_aria: "Sidebar",
  rail_links: "Links & tools",
  rail_lang_hint: "Language: masthead zh | en",

  issue_toc_label: "In this issue",
  issue_toc_pieces: "PIECES",
  issue_hero_aria: "Cover story and issue contents",
  cover_kicker: "The cover story",
  pull_aria: "Pull quote",
  pull_by: "— Lede",
  pull_emphasis: "For research and teaching.",
  pull_fallback: "One printable research brief per gene.",
  toc_fig_lede: "Lead",
  toc_fig_cyto: "Fig. 1",
  toc_fig_expr: "Fig. 2",
  toc_fig_domain: "Fig. 3",
  toc_fig_struct: "Fig. 4",
  toc_fig_var: "Table",

};

const dictionaries: Record<Locale, Dict> = { zh, en };

export type DictKey = string;

export function isLocale(v: unknown): v is Locale {
  return v === "zh" || v === "en";
}

/** Resolve from a raw string (URL / localStorage). Invalid → zh. */
export function resolveLang(raw?: string | null): Locale {
  if (isLocale(raw)) return raw;
  return DEFAULT_LOCALE;
}

/** Server: query param wins when zh|en; else default zh. localStorage is client-only. */
export function resolveLocale(
  searchParams?: { lang?: string | string[] } | null
): Locale {
  const raw = searchParams?.lang;
  const v = Array.isArray(raw) ? raw[0] : raw;
  return resolveLang(v);
}

export function t(
  locale: Locale,
  key: string,
  vars?: Record<string, string | number>
): string {
  const table = dictionaries[locale] || dictionaries.zh;
  let s = table[key] ?? dictionaries.zh[key] ?? key;
  if (vars) {
    for (const [k, v] of Object.entries(vars)) {
      s = s.split(`{${k}}`).join(String(v));
    }
  }
  return s;
}

export function withLang(href: string, locale: Locale): string {
  const qIndex = href.indexOf("?");
  const path = qIndex >= 0 ? href.slice(0, qIndex) : href;
  const qs = qIndex >= 0 ? href.slice(qIndex + 1) : "";
  const params = new URLSearchParams(qs);
  params.set("lang", locale);
  const s = params.toString();
  return s ? `${path}?${s}` : path;
}

/**
 * Deck picker — edition 0.3.0-p35 ships deck_en for all demo genes.
 * Per docs/P35_I18N.md: en → deck_en || deck_zh (defensive); zh → deck_zh.
 */
export function pickDeck(
  gene: { deck_zh?: string; deck_en?: string } | null | undefined,
  locale: Locale
): string {
  if (!gene) return "";
  if (locale === "en") return (gene.deck_en || gene.deck_zh || "").trim();
  return (gene.deck_zh || "").trim();
}

/** tissue: lang==='en' ? name : (name_zh || name) */
export function pickTissueName(tissue: TissueExpr, locale: Locale): string {
  if (locale === "en") return tissue.name;
  return tissue.name_zh || tissue.name;
}

/**
 * Caption picker for expression/structure.
 * Prefer caption_en / caption_zh from gene JSON; dictionary body is fallback only.
 */
export function pickCaption(
  obj: { caption_zh?: string; caption_en?: string } | null | undefined,
  locale: Locale,
  fallback = ""
): string {
  if (!obj) return fallback;
  if (locale === "en") return obj.caption_en || fallback;
  return obj.caption_zh || fallback;
}

/** Call signature: headlineLabel(locale, stat) */
/** Accepts headlineLabel(locale, stat) or headlineLabel(stat, locale). */
export function headlineLabel(
  a: Locale | { key: string; label_zh: string },
  b: Locale | { key: string; label_zh: string }
): string {
  let locale: Locale;
  let stat: { key: string; label_zh: string };
  if (typeof a === "string") {
    locale = a;
    stat = b as { key: string; label_zh: string };
  } else {
    stat = a;
    locale = b as Locale;
  }
  const key = `label_${stat.key}`;
  const fromDict = dictionaries[locale]?.[key];
  if (fromDict) return fromDict;
  if (locale === "zh") return stat.label_zh;
  return dictionaries.en[key] || stat.label_zh;
}

export function disclaimerText(
  gene: Gene | null | undefined,
  locale: Locale
): string {
  if (locale === "zh") {
    return gene?.colophon?.disclaimer_zh || t("zh", "disclaimer");
  }
  return (
    (gene?.colophon as { disclaimer_en?: string } | undefined)?.disclaimer_en ||
    t("en", "disclaimer")
  );
}
