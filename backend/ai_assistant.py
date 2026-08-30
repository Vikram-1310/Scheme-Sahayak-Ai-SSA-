"""
Scheme Sahayak conversational assistant.

The assistant is deliberately grounded in the local scheme registry and the user's
saved profile. It maintains short-term conversation history in SQLite and can
optionally use an OpenAI-compatible or Ollama local model for natural language,
while retaining a deterministic grounded fallback.
"""
from __future__ import annotations
import json, os, re, urllib.request
from typing import Any

from ai.scheme_source import get_scheme_source
from ai.recommendation_service import get_recommendations
from ai.scheme_models import UserProfile
from backend.profile import get_my_profile
from backend.database import get_chat_messages

STOP = {"the","and","for","with","what","which","how","can","are","from","about",
        "scheme","schemes","please","tell","me","want","need","this","that",
        "show","find","give","help","you","your","my","is","am","i","to","of","in"}

TRANSLATIONS = {
    "hi": {
        "greet":"नमस्ते! मैं Scheme Sahayak AI हूँ। मैं सरकारी योजनाएँ खोजने, पात्रता समझने और आवेदन प्रक्रिया बताने में मदद कर सकता हूँ।",
        "need":"बेहतर सुझाव देने के लिए कृपया अपना राज्य, उद्देश्य और वार्षिक पारिवारिक आय बताएं।",
        "none":"मुझे मौजूदा योजना रजिस्ट्री में स्पष्ट मिलान नहीं मिला। राज्य, उद्देश्य, आय या श्रेणी बताकर फिर कोशिश करें।",
        "found":"आपकी जानकारी के आधार पर मुझे ये प्रासंगिक योजनाएँ मिलीं:",
    },
    "te": {
        "greet":"నమస్కారం! నేను Scheme Sahayak AI. ప్రభుత్వ పథకాలను కనుగొనడం, అర్హతను అర్థం చేసుకోవడం మరియు దరఖాస్తు ప్రక్రియలో సహాయం చేయగలను.",
        "need":"మంచి సూచనల కోసం మీ రాష్ట్రం, అవసరం మరియు వార్షిక కుటుంబ ఆదాయం చెప్పండి.",
        "none":"ప్రస్తుత పథకాల రిజిస్ట్రీలో స్పష్టమైన సరిపోలిక దొరకలేదు. రాష్ట్రం, అవసరం, ఆదాయం లేదా వర్గాన్ని జోడించి మళ్లీ ప్రయత్నించండి.",
        "found":"మీ సమాచారానికి సంబంధించిన పథకాలు ఇవి:",
    },
    "ta": {
        "greet":"வணக்கம்! நான் Scheme Sahayak AI. அரசு திட்டங்களை கண்டறியவும், தகுதியை புரிந்துகொள்ளவும், விண்ணப்ப செயல்முறையை அறியவும் உதவுகிறேன்.",
        "need":"சிறந்த பரிந்துரைகளுக்கு உங்கள் மாநிலம், நோக்கம் மற்றும் ஆண்டு குடும்ப வருமானத்தை கூறுங்கள்.",
        "none":"தற்போதைய திட்டப் பதிவில் தெளிவான பொருத்தம் கிடைக்கவில்லை. மாநிலம், நோக்கம், வருமானம் அல்லது வகையை சேர்த்து முயற்சிக்கவும்.",
        "found":"உங்கள் தகவலுக்கு தொடர்புடைய திட்டங்கள்:",
    },
    "kn": {
        "greet":"ನಮಸ್ಕಾರ! ನಾನು Scheme Sahayak AI. ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಲು, ಅರ್ಹತೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಮತ್ತು ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ.",
        "need":"ಉತ್ತಮ ಸಲಹೆಗಾಗಿ ನಿಮ್ಮ ರಾಜ್ಯ, ಉದ್ದೇಶ ಮತ್ತು ವಾರ್ಷಿಕ ಕುಟುಂಬ ಆದಾಯವನ್ನು ತಿಳಿಸಿ.",
        "none":"ಪ್ರಸ್ತುತ ಯೋಜನಾ ನೋಂದಣಿಯಲ್ಲಿ ಸ್ಪಷ್ಟ ಹೊಂದಾಣಿಕೆ ಸಿಗಲಿಲ್ಲ. ರಾಜ್ಯ, ಉದ್ದೇಶ, ಆದಾಯ ಅಥವಾ ವರ್ಗವನ್ನು ಸೇರಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
        "found":"ನಿಮ್ಮ ಮಾಹಿತಿಗೆ ಸಂಬಂಧಿಸಿದ ಯೋಜನೆಗಳು:",
    },
    "ml": {
        "greet":"നമസ്കാരം! ഞാൻ Scheme Sahayak AI. സർക്കാർ പദ്ധതികൾ കണ്ടെത്താനും യോഗ്യത മനസ്സിലാക്കാനും അപേക്ഷാ പ്രക്രിയയിൽ സഹായിക്കാനും കഴിയും.",
        "need":"കൂടുതൽ കൃത്യമായ നിർദ്ദേശങ്ങൾക്ക് നിങ്ങളുടെ സംസ്ഥാനം, ആവശ്യകത, വാർഷിക കുടുംബ വരുമാനം എന്നിവ പറയുക.",
        "none":"നിലവിലെ പദ്ധതി രജിസ്ട്രിയിൽ വ്യക്തമായ പൊരുത്തം കണ്ടെത്താനായില്ല. സംസ്ഥാനം, ആവശ്യകത, വരുമാനം അല്ലെങ്കിൽ വിഭാഗം ചേർത്ത് വീണ്ടും ശ്രമിക്കുക.",
        "found":"നിങ്ങളുടെ വിവരങ്ങൾക്ക് അനുയോജ്യമായ പദ്ധതികൾ:",
    }
}

