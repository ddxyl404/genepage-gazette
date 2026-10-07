/** Chromosome ideogram geometry. Bands come from the figures API; this file only normalizes them. */

export type NormBand = {
  id: string;
  start: number;
  end: number;
  stain: string;
};

export const CHROM_LEN: Record<string, number> = {
  "1": 248956422,
  "2": 242193529,
  "3": 198295559,
  "4": 190214555,
  "5": 181538259,
  "6": 170805979,
  "7": 159345973,
  "8": 145138636,
  "9": 138394717,
  "10": 133797422,
  "11": 135086622,
  "12": 133275309,
  "13": 114364328,
  "14": 107043718,
  "15": 101991189,
  "16": 90338345,
  "17": 83257441,
  "18": 80373285,
  "19": 58617616,
  "20": 64444167,
  "21": 46709983,
  "22": 50818468,
  X: 156040895,
  Y: 57227415,
  MT: 16569,
  M: 16569,
};

/** Approximate centromere fraction for the schematic (no cytoband file). */
const CEN_FRAC: Record<string, number> = {
  "1": 0.48,
  "2": 0.39,
  "3": 0.45,
  "4": 0.27,
  "5": 0.27,
  "6": 0.35,
  "7": 0.38,
  "8": 0.32,
  "9": 0.35,
  "10": 0.3,
  "11": 0.4,
  "12": 0.27,
  "13": 0.16,
  "14": 0.16,
  "15": 0.17,
  "16": 0.4,
  "17": 0.3,
  "18": 0.22,
  "19": 0.43,
  "20": 0.28,
  "21": 0.12,
  "22": 0.15,
  X: 0.38,
  Y: 0.22,
};

export function chromKey(raw: string | number | null | undefined): string {
  return String(raw ?? "")
    .trim()
    .replace(/^chr/i, "");
}

function num(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim() && Number.isFinite(Number(v))) return Number(v);
  return null;
}

export function parseCytobandPayload(raw: unknown): NormBand[] | null {
  if (!raw || typeof raw !== "object") return null;
  const obj = raw as Record<string, unknown>;
  const list = Array.isArray(raw)
    ? raw
    : Array.isArray(obj.bands)
      ? obj.bands
      : null;
  if (!list) return null;
  const bands: NormBand[] = [];
  for (const item of list) {
    if (!item || typeof item !== "object") continue;
    const b = item as Record<string, unknown>;
    const start = num(b.start ?? b.chromStart);
    const end = num(b.end ?? b.chromEnd);
    if (start == null || end == null || end <= start) continue;
    const stain = String(b.stain ?? b.gieStain ?? b.gie_stain ?? "gneg");
    const id = String(b.id ?? b.name ?? b.band ?? "");
    bands.push({ id, start, end, stain });
  }
  if (!bands.length) return null;
  bands.sort((a, b) => a.start - b.start || a.end - b.end);
  return bands;
}

export function schematicBands(key: string, chromLen: number): NormBand[] {
  const len = Math.max(1, chromLen);
  const cen = CEN_FRAC[key] ?? 0.4;
  const half = 0.012;
  const pEnd = Math.max(1, Math.floor(len * Math.max(0.02, cen - half)));
  const qStart = Math.min(len - 1, Math.floor(len * Math.min(0.98, cen + half)));
  const bands: NormBand[] = [];
  const pStain = ["gneg", "gpos50", "gpos100", "gpos25", "gneg"];
  const qStain = ["gneg", "gpos75", "gpos50", "gneg", "gpos100", "gpos25", "gneg"];
  const pN = pStain.length;
  for (let i = 0; i < pN; i++) {
    const a = Math.floor((pEnd * i) / pN);
    const b = i === pN - 1 ? pEnd : Math.floor((pEnd * (i + 1)) / pN);
    bands.push({
      id: `p${pN - i}`,
      start: a,
      end: Math.max(a + 1, b),
      stain: pStain[i],
    });
  }
  const mid = Math.floor(len * cen);
  bands.push({ id: "pcen", start: pEnd, end: Math.max(pEnd + 1, mid), stain: "acen" });
  bands.push({ id: "qcen", start: mid, end: Math.max(mid + 1, qStart), stain: "acen" });
  const qN = qStain.length;
  const qLen = len - qStart;
  for (let i = 0; i < qN; i++) {
    const a = qStart + Math.floor((qLen * i) / qN);
    const b = i === qN - 1 ? len : qStart + Math.floor((qLen * (i + 1)) / qN);
    bands.push({
      id: `q${i + 1}`,
      start: a,
      end: Math.max(a + 1, b),
      stain: qStain[i],
    });
  }
  return bands;
}

export function chromLength(key: string, bands: NormBand[], locusEnd: number): number {
  const table = CHROM_LEN[key] || 0;
  const bandEnd = bands.length ? bands[bands.length - 1].end : 0;
  return Math.max(table, bandEnd, locusEnd, 1);
}

export function bandAt(bands: NormBand[], bp: number): NormBand | null {
  for (const b of bands) {
    if (bp >= b.start && bp < b.end) return b;
  }
  if (bands.length && bp === bands[bands.length - 1].end) return bands[bands.length - 1];
  return null;
}

/** Ink-only G-stain. No hue rotation. */
export function stainFill(stain: string): string {
  const s = stain.toLowerCase();
  if (s.includes("100")) return "#1A1A1A";
  if (s.includes("75")) return "#3A3835";
  if (s.includes("50")) return "#6E6A64";
  if (s.includes("25")) return "#B7B1A6";
  if (s.includes("acen")) return "#F4F0E6";
  if (s.includes("stalk")) return "#C4BEB2";
  if (s.includes("gvar")) return "#4E4C48";
  return "#E4DDD0";
}

export function stainIsAcen(stain: string): boolean {
  return stain.toLowerCase().includes("acen");
}
