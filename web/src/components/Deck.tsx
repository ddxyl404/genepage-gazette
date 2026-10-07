import { type Locale, t } from "@/lib/i18n";

type Props = { text: string; locale?: Locale; lang?: Locale };

export function Deck({ text, locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";
  return (
    <section id="lede" className="deck reveal" aria-labelledby="deck-label">
      <span className="deck__label" id="deck-label">
        {t(L, "deck_label")}
      </span>
      <p>{text}</p>
    </section>
  );
}
