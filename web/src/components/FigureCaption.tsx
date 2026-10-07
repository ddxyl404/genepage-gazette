import { t, type Locale } from "@/lib/i18n";

type Props = {
  dataCaption?: string;
  /** Layout figure number, used when the data caption leaves the slot blank (「图 ·」 / 「Fig. ·」). */
  figureNo?: number;
  titleKey: string;
  bodyFallback: string;
  locale: Locale;
};

/**
 * Prefer caption_zh|en. Data in 0.3.1-p36 writes 「图 · …」 / 「Fig. · …」
 * without a number so the page can stamp the layout order.
 * A caption that already carries a digit is left untouched.
 */
export function FigureCaption({
  dataCaption,
  figureNo,
  titleKey,
  bodyFallback,
  locale,
}: Props) {
  const raw = (dataCaption || "").trim();
  if (raw) {
    const zh = raw.match(/^图\s*(\d+)?\s*[·•]\s*([\s\S]+)$/);
    const en = raw.match(/^Fig\.?\s*(\d+)?\s*[·•]\s*([\s\S]+)$/i);
    const hit = zh || en;
    if (hit) {
      const given = (hit[1] || "").trim();
      const num = given || (figureNo != null ? String(figureNo) : "");
      const label = zh
        ? num
          ? `图 ${num}`
          : "图"
        : num
          ? `Fig. ${num}`
          : "Fig.";
      return (
        <p className="figure-caption">
          <strong>{`${label} ·`}</strong>
          {hit[2].trim()}
        </p>
      );
    }
    return (
      <p className="figure-caption">
        <strong>{raw}</strong>
      </p>
    );
  }
  return (
    <p className="figure-caption">
      <strong>{t(locale, titleKey)}</strong>
      {bodyFallback}
    </p>
  );
}
