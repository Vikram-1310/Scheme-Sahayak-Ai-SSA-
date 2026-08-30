import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { searchSchemes } from "../api/client";
import { useLanguage } from "../context/LanguageContext";

const STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
  "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
  "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
  "Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli and Daman and Diu",
  "Delhi","Jammu and Kashmir","Ladakh","Lakshadweep","Puducherry"
];

const FIELDS = [
  ["Education","Education"],["Agriculture","Agriculture"],["Business","Business & Entrepreneurship"],
  ["Employment","Employment"],["Housing","Housing"],["Healthcare","Healthcare"],
  ["Women & Child","Women & Child Welfare"],["Social Welfare","Social Welfare"],
  ["Financial Assistance","Financial Assistance"],["Skill Development","Skill Development"],
  ["Scholarship","Scholarship"],["MSME","MSME"],["Animal Husbandry","Animal Husbandry"],
  ["Fisheries","Fisheries"],["Rural Development","Rural Development"]
];

export default function Schemes() {
  const { t } = useLanguage();
  const [params] = useSearchParams();
  const [q, setQ] = useState(params.get("keyword") || "");
  const [state, setState] = useState(params.get("state") || "");
  const [field, setField] = useState(params.get("field") || "");
  const [data, setData] = useState({ schemes: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const run = async (event) => {
    event?.preventDefault();
    setLoading(true);
    setError("");
    try {
      setData(await searchSchemes(field || null, state || null, q.trim() || null));
    } catch (e) {
      setError(e.detail || "Unable to load schemes. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { run(); }, []);

  return (
    <main className="page">
      <div className="container">
        <div className="directory-head">
          <div>
            <span className="eyebrow">SCHEME DIRECTORY</span>
            <h1>{t("exploreTitle")}</h1>
            <p>{t("searchPlaceholder")}</p>
          </div>
          <div className="directory-count">
            <strong>{data.total || "4,693+"}</strong>
            <span>scheme records</span>
          </div>
        </div>

        <form className="scheme-filters" onSubmit={run}>
          <div className="filter-field">
            <label>{t("state")}</label>
            <select value={state} onChange={e => setState(e.target.value)}>
              <option value="">{t("allStates") || "All States"}</option>
              {STATES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="filter-field">
            <label>{t("field")}</label>
            <select value={field} onChange={e => setField(e.target.value)}>
              <option value="">{t("allFields") || "All Fields"}</option>
              {FIELDS.map(([value,label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
          <div className="filter-search">
            <label>{t("search")}</label>
            <input value={q} onChange={e => setQ(e.target.value)} placeholder={t("searchPlaceholder")} />
          </div>
          <button className="btn btn-primary filter-button" type="submit">{t("find")}</button>
        </form>

        {error && <div className="banner banner-error">{error}</div>}

        {loading ? (
          <div className="loading-grid">{[1,2,3,4,5,6].map(i => <div className="skeleton-card" key={i}/>)}</div>
        ) : (
          <div className="scheme-directory-grid">
            {data.schemes?.slice(0, 30).map(s => (
              <article className="directory-card" key={s.scheme_id}>
                <div className="directory-card-top">
                  <span className="tag">{s.government_level || "Government"}</span>
                  <span className="tag muted-tag">{(s.category || [])[0] || "Scheme"}</span>
                </div>
                <h2>{s.scheme_name}</h2>
                <p>{s.description || "Government scheme information and eligibility guidance."}</p>
                <div className="directory-meta">
                  <span>✓ Eligibility</span><span>₹ Financial support</span>
                </div>
                <Link className="text-link" to={`/schemes/${s.scheme_id}`}>{t("view")}</Link>
              </article>
            ))}
          </div>
        )}

        {!loading && data.schemes?.length === 0 && !error && (
          <div className="empty-state"><h3>{t("noSchemes")}</h3><p>Try another state, field or keyword.</p></div>
        )}
      </div>
    </main>
  );
}
