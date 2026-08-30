import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProfileApplications } from "../api/client";
import EmptyState from "../components/EmptyState";

const PROFILE_ID_KEY = "scheme_sahayak_profile_id";

const STATUS_LABEL = {
  submitted: { text: "Submitted", cls: "seal-unknown" },
  under_review: { text: "Under review", cls: "seal-unknown" },
  approved: { text: "Approved", cls: "seal-eligible" },
  rejected: { text: "Rejected", cls: "seal-not-eligible" },
  completed: { text: "Completed", cls: "seal-eligible" },
};

export default function Applications() {
  const profileId = localStorage.getItem(PROFILE_ID_KEY);
  const [applications, setApplications] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profileId) {
      setLoading(false);
      return;
    }
    getProfileApplications(profileId)
      .then((data) => setApplications(data.applications))
      .catch((err) => setError(err.detail || "Could not load applications."))
      .finally(() => setLoading(false));
  }, [profileId]);

  if (!profileId) {
    return (
      <div className="page container">
        <EmptyState
          title="No profile yet"
          description="Create your beneficiary profile first."
          action={
            <Link className="btn btn-primary" to="/profile">
              Build your profile
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <h1>Your applications</h1>
        <p>Track every scheme you've applied for and its current status.</p>

        {error && <div className="banner banner-error">{error}</div>}
        {loading && <p>Loading…</p>}

        {!loading && applications?.length === 0 && (
          <EmptyState
            title="No applications yet"
            description="Apply to a recommended scheme to see it tracked here."
            action={
              <Link className="btn btn-primary" to="/recommendations">
                View recommendations
              </Link>
            }
          />
        )}

        {applications?.map((app) => {
          const status = STATUS_LABEL[app.status] || { text: app.status, cls: "seal-unknown" };
          return (
            <div key={app.id} className="ledger-entry">
              <div className="ledger-entry-head">
                <div>
                  <div className="ledger-entry-title">Scheme: {app.scheme_id}</div>
                  <span className="muted">
                    Applied {new Date(app.created_at).toLocaleDateString()}
                  </span>
                </div>
                <span className={`seal ${status.cls}`}>{status.text}</span>
              </div>
              {app.notes && (
                <p style={{ marginTop: "0.6rem", marginBottom: 0 }}>{app.notes}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
