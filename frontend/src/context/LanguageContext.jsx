import { createContext, useContext, useEffect, useMemo, useState } from "react";

// Lightweight i18n for the existing pages. React components can use t(key),
// while the DOM bridge translates legacy literal labels. The bridge deliberately
// observes only React child-list changes and disconnects while translating so it
// can never observe its own text mutations (the previous implementation caused
// an infinite MutationObserver loop and froze the browser).
const dictionaries = {
  en: {language:"Language",home:"Home",how:"How it works",schemes:"Explore schemes",about:"About",faq:"FAQ",dashboard:"Dashboard",profile:"Profile",eligibility:"Eligibility",recommendations:"Recommendations",applications:"Applications",saved:"Saved schemes",compare:"Compare",assistant:"AI Assistant",notifications:"Notifications",settings:"Settings",signin:"Sign in",signout:"Sign out",getstarted:"Get started",find:"Find My Schemes",search:"Search",state:"State",field:"Field / Purpose",selectState:"Select State",selectField:"Select Field",view:"View scheme →",back:"Back to schemes",official:"Official application ↗",why:"Why this scheme?",benefits:"What the scheme provides",documents:"Documents required",apply:"How to apply",finance:"Financial Planner",nearby:"Find help near you",location:"Use my location",ask:"Ask Scheme Sahayak AI",welcome:"Hello! I’m Scheme Sahayak AI. I can help you discover schemes, understand eligibility, compare benefits, and plan your application.",placeholder:"Ask a question…",thinking:"Thinking through your question…",disclaimer:"AI guidance is informational. Confirm final eligibility and terms with the official scheme authority.",exploreTitle:"Explore Government Schemes",searchPlaceholder:"Search by scheme name, purpose, benefit or keyword…",noSchemes:"No schemes found",tryAgain:"Try again",education:"Education",agriculture:"Agriculture",business:"Business & Entrepreneurship",employment:"Employment",housing:"Housing",health:"Healthcare",women:"Women & Child Welfare",social:"Social Welfare",financeAid:"Financial Assistance",skill:"Skill Development",scholarship:"Scholarship",msme:"MSME",animal:"Animal Husbandry",fisheries:"Fisheries",rural:"Rural Development",allStates:"All States",allFields:"All Fields",nearbyTitle:"Find help near you",useLocation:"Use my location",locating:"Finding your location…",noPartners:"No verified partners found near you for this scheme.",locationDenied:"Location permission was denied. You can enable it in your browser settings.",locationUnavailable:"Your location could not be determined.",settingsHint:"Choose the language for the interface."},
  hi: {language:"भाषा",home:"होम",how:"यह कैसे काम करता है",schemes:"योजनाएँ खोजें",about:"हमारे बारे में",faq:"सामान्य प्रश्न",dashboard:"डैशबोर्ड",profile:"प्रोफ़ाइल",eligibility:"पात्रता",recommendations:"सिफारिशें",applications:"आवेदन",saved:"सहेजी गई योजनाएँ",compare:"तुलना",assistant:"AI सहायक",notifications:"सूचनाएँ",settings:"सेटिंग्स",signin:"साइन इन",signout:"साइन आउट",getstarted:"शुरू करें",find:"मेरी योजनाएँ खोजें",search:"खोजें",state:"राज्य",field:"क्षेत्र / उद्देश्य",selectState:"राज्य चुनें",selectField:"क्षेत्र चुनें",view:"योजना देखें →",back:"योजनाओं पर वापस जाएँ",official:"आधिकारिक आवेदन ↗",why:"यह योजना आपके लिए क्यों?",benefits:"योजना के लाभ",documents:"आवश्यक दस्तावेज़",apply:"आवेदन कैसे करें",finance:"वित्तीय योजनाकार",nearby:"पास में सहायता खोजें",location:"मेरी लोकेशन उपयोग करें",ask:"Scheme Sahayak AI से पूछें",welcome:"नमस्ते! मैं Scheme Sahayak AI हूँ। मैं सरकारी योजनाएँ खोजने, पात्रता समझने, तुलना करने और आवेदन की योजना बनाने में मदद कर सकता हूँ।",placeholder:"अपना प्रश्न पूछें…",thinking:"आपके प्रश्न का विश्लेषण कर रहा हूँ…",disclaimer:"AI मार्गदर्शन केवल जानकारी के लिए है। अंतिम पात्रता और शर्तों की पुष्टि आधिकारिक प्राधिकरण से करें।",exploreTitle:"सरकारी योजनाएँ खोजें",searchPlaceholder:"योजना का नाम, उद्देश्य, लाभ या कीवर्ड खोजें…",noSchemes:"कोई योजना नहीं मिली",tryAgain:"फिर कोशिश करें",education:"शिक्षा",agriculture:"कृषि",business:"व्यवसाय और उद्यमिता",employment:"रोजगार",housing:"आवास",health:"स्वास्थ्य",women:"महिला एवं बाल कल्याण",social:"सामाजिक कल्याण",financeAid:"वित्तीय सहायता",skill:"कौशल विकास",scholarship:"छात्रवृत्ति",msme:"MSME",animal:"पशुपालन",fisheries:"मत्स्य पालन",rural:"ग्रामीण विकास",allStates:"सभी राज्य",allFields:"सभी क्षेत्र",nearbyTitle:"अपने पास सहायता खोजें",useLocation:"मेरी लोकेशन उपयोग करें",locating:"आपकी लोकेशन खोजी जा रही है…",noPartners:"इस योजना के लिए आपके पास कोई सत्यापित पार्टनर नहीं मिला।",locationDenied:"लोकेशन की अनुमति नहीं मिली। ब्राउज़र सेटिंग्स में इसे सक्षम करें।",locationUnavailable:"आपकी लोकेशन निर्धारित नहीं की जा सकी।",settingsHint:"इंटरफ़ेस की भाषा चुनें।"},
  ta: {language:"மொழி",home:"முகப்பு",how:"எப்படி செயல்படுகிறது",schemes:"திட்டங்களை ஆராய்க",about:"எங்களை பற்றி",faq:"அடிக்கடி கேட்கப்படும் கேள்விகள்",dashboard:"டாஷ்போர்டு",profile:"சுயவிவரம்",eligibility:"தகுதி",recommendations:"பரிந்துரைகள்",applications:"விண்ணப்பங்கள்",saved:"சேமித்த திட்டங்கள்",compare:"ஒப்பிடுக",assistant:"AI உதவியாளர்",notifications:"அறிவிப்புகள்",settings:"அமைப்புகள்",signin:"உள்நுழை",signout:"வெளியேறு",getstarted:"தொடங்குங்கள்",find:"எனக்கான திட்டங்களை கண்டறி",search:"தேடு",state:"மாநிலம்",field:"துறை / நோக்கம்",selectState:"மாநிலத்தை தேர்ந்தெடுக்கவும்",selectField:"துறையை தேர்ந்தெடுக்கவும்",view:"திட்டத்தை காண்க →",back:"திட்டங்களுக்கு திரும்பு",official:"அதிகாரப்பூர்வ விண்ணப்பம் ↗",why:"இந்த திட்டம் ஏன்?",benefits:"திட்டத்தின் நன்மைகள்",documents:"தேவையான ஆவணங்கள்",apply:"எப்படி விண்ணப்பிப்பது",finance:"நிதி திட்டமிடுபவர்",nearby:"அருகிலுள்ள உதவியை கண்டறிக",location:"என் இருப்பிடத்தைப் பயன்படுத்து",ask:"Scheme Sahayak AI-யிடம் கேளுங்கள்",welcome:"வணக்கம்! நான் Scheme Sahayak AI. அரசு திட்டங்களை கண்டறியவும், தகுதியை புரிந்துகொள்ளவும், ஒப்பிடவும், விண்ணப்பத்தை திட்டமிடவும் உதவுகிறேன்.",placeholder:"உங்கள் கேள்வியை கேளுங்கள்…",thinking:"உங்கள் கேள்வியை பரிசீலிக்கிறேன்…",disclaimer:"AI வழிகாட்டுதல் தகவலுக்காக மட்டுமே. இறுதி தகுதி மற்றும் விதிமுறைகளை அதிகாரப்பூர்வ அமைப்பிடம் உறுதி செய்யுங்கள்.",exploreTitle:"அரசுத் திட்டங்களை ஆராய்க",searchPlaceholder:"திட்டப் பெயர், நோக்கம், நன்மை அல்லது முக்கிய சொல்லை தேடுங்கள்…",noSchemes:"திட்டங்கள் கிடைக்கவில்லை",tryAgain:"மீண்டும் முயற்சிக்கவும்",education:"கல்வி",agriculture:"விவசாயம்",business:"வணிகம் மற்றும் தொழில்முனைவு",employment:"வேலைவாய்ப்பு",housing:"வீட்டுவசதி",health:"சுகாதாரம்",women:"பெண்கள் மற்றும் குழந்தைகள் நலன்",social:"சமூக நலன்",financeAid:"நிதி உதவி",skill:"திறன் மேம்பாடு",scholarship:"உதவித்தொகை",msme:"MSME",animal:"கால்நடை வளர்ப்பு",fisheries:"மீன்வளம்",rural:"ஊரக வளர்ச்சி",allStates:"அனைத்து மாநிலங்கள்",allFields:"அனைத்து துறைகள்",nearbyTitle:"உங்களுக்கு அருகில் உதவி",useLocation:"என் இருப்பிடத்தைப் பயன்படுத்து",locating:"உங்கள் இருப்பிடம் கண்டறியப்படுகிறது…",noPartners:"இந்தத் திட்டத்திற்கு அருகில் சரிபார்க்கப்பட்ட கூட்டாளர்கள் இல்லை.",locationDenied:"இருப்பிட அனுமதி மறுக்கப்பட்டது. உலாவி அமைப்புகளில் அனுமதிக்கவும்.",locationUnavailable:"உங்கள் இருப்பிடத்தை கண்டறிய முடியவில்லை.",settingsHint:"இடைமுக மொழியைத் தேர்ந்தெடுக்கவும்."},
  te: {language:"భాష",home:"హోమ్",how:"ఎలా పనిచేస్తుంది",schemes:"పథకాలను చూడండి",about:"మా గురించి",faq:"తరచుగా అడిగే ప్రశ్నలు",dashboard:"డాష్‌బోర్డ్",profile:"ప్రొఫైల్",eligibility:"అర్హత",recommendations:"సిఫార్సులు",applications:"దరఖాస్తులు",saved:"సేవ్ చేసిన పథకాలు",compare:"పోల్చండి",assistant:"AI సహాయకుడు",notifications:"నోటిఫికేషన్లు",settings:"సెట్టింగ్స్",signin:"సైన్ ఇన్",signout:"లాగ్ అవుట్",getstarted:"ప్రారంభించండి",find:"నా పథకాలను కనుగొనండి",search:"శోధించండి",state:"రాష్ట్రం",field:"రంగం / ప్రయోజనం",selectState:"రాష్ట్రాన్ని ఎంచుకోండి",selectField:"రంగాన్ని ఎంచుకోండి",view:"పథకాన్ని చూడండి →",back:"పథకాలకు తిరిగి వెళ్ళండి",official:"అధికారిక దరఖాస్తు ↗",why:"ఈ పథకం ఎందుకు?",benefits:"పథకం ప్రయోజనాలు",documents:"అవసరమైన పత్రాలు",apply:"ఎలా దరఖాస్తు చేయాలి",finance:"ఆర్థిక ప్రణాళిక",nearby:"సమీపంలో సహాయం కనుగొనండి",location:"నా స్థానాన్ని ఉపయోగించండి",ask:"Scheme Sahayak AIని అడగండి",welcome:"నమస్కారం! నేను Scheme Sahayak AI. ప్రభుత్వ పథకాలను కనుగొనడం, అర్హతను అర్థం చేసుకోవడం, పోల్చడం మరియు దరఖాస్తును ప్లాన్ చేయడంలో సహాయం చేస్తాను.",placeholder:"మీ ప్రశ్న అడగండి…",thinking:"మీ ప్రశ్నను విశ్లేషిస్తున్నాను…",disclaimer:"AI మార్గదర్శకం సమాచార ప్రయోజనాల కోసం మాత్రమే. తుది అర్హత మరియు నిబంధనలను అధికారిక సంస్థతో నిర్ధారించండి.",exploreTitle:"ప్రభుత్వ పథకాలను అన్వేషించండి",searchPlaceholder:"పథకం పేరు, ప్రయోజనం, లాభం లేదా కీవర్డ్‌తో శోధించండి…",noSchemes:"పథకాలు కనబడలేదు",tryAgain:"మళ్లీ ప్రయత్నించండి",education:"విద్య",agriculture:"వ్యవసాయం",business:"వ్యాపారం మరియు పారిశ్రామికవేత్తలు",employment:"ఉపాధి",housing:"గృహం",health:"ఆరోగ్యం",women:"మహిళలు మరియు పిల్లల సంక్షేమం",social:"సామాజిక సంక్షేమం",financeAid:"ఆర్థిక సహాయం",skill:"నైపుణ్య అభివృద్ధి",scholarship:"స్కాలర్‌షిప్",msme:"MSME",animal:"పశుపోషణ",fisheries:"మత్స్య సంపద",rural:"గ్రామీణ అభివృద్ధి",allStates:"అన్ని రాష్ట్రాలు",allFields:"అన్ని రంగాలు",nearbyTitle:"మీకు సమీపంలో సహాయం",useLocation:"నా స్థానాన్ని ఉపయోగించండి",locating:"మీ స్థానాన్ని కనుగొంటున్నాం…",noPartners:"ఈ పథకానికి మీ సమీపంలో ధృవీకరించబడిన భాగస్వాములు లేరు.",locationDenied:"స్థాన అనుమతి నిరాకరించబడింది. బ్రౌజర్ సెట్టింగుల్లో అనుమతించండి.",locationUnavailable:"మీ స్థానాన్ని గుర్తించలేకపోయాము.",settingsHint:"ఇంటర్‌ఫేస్ భాషను ఎంచుకోండి."},
  kn: {language:"ಭಾಷೆ",home:"ಮುಖಪುಟ",how:"ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",schemes:"ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",about:"ನಮ್ಮ ಬಗ್ಗೆ",faq:"ಸಾಮಾನ್ಯ ಪ್ರಶ್ನೆಗಳು",dashboard:"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",profile:"ಪ್ರೊಫೈಲ್",eligibility:"ಅರ್ಹತೆ",recommendations:"ಶಿಫಾರಸುಗಳು",applications:"ಅರ್ಜಿಗಳು",saved:"ಉಳಿಸಿದ ಯೋಜನೆಗಳು",compare:"ಹೋಲಿಸಿ",assistant:"AI ಸಹಾಯಕ",notifications:"ಅಧಿಸೂಚನೆಗಳು",settings:"ಸೆಟ್ಟಿಂಗ್‌ಗಳು",signin:"ಸೈನ್ ಇನ್",signout:"ಲಾಗ್ ಔಟ್",getstarted:"ಪ್ರಾರಂಭಿಸಿ",find:"ನನ್ನ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಿ",search:"ಹುಡುಕಿ",state:"ರಾಜ್ಯ",field:"ಕ್ಷೇತ್ರ / ಉದ್ದೇಶ",selectState:"ರಾಜ್ಯ ಆಯ್ಕೆಮಾಡಿ",selectField:"ಕ್ಷೇತ್ರ ಆಯ್ಕೆಮಾಡಿ",view:"ಯೋಜನೆ ನೋಡಿ →",back:"ಯೋಜನೆಗಳಿಗೆ ಹಿಂತಿರುಗಿ",official:"ಅಧಿಕೃತ ಅರ್ಜಿ ↗",why:"ಈ ಯೋಜನೆ ಏಕೆ?",benefits:"ಯೋಜನೆಯ ಪ್ರಯೋಜನಗಳು",documents:"ಅಗತ್ಯ ದಾಖಲೆಗಳು",apply:"ಅರ್ಜಿ ಸಲ್ಲಿಸುವುದು ಹೇಗೆ",finance:"ಹಣಕಾಸು ಯೋಜಕ",nearby:"ಹತ್ತಿರದ ಸಹಾಯ ಹುಡುಕಿ",location:"ನನ್ನ ಸ್ಥಳ ಬಳಸಿ",ask:"Scheme Sahayak AI ಅನ್ನು ಕೇಳಿ",welcome:"ನಮಸ್ಕಾರ! ನಾನು Scheme Sahayak AI. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಲು, ಅರ್ಹತೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು, ಹೋಲಿಸಲು ಮತ್ತು ಅರ್ಜಿಯನ್ನು ಯೋಜಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ.",placeholder:"ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ…",thinking:"ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ…",disclaimer:"AI ಮಾರ್ಗದರ್ಶನ ಮಾಹಿತಿ ಉದ್ದೇಶಕ್ಕಾಗಿ ಮಾತ್ರ. ಅಂತಿಮ ಅರ್ಹತೆ ಮತ್ತು ನಿಯಮಗಳನ್ನು ಅಧಿಕೃತ ಸಂಸ್ಥೆಯಿಂದ ದೃಢೀಕರಿಸಿ.",exploreTitle:"ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",searchPlaceholder:"ಯೋಜನೆ ಹೆಸರು, ಉದ್ದೇಶ, ಪ್ರಯೋಜನ ಅಥವಾ ಕೀವರ್ಡ್ ಮೂಲಕ ಹುಡುಕಿ…",noSchemes:"ಯೋಜನೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ",tryAgain:"ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",education:"ಶಿಕ್ಷಣ",agriculture:"ಕೃಷಿ",business:"ವ್ಯಾಪಾರ ಮತ್ತು ಉದ್ಯಮಶೀಲತೆ",employment:"ಉದ್ಯೋಗ",housing:"ವಸತಿ",health:"ಆರೋಗ್ಯ",women:"ಮಹಿಳಾ ಮತ್ತು ಮಕ್ಕಳ ಕಲ್ಯಾಣ",social:"ಸಾಮಾಜಿಕ ಕಲ್ಯಾಣ",financeAid:"ಹಣಕಾಸು ಸಹಾಯ",skill:"ಕೌಶಲ್ಯ ಅಭಿವೃದ್ಧಿ",scholarship:"ವಿದ್ಯಾರ್ಥಿವೇತನ",msme:"MSME",animal:"ಪಶುಸಂಗೋಪನೆ",fisheries:"ಮೀನುಗಾರಿಕೆ",rural:"ಗ್ರಾಮೀಣ ಅಭಿವೃದ್ಧಿ",allStates:"ಎಲ್ಲಾ ರಾಜ್ಯಗಳು",allFields:"ಎಲ್ಲಾ ಕ್ಷೇತ್ರಗಳು",nearbyTitle:"ನಿಮ್ಮ ಹತ್ತಿರ ಸಹಾಯ ಹುಡುಕಿ",useLocation:"ನನ್ನ ಸ್ಥಳ ಬಳಸಿ",locating:"ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಹುಡುಕಲಾಗುತ್ತಿದೆ…",noPartners:"ಈ ಯೋಜನೆಗೆ ನಿಮ್ಮ ಹತ್ತಿರ ಪರಿಶೀಲಿಸಿದ ಪಾಲುದಾರರು ಕಂಡುಬಂದಿಲ್ಲ.",locationDenied:"ಸ್ಥಳ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ. ಬ್ರೌಸರ್ ಸೆಟ್ಟಿಂಗ್‌ಗಳಲ್ಲಿ ಅನುಮತಿಸಿ.",locationUnavailable:"ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಕಂಡುಹಿಡಿಯಲಾಗಲಿಲ್ಲ.",settingsHint:"ಇಂಟರ್‌ಫೇಸ್ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ."},
  ml: {language:"ഭാഷ",home:"ഹോം",how:"എങ്ങനെ പ്രവർത്തിക്കുന്നു",schemes:"പദ്ധതികൾ കണ്ടെത്തുക",about:"ഞങ്ങളെ കുറിച്ച്",faq:"പതിവുചോദ്യങ്ങൾ",dashboard:"ഡാഷ്ബോർഡ്",profile:"പ്രൊഫൈൽ",eligibility:"യോഗ്യത",recommendations:"ശുപാർശകൾ",applications:"അപേക്ഷകൾ",saved:"സേവ് ചെയ്ത പദ്ധതികൾ",compare:"താരതമ്യം",assistant:"AI സഹായി",notifications:"അറിയിപ്പുകൾ",settings:"ക്രമീകരണങ്ങൾ",signin:"സൈൻ ഇൻ",signout:"പുറത്തുകടക്കുക",getstarted:"തുടങ്ങുക",find:"എനിക്ക് അനുയോജ്യമായ പദ്ധതികൾ കണ്ടെത്തുക",search:"തിരയുക",state:"സംസ്ഥാനം",field:"മേഖല / ഉദ്ദേശ്യം",selectState:"സംസ്ഥാനം തിരഞ്ഞെടുക്കുക",selectField:"മേഖല തിരഞ്ഞെടുക്കുക",view:"പദ്ധതി കാണുക →",back:"പദ്ധതികളിലേക്ക് മടങ്ങുക",official:"ഔദ്യോഗിക അപേക്ഷ ↗",why:"ഈ പദ്ധതി എന്തുകൊണ്ട്?",benefits:"പദ്ധതിയുടെ ആനുകൂല്യങ്ങൾ",documents:"ആവശ്യമായ രേഖകൾ",apply:"എങ്ങനെ അപേക്ഷിക്കാം",finance:"സാമ്പത്തിക പ്ലാനർ",nearby:"അടുത്തുള്ള സഹായം കണ്ടെത്തുക",location:"എന്റെ ലൊക്കേഷൻ ഉപയോഗിക്കുക",ask:"Scheme Sahayak AI-യോട് ചോദിക്കുക",welcome:"നമസ്കാരം! ഞാൻ Scheme Sahayak AI. സർക്കാർ പദ്ധതികൾ കണ്ടെത്താനും യോഗ്യത മനസ്സിലാക്കാനും താരതമ്യം ചെയ്യാനും അപേക്ഷ ആസൂത്രണം ചെയ്യാനും സഹായിക്കും.",placeholder:"നിങ്ങളുടെ ചോദ്യം ചോദിക്കൂ…",thinking:"നിങ്ങളുടെ ചോദ്യം പരിശോധിക്കുന്നു…",disclaimer:"AI മാർഗനിർദ്ദേശം വിവര ആവശ്യത്തിനാണ്. അന്തിമ യോഗ്യതയും നിബന്ധനകളും ഔദ്യോഗിക അധികാരിയിൽ നിന്ന് സ്ഥിരീകരിക്കുക.",exploreTitle:"സർക്കാർ പദ്ധതികൾ കണ്ടെത്തുക",searchPlaceholder:"പദ്ധതിയുടെ പേര്, ഉദ്ദേശ്യം, ആനുകൂല്യം അല്ലെങ്കിൽ കീവേഡ് ഉപയോഗിച്ച് തിരയുക…",noSchemes:"പദ്ധതികൾ കണ്ടെത്തിയില്ല",tryAgain:"വീണ്ടും ശ്രമിക്കുക",education:"വിദ്യാഭ്യാസം",agriculture:"കൃഷി",business:"ബിസിനസും സംരംഭകത്വവും",employment:"തൊഴിൽ",housing:"ഭവനം",health:"ആരോഗ്യം",women:"സ്ത്രീ-ശിശു ക്ഷേമം",social:"സാമൂഹിക ക്ഷേമം",financeAid:"സാമ്പത്തിക സഹായം",skill:"നൈപുണ്യ വികസനം",scholarship:"സ്കോളർഷിപ്പ്",msme:"MSME",animal:"മൃഗസംരക്ഷണം",fisheries:"മത്സ്യബന്ധനം",rural:"ഗ്രാമവികസനം",allStates:"എല്ലാ സംസ്ഥാനങ്ങളും",allFields:"എല്ലാ മേഖലകളും",nearbyTitle:"നിങ്ങളുടെ സമീപത്ത് സഹായം കണ്ടെത്തുക",useLocation:"എന്റെ ലൊക്കേഷൻ ഉപയോഗിക്കുക",locating:"നിങ്ങളുടെ ലൊക്കേഷൻ കണ്ടെത്തുന്നു…",noPartners:"ഈ പദ്ധതിക്ക് സമീപത്ത് പരിശോധിച്ച പങ്കാളികളെ കണ്ടെത്താനായില്ല.",locationDenied:"ലൊക്കേഷൻ അനുമതി നിരസിച്ചു. ബ്രൗസർ ക്രമീകരണങ്ങളിൽ അനുവദിക്കുക.",locationUnavailable:"നിങ്ങളുടെ ലൊക്കേഷൻ കണ്ടെത്താനായില്ല.",settingsHint:"ഇന്റർഫേസ് ഭാഷ തിരഞ്ഞെടുക്കുക."}
};

