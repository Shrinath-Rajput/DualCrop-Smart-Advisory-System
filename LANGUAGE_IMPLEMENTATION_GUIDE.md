# Multi-Language Implementation Guide 🌍

## Overview
DualCrop Smart Advisory System now supports **3 languages**:
- 🇬🇧 **English** (en)
- 🇮🇳 **हिंदी (Hindi)** (hi)
- 🇮🇳 **मराठी (Marathi)** (mr)

---

## Features Implemented ✅

### 1. **Language Dropdown in Navbar**
- Added to all pages via the updated `base.html`
- Dropdown menu with flag emojis for easy identification
- Located in the top-right corner of the navigation bar
- Easy one-click language switching

### 2. **Dynamic Language Switching**
- **Global State Management**: Uses `localStorage` to persist language selection
- **Real-time Translation**: Applies translations immediately without page reload
- **Session Memory**: Language preference is saved and restored on next visit
- **Auto-load**: Remembers user's last selected language

### 3. **Complete Translation Support**
- **Navbar**: Home, Analyze, Weather, Dashboard, Chatbot, About links translated
- **All Pages**: Buttons, labels, placeholders translated
- **Chatbot**: Full multi-language responses
- **Date/Time Formatting**: Locale-aware formatting (English, Hindi, Marathi)
- **Messages**: Error messages, success notifications in all languages

### 4. **Chatbot Multi-Language Support**
- Chatbot responses in the selected language
- User's message analyzed and responded in the chosen language
- Seamless language switching during chat session
- Language parameter sent to backend API

### 5. **Client-Side Language Manager**
- **File**: `Backend/public/js/language-manager.js`
- Handles language initialization, switching, and translation application
- Automatic language detection on page load
- Event-based language change notifications

---

## How It Works 🔧

### Language Manager Flow
```
1. User visits the site
2. LanguageManager checks localStorage for saved language
3. If no language saved, defaults to English
4. Loads translations.json file
5. Applies translations to all elements with [data-i18n] attributes
6. User clicks language dropdown
7. changeLanguage(lang) function triggered
8. LanguageManager updates language and localStorage
9. Applies new translations instantly
```

### Translation Keys
All translatable content uses keys in the `translations.json` file:
```json
{
  "en": { "home": "Home", "analyze": "Analyze", ... },
  "hi": { "home": "होम", "analyze": "विश्लेषण करें", ... },
  "mr": { "home": "होम", "analyze": "विश्लेषण करा", ... }
}
```

---

## File Changes 📝

### Modified Files

1. **Backend/views/base.html**
   - Added language dropdown with 3 language options
   - Added language-manager.js script reference

2. **Backend/public/js/language-manager.js**
   - Enhanced with robust translation handling
   - Added event dispatching for language changes
   - Improved translation application logic

3. **Backend/public/js/main.js**
   - Added `changeLanguage()` function
   - Language-aware date/time formatting
   - Language change event listener

4. **Backend/views/chatbot.ejs**
   - Added language-manager.js script
   - Updated message submission to include language parameter
   - Multi-language error messages

5. **Backend/public/translations.json**
   - Expanded with all UI text in 3 languages
   - Complete translation coverage

### New Features

- **Language Switching Function**: `changeLanguage(lang, event)`
- **Event System**: `languageChanged` custom event
- **Translation Helper**: `languageManager.t(key)` method

---

## How to Use 👥

### For End Users

1. **Select Language**
   - Click the globe icon (🌐) in the top-right navbar
   - Select your preferred language:
     - 🇬🇧 English
     - 🇮🇳 हिंदी (Hindi)
     - 🇮🇳 मराठी (Marathi)

2. **Entire Interface Changes**
   - All menu items translate instantly
   - All page content updates
   - Chatbot responds in selected language

3. **Example Workflow**
   - Select **Marathi** → Navigate to Analyze page
   - Upload brinjal image → Get results in Marathi
   - Select **Hindi** → Go to Weather page
   - Enter city "Pune" → Get weather advice in Hindi
   - Go to Chatbot → Ask questions in Hindi → Responses in Hindi

---

## Developer Guide 👨‍💻

### Adding New Translations

