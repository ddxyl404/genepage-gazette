"use client";

import { useCallback, useEffect } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  DEFAULT_LOCALE,
  LANG_STORAGE_KEY,
  isLocale,
  type Lang,
} from "@/lib/i18n";

type Props = {
  /** Server-resolved lang from ?lang= (via resolveLocale). */
  initialLang?: Lang;
  /** Alias used by some call sites. */
  locale?: Lang;
};

/**
 * Gazette masthead language toggle (visual shell).
 * State: URL ?lang= wins; else localStorage genepage_lang; default zh.
 * Uses eng i18n helpers only — do not reintroduce LanguageSwitcher.
 */
export function LangSwitch({ initialLang, locale }: Props) {
  const current: Lang = locale || initialLang || DEFAULT_LOCALE;
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const fromUrl = searchParams.get("lang");
    if (isLocale(fromUrl)) {
      try {
        localStorage.setItem(LANG_STORAGE_KEY, fromUrl);
      } catch {
        /* ignore */
      }
      return;
    }
    let stored: string | null = null;
    try {
      stored = localStorage.getItem(LANG_STORAGE_KEY);
    } catch {
      stored = null;
    }
    if (isLocale(stored)) {
      const params = new URLSearchParams(searchParams.toString());
      params.set("lang", stored);
      const qs = params.toString();
      router.replace(qs ? `${pathname}?${qs}` : pathname);
      return;
    }
    try {
      localStorage.setItem(LANG_STORAGE_KEY, DEFAULT_LOCALE);
    } catch {
      /* ignore */
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- hydrate preference once
  }, []);

  const setLang = useCallback(
    (next: Lang) => {
      try {
        localStorage.setItem(LANG_STORAGE_KEY, next);
      } catch {
        /* ignore */
      }
      const params = new URLSearchParams(searchParams.toString());
      params.set("lang", next);
      const qs = params.toString();
      router.push(qs ? `${pathname}?${qs}` : pathname);
      router.refresh();
    },
    [pathname, router, searchParams],
  );

  const btnClass = (active: boolean) =>
    active
      ? "lang-switch__btn lang-switch__btn--active is-active"
      : "lang-switch__btn";

  return (
    <div
      className="lang-switch no-print"
      role="group"
      aria-label={current === "en" ? "Language" : "语言"}
    >
      <button
        type="button"
        className={btnClass(current === "zh")}
        aria-pressed={current === "zh"}
        onClick={() => setLang("zh")}
      >
        zh
      </button>
      <span className="lang-switch__sep" aria-hidden="true">
        |
      </span>
      <button
        type="button"
        className={btnClass(current === "en")}
        aria-pressed={current === "en"}
        onClick={() => setLang("en")}
      >
        en
      </button>
    </div>
  );
}