const originals = Object.fromEntries(Object.entries(dictionaries.en).map(([k,v])=>[v,k]));

function translateDom(lang) {
  if (!document.body) return;
  const dict = dictionaries[lang] || dictionaries.en;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const current = node.nodeValue;
    const trimmed = current.trim();
    if (!trimmed || node.parentElement?.closest("script,style")) continue;

    // If React has just written a known English literal, refresh the stored
    // original. Otherwise preserve it so we can translate back from another
    // language without losing the source text.
    if (originals[trimmed]) node.__schemeOriginal = trimmed;
    const raw = node.__schemeOriginal || trimmed;
    const key = originals[raw];
    if (key && dict[key]) {
      const lead = current.match(/^\s*/)?.[0] || "";
      const trail = current.match(/\s*$/)?.[0] || "";
      const next = lead + dict[key] + trail;
      if (node.nodeValue !== next) node.nodeValue = next;
    }
  }

  document.querySelectorAll("input[placeholder],textarea[placeholder]").forEach((el) => {
    const current = el.placeholder || "";
    if (!current) return;
    if (originals[current]) el.dataset.schemeOriginal = current;
    const raw = el.dataset.schemeOriginal || current;
    const key = originals[raw];
    if (key && dict[key]) el.placeholder = dict[key];
  });
}

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => localStorage.getItem("scheme_sahayak_language") || "en");

  const changeLanguage = (next) => {
    if (dictionaries[next]) {
      setLanguage(next);
      localStorage.setItem("scheme_sahayak_language", next);
    }
  };

  useEffect(() => {
    document.documentElement.lang = language;

    let observer = null;
    let translating = false;

    const observe = () => {
      if (!document.body || !observer) return;
      observer.observe(document.body, { subtree: true, childList: true });
    };

    const translateSafely = () => {
      if (translating || !document.body) return;
      translating = true;
      observer?.disconnect();
      try {
        translateDom(language);
      } finally {
        translating = false;
        observe();
      }
    };

    observer = new MutationObserver(() => translateSafely());

    translateSafely();
    return () => observer?.disconnect();
  }, [language]);

  const value = useMemo(
    () => ({
      language,
      changeLanguage,
      languages: Object.keys(dictionaries),
      t: (key) => dictionaries[language]?.[key] ?? dictionaries.en[key] ?? key,
    }),
    [language]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const c = useContext(LanguageContext);
  if (!c) throw new Error("useLanguage must be used inside LanguageProvider");
  return c;
}
