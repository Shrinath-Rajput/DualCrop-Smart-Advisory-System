// Language Manager - Handles all language switching
class LanguageManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.translations = {};
        this.initLanguage();
    }

    // Initialize language
    async initLanguage() {
        try {
            const response = await fetch('/translations.json');
            this.translations = await response.json();
            this.setLanguage(this.currentLanguage);
            document.documentElement.lang = this.currentLanguage;
        } catch (error) {
            console.error('Error loading translations:', error);
        }
    }

    // Set language
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLanguage = lang;
            localStorage.setItem('language', lang);
            document.documentElement.lang = lang;
            this.applyTranslations();
            // Trigger custom event for language change
            window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
            return true;
        }
        return false;
    }

    // Get translation
    t(key) {
        const lang = this.currentLanguage;
        return this.translations[lang]?.[key] || this.translations['en']?.[key] || key;
    }

    // Apply translations to page
    applyTranslations() {
        // Translate text content
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.dataset.i18n;
            if (element.tagName === 'A' || element.tagName === 'BUTTON') {
                // For links and buttons, translate only the text content, not the span inside
                const span = element.querySelector('span[data-i18n]');
                if (span) {
                    span.textContent = this.t(key);
                }
            } else {
                element.textContent = this.t(key);
            }
        });

        // Translate placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.dataset.i18nPlaceholder;
            element.placeholder = this.t(key);
        });

        // Translate aria-labels
        document.querySelectorAll('[data-i18n-aria]').forEach(element => {
            const key = element.dataset.i18nAria;
            element.setAttribute('aria-label', this.t(key));
        });
    }

    // Get current language
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // Get all translations for a language
    getLanguageStrings() {
        return this.translations[this.currentLanguage] || this.translations['en'];
    }
}

// Initialize on page load
let languageManager;
document.addEventListener('DOMContentLoaded', () => {
    languageManager = new LanguageManager();
});

