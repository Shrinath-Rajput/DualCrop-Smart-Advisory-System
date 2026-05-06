// Language-aware response generator for Chatbot

const languageResponses = {
    "en": {
        "hello": "👋 **Hello!** Welcome to DualCrop AI Assistant.\n\nI'm here to help you with:\n🍆 **Brinjal** - Growing, diseases, fertilizers\n🍇 **Grapes** - Cultivation, diseases, care\n\nWhat would you like to know today?",
        "help": "📖 **DualCrop AI Assistant Guide:**\n\n🍆 **Ask about Brinjal:**\n- How to grow brinjal?\n- What diseases affect brinjal?\n- What fertilizer for brinjal?\n- Why grow brinjal?\n- What is use of brinjal?\n\n🍇 **Ask about Grapes:**\n- How to cultivate grapes?\n- Tell me about grape diseases\n- What fertilizer for grapes?\n- Best time to plant grapes?\n- Why grow grapes?\n\n💡 **Other Topics:**\n- Weather advisory\n- Pest control methods\n- Irrigation techniques",
        "brinjal_why": "🍆 **Why Grow Brinjal?**\n\n✅ **Economic Benefits:**\n- High market demand & good prices\n- Multiple harvests per year (6-8 months)\n- Good profit margin (₹3-5 lakh per hectare)\n- Year-round availability\n- Quick returns on investment\n\n✅ **Nutritional Benefits:**\n- Rich in vitamins & minerals\n- Low calories (25 cal/100g)\n- High dietary fiber\n- Various health benefits",
        "brinjal_disease": "🍆 **Brinjal Common Diseases:**\n\n🔴 **Shoot and Fruit Borer** (Most Common)\n- Symptom: Holes in fruits & shoots\n- Medicine: Spinosad 45% SC (0.5 ml/L)\n- Spray: Every 7-10 days\n\n🔴 **Leaf Spot Disease**\n- Symptom: Brown spots on leaves\n- Medicine: Mancozeb 75% WP (2 gm/L)\n- Spray: Every 10-14 days\n\n💡 **Prevention:**\n- Use healthy seeds\n- Maintain field hygiene\n- Regular monitoring",
        "brinjal_grow": "🍆 **How to Grow Brinjal:**\n\n🌡️ **Optimal: 20-30°C**\n🌱 **Spacing: 60cm x 45cm**\n💧 **Summer: Daily irrigation**\n🛟 **Well-drained soil, pH: 5.5-7.5**\n⏱️ **Harvest: 70-90 days after transplanting**",
        "grapes_why": "🍇 **Why Grow Grapes?**\n\n✅ **Economic Benefits:**\n- Premium fruit with high value\n- Multiple uses: Fresh, Wine, Juice\n- Excellent export market\n- Sustained income for 30-40 years\n- Profit: ₹5-8 lakhs per hectare\n\n✅ **Health Benefits:**\n- Rich in antioxidants\n- Contains resveratrol (heart health)\n- Good source of vitamins",
        "grapes_disease": "🍇 **Grape Diseases:**\n\n🔴 **Black Rot** (Most Serious)\n- Symptoms: Dark spots on berries\n- Medicine: Bordeaux Mixture 1%\n- Spray: Every 7-10 days\n\n🔴 **Leaf Blight**\n- Symptoms: Brown spots with yellow halo\n- Medicine: Chlorothalonil 75% WP\n- Spray: Every 10-14 days",
        "grapes_grow": "🍇 **How to Cultivate Grapes:**\n\n🌡️ **Optimal: 10-30°C**\n🌱 **Spacing: 2m x 2m**\n💧 **Drip irrigation: 50-60 L/plant/day**\n🛟 **Well-drained soil, pH: 6.5-7.5**\n⏱️ **Full production: 5-7 years**",
        "default": "🤔 I'm not sure about that. Please ask about:\n\n🍆 **Brinjal:** growing, diseases, fertilizer\n🍇 **Grapes:** cultivation, diseases, care\n\nOr type 'Help' for more options!"
    },
    "hi": {
        "hello": "👋 **नमस्ते!** डुअलक्रॉप एआई सहायक में आपका स्वागत है।\n\nमैं आपको यहाँ मदद करने के लिए हूँ:\n🍆 **बैंगन** - उगाना, रोग, खाद\n🍇 **अंगूर** - खेती, रोग, देखभाल\n\nआप क्या जानना चाहते हैं?",
        "help": "📖 **डुअलक्रॉप एआई सहायक मार्गदर्शन:**\n\n🍆 **बैंगन के बारे में पूछें:**\n- बैंगन कैसे उगाएं?\n- बैंगन की बीमारियां क्या हैं?\n- बैंगन के लिए खाद क्या है?\n- बैंगन क्यों उगाएं?\n\n🍇 **अंगूर के बारे में पूछें:**\n- अंगूर की खेती कैसे करें?\n- अंगूर की बीमारियों के बारे में बताएं\n- अंगूर के लिए खाद क्या है?\n- अंगूर कब लगाएं?\n\n💡 **अन्य विषय:**\n- मौसम सलाह\n- कीट नियंत्रण\n- सिंचाई तकनीकें",
        "brinjal_why": "🍆 **बैंगन क्यों उगाएं?**\n\n✅ **आर्थिक लाभ:**\n- उच्च बाजार मांग\n- साल में 6-8 महीने उपज\n- अच्छा लाभ (₹3-5 लाख प्रति हेक्टेयर)\n- पूरे साल उपलब्ध\n- जल्दी रिटर्न\n\n✅ **पोषण लाभ:**\n- विटामिन और खनिज से भरपूर\n- कम कैलोरी\n- उच्च फाइबर",
        "brinjal_disease": "🍆 **बैंगन की आम बीमारियां:**\n\n🔴 **शूट और फल बेधक** (सबसे आम)\n- लक्षण: फलों में छेद\n- दवा: स्पिनोसाड 0.5 मिली/लीटर\n- छिड़काव: हर 7-10 दिन\n\n🔴 **पत्ती धब्बा**\n- लक्षण: भूरे धब्बे\n- दवा: मेनकोजेब 2 ग्राम/लीटर\n- छिड़काव: हर 10-14 दिन",
        "brinjal_grow": "🍆 **बैंगन कैसे उगाएं:**\n\n🌡️ **तापमान: 20-30°C**\n🌱 **दूरी: 60cm x 45cm**\n💧 **गर्मी में: रोज सिंचाई**\n🛟 **अच्छी जल निकासी, पीएच: 5.5-7.5**\n⏱️ **कटाई: 70-90 दिन बाद**",
        "grapes_why": "🍇 **अंगूर क्यों उगाएं?**\n\n✅ **आर्थिक लाभ:**\n- प्रीमियम फल\n- कई उपयोग: ताजा, शराब, रस\n- निर्यात बाजार\n- 30-40 साल आय\n- लाभ: ₹5-8 लाख प्रति हेक्टेयर\n\n✅ **स्वास्थ्य लाभ:**\n- एंटीऑक्सिडेंट\n- दिल के लिए अच्छा",
        "grapes_disease": "🍇 **अंगूर की बीमारियां:**\n\n🔴 **काला सड़न** (सबसे गंभीर)\n- लक्षण: बेरीज पर काले धब्बे\n- दवा: बोर्डो मिश्रण 1%\n- छिड़काव: हर 7-10 दिन\n\n🔴 **पत्ती झुलसा**\n- लक्षण: पीले हालो के साथ भूरे धब्बे\n- दवा: क्लोरोथालोनिल\n- छिड़काव: हर 10-14 दिन",
        "grapes_grow": "🍇 **अंगूर की खेती:**\n\n🌡️ **तापमान: 10-30°C**\n🌱 **दूरी: 2m x 2m**\n💧 **ड्रिप सिंचाई: 50-60 लीटर/पौधा/दिन**\n🛟 **अच्छी जल निकासी**\n⏱️ **पूरी उपज: 5-7 साल**",
        "default": "🤔 मुझे समझ नहीं आया। कृपया पूछें:\n\n🍆 **बैंगन:** उगाना, रोग, खाद\n🍇 **अंगूर:** खेती, रोग, देखभाल\n\nया 'मदद' के लिए टाइप करें!"
    },
    "mr": {
        "hello": "👋 **नमस्ते!** डुअलक्रॉप एआय सहायकांमध्ये आपले स्वागत आहे।\n\nमैं आपल्याला येथे मदत करण्यासाठी आहे:\n🍆 **वारी** - उगवणे, रोग, खत\n🍇 **द्राक्षे** - शेती, रोग, काळजी\n\nआपण काय जाणू शकता?",
        "help": "📖 **डुअलक्रॉप एआय मार्गदर्शन:**\n\n🍆 **वारीबद्दल विचारा:**\n- वारी कशी उगवायची?\n- वारीची रोगे कोणत्या आहेत?\n- वारीसाठी खत काय आहे?\n- वारी का उगवायची?\n\n🍇 **द्राक्षेबद्दल विचारा:**\n- द्राक्षे शेती कशी करायची?\n- द्राक्षांच्या रोगांबद्दल सांगा\n- द्राक्षांसाठी खत काय?\n- द्राक्षे कधी लावायचे?\n\n💡 **इतर विषय:**\n- हवामान सल्ला\n- कीटक नियंत्रण\n- सिंचन तंत्र",
        "brinjal_why": "🍆 **वारी का उगवायची?**\n\n✅ **आर्थिक लाभ:**\n- उच्च बाजार मागणी\n- 6-8 महिने उत्पादन\n- चांगला नफा (₹3-5 लाख प्रति हेक्टेयर)\n- वर्षभर उपलब्ध\n- जलद रिटर्न\n\n✅ **पोषण लाभ:**\n- व्हिटामिन आणि खनिजाने समृद्ध\n- कमी कॅलोरी\n- उच्च फायबर",
        "brinjal_disease": "🍆 **वारीची सामान्य रोगे:**\n\n🔴 **शूट आणि फळ बोरर**\n- लक्षण: फळांमध्ये छिद्र\n- दवा: स्पिनोसॅड 0.5 मिली/लीटर\n- फवारणी: 7-10 दिने\n\n🔴 **पात डाग**\n- लक्षण: तपकिरी डाग\n- दवा: मेनकोजेब 2 ग्रॅम/लीटर\n- फवारणी: 10-14 दिने",
        "brinjal_grow": "🍆 **वारी कशी उगवायची:**\n\n🌡️ **तापमान: 20-30°C**\n🌱 **अंतर: 60cm x 45cm**\n💧 **उन्हाळ्यात: दररोज पाणी**\n🛟 **चांगली ड्रेनेज**\n⏱️ **कापणी: 70-90 दिन**",
        "grapes_why": "🍇 **द्राक्षे का उगवायचे?**\n\n✅ **आर्थिक लाभ:**\n- प्रीमियम फळ\n- विविध उपयोग\n- निर्यात बाजार\n- 30-40 साल उत्पादन\n- नफा: ₹5-8 लाख प्रति हेक्टेयर\n\n✅ **स्वास्थ्य लाभ:**\n- अँटिऑक्सिडेंट्स\n- हृदयासाठी चांगले",
        "grapes_disease": "🍇 **द्राक्षांची रोगे:**\n\n🔴 **काळा सड** (सर्वात गंभीर)\n- लक्षण: बेरीवर काळे डाग\n- दवा: बोर्डो मिश्रण 1%\n- फवारणी: 7-10 दिने\n\n🔴 **पात झुलसा**\n- लक्षण: पीळ हॅलो सह तपकिरी डाग\n- दवा: क्लोरोथालोनिल\n- फवारणी: 10-14 दिने",
        "grapes_grow": "🍇 **द्राक्षे शेती:**\n\n🌡️ **तापमान: 10-30°C**\n🌱 **अंतर: 2m x 2m**\n💧 **ड्रिप सिंचन: 50-60 लीटर/वनस्पती/दिवस**\n🛟 **चांगली ड्रेनेज**\n⏱️ **पूर्ण उत्पादन: 5-7 साल**",
        "default": "🤔 मला समजत नाही। कृपया विचारा:\n\n🍆 **वारी:** उगवणे, रोग, खत\n🍇 **द्राक्षे:** शेती, रोग, काळजी\n\nअथवा 'मदत' टाइप करा!"
    }
};

