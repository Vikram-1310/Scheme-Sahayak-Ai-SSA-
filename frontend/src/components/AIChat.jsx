import { useEffect, useMemo, useState } from "react";
import { chatWithAI, getChatHistory } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

const SESSION_KEY = "scheme_sahayak_chat_session";

export default function AIChat({ schemeId = null }) {
  const { language, t } = useLanguage();
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [sessionId, setSessionId] = useState(() => localStorage.getItem(SESSION_KEY) || "");
  const [messages, setMessages] = useState([
    { role: "assistant", text: t("welcome") },
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setMessages(current => {
      const hasUser = current.some(m => m.role === "user");
      if (!hasUser) return [{ role: "assistant", text: t("welcome") }];
      return current;
    });
  }, [language, t]);

  useEffect(() => {
    if (!sessionId) return;
    getChatHistory(sessionId)
      .then((r) => {
        if (Array.isArray(r.messages) && r.messages.length) setMessages(r.messages.map(x => ({ role: x.role, text: x.content })));
      })
      .catch(() => {});
  }, [sessionId]);

  const suggestions = useMemo(() => schemeId
    ? ["Am I eligible for this scheme?", "What documents do I need?", "How do I apply?", "Explain the financial assistance"]
    : language === "hi" ? ["शिक्षा के लिए योजनाएँ बताएं", "व्यवसाय शुरू करने की योजनाएँ बताएं", "मैं पात्रता कैसे जाँचूँ?", "मेरे लिए योजना खोजें"]
    : language === "ta" ? ["கல்விக்கான திட்டங்களை சொல்லுங்கள்", "தொழில் தொடங்கும் திட்டங்களை சொல்லுங்கள்", "தகுதியை எப்படி சரிபார்ப்பது?", "எனக்கான திட்டத்தை தேடுங்கள்"]
    : language === "te" ? ["విద్యకు పథకాలు చెప్పండి", "వ్యాపారం ప్రారంభించే పథకాలు చెప్పండి", "అర్హతను ఎలా తనిఖీ చేయాలి?", "నా కోసం పథకం కనుగొనండి"]
    : language === "kn" ? ["ಶಿಕ್ಷಣದ ಯೋಜನೆಗಳನ್ನು ತಿಳಿಸಿ", "ವ್ಯಾಪಾರ ಆರಂಭದ ಯೋಜನೆಗಳನ್ನು ತಿಳಿಸಿ", "ಅರ್ಹತೆಯನ್ನು ಹೇಗೆ ಪರಿಶೀಲಿಸುವುದು?", "ನನಗಾಗಿ ಯೋಜನೆ ಹುಡುಕಿ"]
    : language === "ml" ? ["വിദ്യാഭ്യാസ പദ്ധതികൾ പറയൂ", "ബിസിനസ് തുടങ്ങാനുള്ള പദ്ധതികൾ പറയൂ", "യോഗ്യത എങ്ങനെ പരിശോധിക്കും?", "എനിക്കായി പദ്ധതി കണ്ടെത്തൂ"]
    : ["Find schemes for starting a business", "What schemes are available for education?", "How do I check eligibility?", "Help me find a scheme"], [schemeId, language]);

  const send = async (e, preset) => {
    e?.preventDefault();
    const text = (preset ?? message).trim();
    if (!text || loading) return;
    setMessage("");
    setMessages(m => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const result = await chatWithAI(text, { sessionId, language, schemeId });
      if (result.session_id && result.session_id !== sessionId) {
        setSessionId(result.session_id);
        localStorage.setItem(SESSION_KEY, result.session_id);
      }
      setMessages(m => [...m, {
        role: "assistant",
        text: result.reply || "I couldn't produce a grounded answer from the available scheme data.",
        matches: result.scheme_matches || []
      }]);
    } catch (err) {
      setMessages(m => [...m, { role: "assistant", text: err.detail || "I’m temporarily unable to connect to the assistant. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {open && (
        <section className="ai-panel" aria-label="Scheme Sahayak AI assistant">
          <div className="ai-panel-head">
            <div>
              <strong>Scheme Sahayak AI</strong>
              <span>{schemeId ? "Context-aware scheme assistant" : "Government scheme assistant"}</span>
            </div>
            <button className="icon-button" onClick={() => setOpen(false)} aria-label="Close assistant">×</button>
          </div>

          <div className="ai-suggestions">
            {suggestions.map(s => <button key={s} type="button" onClick={(e) => send(e, s)} disabled={loading}>{s}</button>)}
          </div>

          <div className="ai-messages" aria-live="polite">
            {messages.map((m, i) => (
              <div key={i} className={`ai-message ${m.role === "user" ? "user" : "assistant"}`}>
                <div className="ai-role">{m.role === "user" ? "You" : "Scheme Sahayak AI"}</div>
                <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>
              </div>
            ))}
            {loading && <div className="ai-message assistant"><div className="ai-role">Scheme Sahayak AI</div>Thinking through your question…</div>}
          </div>

          <form className="ai-input" onSubmit={send}>
            <input value={message} onChange={e => setMessage(e.target.value)} placeholder="Ask a question…" aria-label="Ask Scheme Sahayak AI" />
            <button className="btn btn-primary" disabled={loading || !message.trim()}>Send</button>
          </form>
          <div className="ai-disclaimer">AI guidance is informational. Confirm final eligibility and terms with the official scheme authority.</div>
        </section>
      )}
      <button className="ai-fab" onClick={() => setOpen(v => !v)} aria-label="Open Scheme Sahayak AI">
        <span>✦</span><b>AI</b>
      </button>
    </>
  );
}