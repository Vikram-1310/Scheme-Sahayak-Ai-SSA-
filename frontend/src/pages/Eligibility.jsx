import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProfile, checkEligibility } from "../api/client";
import EmptyState from "../components/EmptyState";
import StatusSeal from "../components/StatusSeal";

const PROFILE_ID_KEY = "scheme_sahayak_profile_id";

export default function Eligibility() {
  const profileId = localStorage.getItem(PROFILE_ID_KEY);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showOnlyEligible, setShowOnlyEligible] = useState(false);

  const runCheck = async () => {
    setLoading(true);
    setError(null);
    try {
      const profileData = await getProfile(profileId);
      const p = profileData.profile;
      const data = await checkEligibility({
        category: p.category,
        annual_income: p.annual_income,
        age: p.age,
        purpose: p.purpose,
        gender: p.gender,
      });
      setResults(data);
    } catch (err) {
      setError(err.detail || "Could not run the eligibility check.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (profileId) runCheck();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profileId]);

  if (!profileId) {
    return (
      <div className="page container">
        <EmptyState
          title="No profile yet"
          description="Create your beneficiary profile first — eligibility is checked against it."
          action={
            <Link className="btn btn-primary" to="/profile">
              Build your profile
            </Link>
          }
        />
      </div>
    );
  }

  const entries = results?.results || [];
  const visible = showOnlyEligible ? entries.filter((r) => r.eligible) : entries;

  return (
    <div className="page">
      <div className="container">
        <h1>Eligibility ledger</h1>
        <p>
          {results
            ? `Checked against ${results.total_schemes_checked} scheme${
                results.total_schemes_checked === 1 ? "" : "s"
              }.`
            : "Run a check against every scheme in the registry."}
        </p>

        {error && <div className="banner banner-error">{error}</div>}

        <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "1.2rem" }}>
          <button className="btn btn-secondary" onClick={runCheck} disabled={loading}>
            {loading ? "Checking…" : "Re-check eligibility"}
          </button>
          {entries.length > 0 && (
            <label className="muted" style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
              <input
                type="checkbox"
                checked={showOnlyEligible}
                onChange={(e) => setShowOnlyEligible(e.target.checked)}
              />
              Show eligible only
            </label>
          )}
        </div>

        {loading && !results && <p>Running the check…</p>}

        {!loading && entries.length === 0 && results && (
          <EmptyState title="No schemes found" description="The scheme registry may be empty." />
        )}

        {visible.map((r) => (
          <div
            key={r.scheme_id}
            className={`ledger-entry ${r.eligible ? "is-eligible" : "is-not-eligible"}`}
          >
            <div className="ledger-entry-head">
              <div>
                <div className="ledger-entry-title">{r.scheme_name}</div>
                <StatusSeal eligible={r.eligible} />
              </div>
            </div>
            {r.reasons?.length > 0 && (
              <ul>
                {r.reasons.map((reason, i) => (
                  <li key={i}>{reason}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