function getSmartChatbotResponseInLanguage(message, language = 'en') {
    const lowerMessage = message.toLowerCase().trim();
    const responses = languageResponses[language] || languageResponses['en'];

    // Detect keywords
    const isHello = ['hello', 'hi', 'hey', 'greetings', 'namaste', 'नमस्ते', 'हेलो', 'नमस्कार'].some(k => lowerMessage.includes(k));
    const isHelp = ['help', 'guide', 'tutorial', 'मदद', 'गाइड', 'सहायता'].some(k => lowerMessage.includes(k));
    
    const isBrinjal = ['brinjal', 'binjal', 'eggplant', 'बैंगन', 'वारी', 'ईगप्लांट'].some(k => lowerMessage.includes(k));
    const isGrape = ['grape', 'grapes', 'wine', 'vineyard', 'अंगूर', 'द्राक्षे', 'वाइन'].some(k => lowerMessage.includes(k));
    
    const isWhy = ['why', 'importance', 'benefit', 'क्यों', 'महत्व', 'क्या', 'का'].some(k => lowerMessage.includes(k));
    const isDisease = ['disease', 'pest', 'rot', 'blight', 'रोग', 'कीट', 'सड़', 'झुलसा'].some(k => lowerMessage.includes(k));
    const isGrow = ['how', 'grow', 'cultivate', 'plant', 'कैसे', 'उगाना', 'उगवणे', 'लावणे'].some(k => lowerMessage.includes(k));

    // Return language-specific responses
    if (isHello) return responses.hello;
    if (isHelp) return responses.help;
    
    if (isBrinjal) {
        if (isWhy) return responses.brinjal_why;
        if (isDisease) return responses.brinjal_disease;
        if (isGrow) return responses.brinjal_grow;
        return responses.brinjal_why; // Default brinjal response
    }
    
    if (isGrape) {
        if (isWhy) return responses.grapes_why;
        if (isDisease) return responses.grapes_disease;
        if (isGrow) return responses.grapes_grow;
        return responses.grapes_why; // Default grapes response
    }
    
    return responses.default;
}

module.exports = { getSmartChatbotResponseInLanguage, languageResponses };
