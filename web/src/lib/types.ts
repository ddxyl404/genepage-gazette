export type HeadlineStat = {
  key: string;
  label_zh: string;
  value: string | number | null;
  as_of?: string;
  /** Full English / long form; short form stays in value */
  detail?: string;
};

export type Pathway = {
  name: string;
  url: string;
  source?: string;
};

export type TissueExpr = {
  name: string;
  value: number;
  name_zh?: string;
};

export type VariantRow = {
  rsid?: string | null;
  hgvs_p?: string | null;
  significance?: string | null;
  note_zh?: string | null;
  note_en?: string | null;
};

export type CytoBand = {
  id?: string;
  name?: string;
  start: number;
  end: number;
  stain?: string;
  gieStain?: string;
};

/** Gene-level locus note. Full G-bands live in /api/figures/cytobands/{chrom}. */
export type CytobandMeta = {
  chrom?: string;
  start?: number;
  end?: number;
  assembly?: string;
  band_label?: string;
  figure_id?: string;
  length?: number;
  bands?: CytoBand[];
  caption_zh?: string;
  caption_en?: string;
};

export type ProteinDomain = {
  id?: string;
  name: string;
  name_zh?: string;
  start: number;
  end: number;
  source?: string;
  url?: string;
};

export type Gene = {
  id: string;
  symbol: string;
  aliases: string[];
  type: string;
  location: {
    chrom: string;
    start: number;
    end: number;
    assembly: string;
  };
  deck_zh: string;
  deck_en?: string;
  headline_stats: HeadlineStat[];
  pathways: Pathway[];
  expression: {
    source: string;
    unit: string;
    tissues: TissueExpr[];
    caption_zh?: string;
    caption_en?: string;
  };
  structure: {
    alphafold_url: string | null;
    /**
     * AlphaFold static preview URL or null.
     * Prefer API convention: `/api/figures/alphafold/{SYMBOL}`
     * (may also be a relative cache path until data rewrites).
     */
    preview_image: string | null;
    caption_zh?: string;
    caption_en?: string;
  };
  variants_summary: {
    clinvar_pathogenic: number;
    clinvar_likely_pathogenic: number;
    note_zh: string;
    note_en?: string;
    rows?: VariantRow[];
  };
  colophon: {
    data_as_of: string;
    edition: string;
    disclaimer_zh: string;
    disclaimer_en?: string;
  };
  sources: Array<{
    name: string;
    url: string;
    version?: string;
    confidence?: string;
  }>;
  confidence?: Record<string, string>;
  /** Optional. Bands themselves are fetched, not inlined. */
  cytoband?: CytobandMeta | null;
  /** Empty or omitted → domain-strip empty state. */
  domains?: ProteinDomain[] | null;
};

export type IndexEntry = {
  symbol: string;
  id: string;
  file: string;
};

export type CatalogIndex = {
  edition: string;
  data_as_of: string;
  count: number;
  genes: IndexEntry[];
};

export type SearchResult = {
  symbol: string;
  id: string;
  aliases?: string[];
  location?: string | null;
  type?: string;
  deck_zh?: string;
  deck_en?: string;
  file?: string;
};