def _profile_text(user_id:int) -> str:
    p=get_my_profile(user_id)
    if not p: return ""
    return ", ".join(f"{k}={p[k]}" for k in ("age","gender","category","annual_income","purpose","state","district","occupation","business_type") if p.get(k) not in (None,""))

def _search(message:str):
    source=get_scheme_source()
    text=message.lower()
    aliases={
        "education":"education","शिक्षा":"education","विद्या":"education","విద్య":"education","கல்வி":"education","ಶಿಕ್ಷಣ":"education","വിദ്യാഭ്യാസം":"education",
        "business":"business","व्यवसाय":"business","व्यापार":"business","వ్యాపారం":"business","வணிகம்":"business","ವ್ಯವಹಾರ":"business","ബിസിനസ്":"business",
        "agriculture":"agriculture","कृषि":"agriculture","వ్యవసాయం":"agriculture","விவசாயம்":"agriculture","ಕೃಷಿ":"agriculture","കൃഷി":"agriculture",
        "employment":"employment","रोजगार":"employment","ఉపాధి":"employment","வேலைவாய்ப்பு":"employment","ಉದ್ಯೋಗ":"employment","തൊഴിൽ":"employment",
        "housing":"housing","आवास":"housing","గృహం":"housing","வீடு":"housing","ವಸತಿ":"housing","ഭവനം":"housing",
        "women":"women","महिला":"women","महिलाओं":"women","మహిళ":"women","பெண்கள்":"women","ಮಹಿಳೆ":"women","സ്ത്രീ":"women",
        "health":"health","स्वास्थ्य":"health","ఆరోగ్యం":"health","சுகாதாரம்":"health","ಆರೋಗ್ಯ":"health","ആരോഗ്യം":"health",
        "scholarship":"scholarship","छात्रवृत्ति":"scholarship","విద్యార్థి":"scholarship","உதவித்தொகை":"scholarship","ವಿದ್ಯಾರ್ಥಿವೇತನ":"scholarship","സ്കോളർഷിപ്പ്":"scholarship",
        "loan":"loan","ऋण":"loan","రుణం":"loan","கடன்":"loan","ಸಾಲ":"loan","വായ്പ":"loan",
    }
    normalized=text
    for k,v in aliases.items():
        if k in normalized: normalized += " " + v
    terms=[t for t in re.findall(r"[A-Za-z]{3,}", normalized) if t not in STOP]
    scored=[]
    for s in source.all():
        hay=" ".join([s.scheme_name or "",s.description or ""," ".join(s.category or [])," ".join(s.benefits or []),s.state or "",s.ministry or "",s.eligibility_text_raw or ""]).lower()
        score=sum(2 if t in (s.scheme_name or "").lower() else 1 for t in terms if t in hay)
        if score: scored.append((score,s))
    scored.sort(key=lambda x:(-x[0],x[1].scheme_name))
    return scored[:5]