1. **Identify the text** that needs translation
2. **Create a unique key** (e.g., `my_new_key`)
3. **Add to translations.json**:
```json
{
  "en": { "my_new_key": "English text" },
  "hi": { "my_new_key": "हिंदी पाठ" },
  "mr": { "my_new_key": "मराठी मजकूर" }
}
```

4. **Use in HTML** with data-i18n attribute:
```html
<button data-i18n="my_new_key">English text</button>
```

5. **Use in JavaScript**:
```javascript
if (languageManager) {
    const text = languageManager.t('my_new_key');
}
```

### Translation Best Practices

- Keep keys short and descriptive
- Use snake_case for key names
- Provide complete translations for all 3 languages
- Test translations in all languages
- Ensure cultural appropriateness

### Accessing Current Language

```javascript
const currentLang = languageManager.getCurrentLanguage();
// Returns: 'en', 'hi', or 'mr'
```

---

## Technical Architecture 🏗️

### Client-Side
```
base.html (Layout)
    ├── Navbar with Language Dropdown
    ├── Views (home, analyze, weather, etc.)
    └── Scripts
        ├── language-manager.js (Core translation engine)
        ├── main.js (UI utilities & language switching)
        └── page-specific scripts

translations.json (Translation data)
    ├── English (en)
    ├── Hindi (hi)
    └── Marathi (mr)
```

### Server-Side
```
server.js
    ├── /api/chat endpoint (accepts language parameter)
    ├── language-responses.js (Chatbot responses)
    └── Routes (render EJS with language support)
```

---

## Testing Checklist ✓

- [ ] Language dropdown visible in all pages
- [ ] Click each language option
- [ ] Verify navbar text changes
- [ ] Test in Analyze page - upload image, check language
- [ ] Test Weather page - check for language-specific formatting
- [ ] Test Chatbot - ask questions in each language
- [ ] Test Dashboard - verify all labels translate
- [ ] Test responsive design - check mobile navbar
- [ ] Verify localStorage - open DevTools > Application > localStorage
- [ ] Check language persistence - reload page, verify language stays same
- [ ] Test language switching during active session
- [ ] Verify date/time formatting in selected language

---

## Troubleshooting 🐛

### Language Not Changing
**Solution**: 
- Clear browser cache
- Check localStorage in DevTools
- Verify `language-manager.js` is loaded
- Check browser console for errors

### Translations Not Appearing
**Solution**:
- Ensure `data-i18n` attribute is set correctly
- Verify translation key exists in translations.json
- Check that `languageManager` is initialized
- Hard refresh the page (Ctrl+F5)

### Chatbot Responses in Wrong Language
**Solution**:
- Verify language parameter is sent to backend
- Check that language variable is set in chatbot.ejs
- Ensure `language-responses.js` has translations for that language
- Check backend console for errors

---

## Performance Optimization ⚡

- Translations cached in `languageManager.translations`
- Language switching doesn't require page reload
- localStorage used for instant language restoration
- Minimal DOM queries for translation application
- Event-based updates only when needed

---

## Future Enhancements 🚀

- [ ] Add language auto-detection based on browser settings
- [ ] Add more languages (Bengali, Gujarati, Kannada, etc.)
- [ ] Voice narration for accessibility
- [ ] Right-to-Left (RTL) language support
- [ ] Automated translation updates via API
- [ ] User language preference in backend database
- [ ] Language-specific date/number formatting
- [ ] Translation management dashboard

---

## Support & Feedback 💬

For issues or questions about the multi-language implementation:
1. Check the troubleshooting section above
2. Review the implementation guide files
3. Check browser console for error messages
4. Verify all required files are in place

---

## Quick Reference 📋

| Language | Code | Flag | Name |
|----------|------|------|------|
| English | `en` | 🇬🇧 | English |
| Hindi | `hi` | 🇮🇳 | हिंदी |
| Marathi | `mr` | 🇮🇳 | मराठी |

---

## Completion Status ✅

- ✅ Language dropdown in navbar
- ✅ Multi-language translation system
- ✅ Chatbot language support
- ✅ API integration with language parameter
- ✅ localStorage persistence
- ✅ Dynamic date/time formatting
- ✅ Language manager class
- ✅ Complete translation coverage

**Last Updated**: May 6, 2026
**Version**: 1.0.0
