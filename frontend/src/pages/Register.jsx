import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "", role: "beneficiary" });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(form.username.trim(), form.password, form.role);
      setSuccess(true);
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setError(err.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container auth-shell">
        <h1>Create your account</h1>
        <p>Register to build a beneficiary profile and see which schemes fit you.</p>

        {error && <div className="banner banner-error">{error}</div>}
        {success && (
          <div className="banner banner-info">Account created — taking you to sign in…</div>
        )}

        <form className="card" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
              minLength={3}
              autoFocus
            />
            <div className="field-hint">At least 3 characters.</div>
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              minLength={8}
            />
            <div className="field-hint">At least 8 characters.</div>
          </div>
          <div className="field">
            <label>Account type</label>
            <input value="Beneficiary" disabled />
            <div className="field-hint">Officer and admin accounts are provisioned securely.</div>
          </div>
          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="muted" style={{ marginTop: "1rem", textAlign: "center" }}>
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
