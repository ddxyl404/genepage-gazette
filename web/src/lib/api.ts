import type { CatalogIndex, Gene, SearchResult } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  (typeof window === "undefined" ? "http://127.0.0.1:8000" : "");

function apiUrl(path: string): string {
  if (API_BASE) return `${API_BASE}${path}`;
  return path;
}

export async function fetchGene(idOrSymbol: string): Promise<Gene | null> {
  const res = await fetch(apiUrl(`/api/gene/${encodeURIComponent(idOrSymbol)}`), {
    next: { revalidate: 60 },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`gene fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchIndex(): Promise<CatalogIndex> {
  const res = await fetch(apiUrl("/api/index"), { next: { revalidate: 60 } });
  if (!res.ok) {
    // fallback: empty search listing
    const search = await fetchSearch("");
    return {
      edition: "0.1.0-preview",
      data_as_of: "2026-09-29",
      count: search.length,
      genes: search.map((r) => ({
        symbol: r.symbol,
        id: r.id,
        file: r.file || `genes/${r.symbol}.json`,
      })),
    };
  }
  return res.json();
}

export async function fetchSearch(q: string): Promise<SearchResult[]> {
  const res = await fetch(
    apiUrl(`/api/search?q=${encodeURIComponent(q)}`),
    { next: { revalidate: 30 } }
  );
  if (!res.ok) throw new Error(`search failed: ${res.status}`);
  const body = await res.json();
  return body.results || [];
}

/** Cytoband JSON from GET /api/figures/cytobands/{chrom}. Missing file → null (schematic). */
export async function fetchCytobandFigure(chrom: string): Promise<unknown | null> {
  const key = String(chrom || "").trim();
  if (!key) return null;
  try {
    const res = await fetch(
      apiUrl(`/api/figures/cytobands/${encodeURIComponent(key)}`),
      { next: { revalidate: 60 } },
    );
    if (!res.ok) return null;
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("svg")) return null;
    return await res.json();
  } catch {
    return null;
  }
}
