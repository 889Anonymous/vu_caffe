import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import vi from './locales/vi.json';

i18n
    .use(LanguageDetector)      // auto-detect from browser / localStorage
    .use(initReactI18next)
    .init({
        resources: {
            en: { translation: en },
            vi: { translation: vi },
        },
        fallbackLng: 'vi',          // default to Vietnamese for this fork
        lng: localStorage.getItem('pos_language') || 'vi',
        debug: false,
        interpolation: {
            escapeValue: false,       // React already escapes by default
        },
        detection: {
            // Lookup order: localStorage → navigator.language
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
            lookupLocalStorage: 'pos_language',
        },
    });

export default i18n;
