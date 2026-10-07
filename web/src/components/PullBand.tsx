import { t, type Locale } from "@/lib/i18n";

type Props = {
  deck: string;
  lang: Locale;
};

/** First sentence of deck as pull quote; trailing clause in rust italic when splittable. */
function splitQuote(deck: string, lang: Locale): { lead: string; rust: string } {
  const text = (deck || "").trim();
  if (!text) {
    return { lead: t(lang, "pull_fallback"), rust: "" };
  }
  // Prefer first sentence
  let sentence = text;
  if (lang === "zh") {
    const m = text.match(/^[^。！？]+[。！？]?/);
    if (m) sentence = m[0];
  } else {
    const m = text.match(/^[^.!?]+[.!?]?/);
    if (m) sentence = m[0].trim();
  }

  // Split on last comma / Chinese顿号/comma for rust emphasis on tail
  if (lang === "zh") {
    const idx = Math.max(sentence.lastIndexOf("，"), sentence.lastIndexOf("、"));
    if (idx > 8 && idx < sentence.length - 4) {
      return {
        lead: sentence.slice(0, idx + 1),
        rust: sentence.slice(idx + 1).trim(),
      };
    }
  } else {
    const idx = sentence.lastIndexOf(",");
    if (idx > 12 && idx < sentence.length - 6) {
      return {
        lead: sentence.slice(0, idx + 1),
        rust: sentence.slice(idx + 1).trim(),
      };
    }
  }
  return { lead: sentence, rust: t(lang, "pull_emphasis") };
}

export function PullBand({ deck, lang }: Props) {
  const { lead, rust } = splitQuote(deck, lang);
  return (
    <aside className="pull-band reveal" aria-label={t(lang, "pull_aria")}>
      <span className="pull-band__marks" aria-hidden="true">
        “
      </span>
      <p className="pull-band__quote">
        {lead}
        {rust ? (
          <>
            {" "}
            <em className="pull-band__rust">{rust}</em>
          </>
        ) : null}
      </p>
      <p className="pull-band__by">{t(lang, "pull_by")}</p>
    </aside>
  );
}