def _ollama(message, context, history, language):
    url=os.getenv("OLLAMA_URL","").strip()
    model=os.getenv("OLLAMA_MODEL","").strip()
    if not (url and model): return None
    system=("You are Scheme Sahayak AI, a careful Indian government-scheme assistant. "
            "Answer logically and conversationally. Use only the supplied scheme context; "
            "never invent benefits, eligibility, deadlines, offices or money. "
            "Distinguish AI guidance from official eligibility. Ask one useful follow-up "
            "question when profile information is missing. Respond in the requested language.")
    prompt=system+f"\nLanguage: {language}\nUser profile: {context or 'not available'}\n"
    prompt+="Recent conversation:\n"+json.dumps(history[-8:],ensure_ascii=False)+"\nUser: "+message
    body=json.dumps({"model":model,"prompt":prompt,"stream":False}).encode()
    try:
        req=urllib.request.Request(url.rstrip("/")+"/api/generate",data=body,headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=20) as r:
            data=json.loads(r.read().decode())
        return (data.get("response") or "").strip() or None
    except Exception:
        return None

def respond(message:str, user_id:int, language="en", scheme_id=None, history=None):
    msg=message.strip()
    lang=language if language in TRANSLATIONS else "en"
    t=TRANSLATIONS.get(lang,{})
    history=history or []
    profile=_profile_text(user_id)
    context=[]
    if scheme_id:
        s=get_scheme_source().get(scheme_id)
        if s: context.append(f"Selected scheme: {s.scheme_name}. Description: {s.description}. Benefits: {', '.join(s.benefits or [])}. Eligibility: {s.eligibility_text_raw or 'see official criteria'}.")
    hits=_search(msg)
    for _,s in hits[:5]:
        context.append(f"{s.scheme_name} | category={', '.join(s.category or [])} | benefits={', '.join(s.benefits or [])} | source={s.official_source or s.application_url or 'not provided'}")
    llm=_ollama(msg,profile,history,lang)
    if llm:
        return {"reply":llm,"mode":"llm","scheme_matches":[s.scheme_id for _,s in hits]}

    low=msg.lower()
    if any(x in low for x in ("hello","hi","hey","namaste","नमस्ते")):
        reply=t.get("greet","Hi! I’m Scheme Sahayak AI. I can help you discover and understand government schemes.")
    elif any(x in low for x in ("eligible","eligibility","qualify","पात्र","అర్హ", "தகுதி")):
        if scheme_id:
            s=get_scheme_source().get(scheme_id)
            if s:
                reply=f"I can help you assess the published criteria for {s.scheme_name}. {s.eligibility_text_raw or 'The registry does not contain enough structured eligibility detail.'} This is an AI-assisted assessment; final eligibility is confirmed by the implementing authority."
            else: reply="I couldn't verify that scheme in the registry."
        else:
            reply="I can assess a specific scheme more reliably. Open a scheme and ask me about eligibility, or tell me your age, state, category, annual income and purpose."
    elif any(x in low for x in ("document","documents","paper","certificate")):
        if scheme_id and get_scheme_source().get(scheme_id):
            s=get_scheme_source().get(scheme_id)
            reply=f"For {s.scheme_name}, check the Documents section and the official source before applying. I won't guess documents that are not present in the verified scheme data."
        else:
            reply="Tell me which scheme you mean, or open a scheme and ask about its documents. Requirements vary by scheme."
    elif hits:
        lines=[t.get("found","I found these relevant schemes in the current registry:")]
        for _,s in hits[:3]:
            benefit=(s.benefits[0] if s.benefits else "See scheme details for benefits.")
            lines.append(f"• {s.scheme_name} — {benefit[:180]}")
        lines.append("I can narrow these results if you provide your state, purpose, age, category and annual income.")
        reply="\n".join(lines)
    elif not profile:
        reply=t.get("need","To give a useful recommendation, tell me your state, purpose and annual family income.")
    else:
        reply=t.get("none","I couldn't find a close match in the current scheme registry. Add your state, purpose, income, age or category and I can narrow it down.")
    return {"reply":reply,"mode":"grounded","scheme_matches":[s.scheme_id for _,s in hits]}

