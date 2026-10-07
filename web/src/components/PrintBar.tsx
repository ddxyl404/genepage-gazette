"use client";

import { type Locale, t } from "@/lib/i18n";

type Props = { locale?: Locale; lang?: Locale };

export function PrintBar({ locale, lang }: Props) {
  const L: Locale = locale || lang || "zh";
  return (
    <div
      className="print-bar no-print"
      role="region"
      aria-label={t(L, "print_aria")}
    >
      <button
        type="button"
        className="print-bar__btn"
        onClick={() => window.print()}
      >
        {t(L, "print_btn")}
      </button>
      <span className="print-bar__hint">{t(L, "print_hint")}</span>
    </div>
  );
}
