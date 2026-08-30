// frontend/src/api/client.js
// Scheme Sahayak AI API client
//
// Local development:
//   Vite proxy sends /api -> http://127.0.0.1:8000
//
// Production:
//   VITE_API_URL points to the deployed Render backend.

const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

const TOKEN_KEY = "scheme_sahayak_token";
const USER_KEY = "scheme_sahayak_user";

// --------------------------------------------------
// Session
// --------------------------------------------------

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem("scheme_sahayak_profile_id");
}

// --------------------------------------------------
// API Error
// --------------------------------------------------

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

// --------------------------------------------------
// Request helper
// --------------------------------------------------

async function request(
  path,
  {
    method = "GET",
    body = undefined,
    auth = true,
  } = {}
) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (auth) {
    const token = getToken();

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  /*
   * Local:
   *   API_BASE = ""
   *   /api/...
   *
   * Production:
   *   API_BASE =
   *   https://scheme-sahayak-ai-api.onrender.com
   *
   *   https://scheme-sahayak-ai-api.onrender.com/api/...
   */

  const url = `${API_BASE}/api${path}`;

  console.log(`[Scheme Sahayak API] ${method} ${url}`);

  let res;

  try {
    res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (error) {
    console.error("[Scheme Sahayak API] Network error:", error);

    throw new ApiError(
      "Unable to connect to the Scheme Sahayak AI backend.",
      0,
      error?.message || "Network error"
    );
  }

  let data = null;

  try {
    data = await res.json();
  } catch {
    // Response has no JSON body.
    data = null;
  }

  if (!res.ok) {
    const detail =
      data?.detail ||
      data?.message ||
      res.statusText ||
      "Request failed";

    if (res.status === 401) {
      clearSession();
    }

    console.error(
      `[Scheme Sahayak API] ${res.status}:`,
      detail
    );

    throw new ApiError(
      detail,
      res.status,
      detail
    );
  }

  return data;
}

// ==================================================
// AUTH
// ==================================================

export const registerUser = (
  username,
  password,
  role = "beneficiary"
) =>
  request("/auth/register", {
    method: "POST",
    body: {
      username,
      password,
      role,
    },
    auth: false,
  });

export const loginUser = (
  username,
  password
) =>
  request("/auth/login", {
    method: "POST",
    body: {
      username,
      password,
    },
    auth: false,
  });

// ==================================================
// PROFILES
// ==================================================

export const createProfile = (profile) =>
  request("/profiles", {
    method: "POST",
    body: profile,
  });

export const getProfile = (profileId) =>
  request(`/profiles/${profileId}`);

export const updateProfile = (
  profileId,
  profile
) =>
  request(`/profiles/${profileId}`, {
    method: "PUT",
    body: profile,
  });

export const getMyProfile = () =>
  request("/profiles/me");

export const getProfileApplications = (
  profileId
) =>
  request(
    `/profiles/${profileId}/applications`
  );

// ==================================================
// FEATURES
// ==================================================

export const getFeatures = () =>
  request("/features");

export const getFeature = (
  featureId
) =>
  request(
    `/features/${encodeURIComponent(featureId)}`
  );

// ==================================================
// ELIGIBILITY
// ==================================================

export const checkEligibility = (
  profile
) =>
  request("/eligibility/check", {
    method: "POST",
    body: profile,
  });

// ==================================================
// RECOMMENDATIONS
// ==================================================

export const getRecommendations = (
  profileWithAmount
) =>
  request("/recommendations", {
    method: "POST",
    body: profileWithAmount,
  });

// ==================================================
// SCHEMES
// ==================================================

export const searchSchemes = (
  category,
  state,
  keyword
) => {
  const q = new URLSearchParams();

  if (category) {
    q.set("category", category);
  }

  if (state) {
    q.set("state", state);
  }

  if (keyword) {
    q.set("keyword", keyword);
  }

  const queryString = q.toString();

  return request(
    `/schemes/search${
      queryString ? `?${queryString}` : ""
    }`,
    {
      auth: false,
    }
  );
};

export const getScheme = (
  schemeId
) =>
  request(
    `/schemes/${encodeURIComponent(schemeId)}`,
    {
      auth: false,
    }
  );

// ==================================================
// AI CHAT
// ==================================================

export const chatWithAI = (
  message,
  {
    sessionId = null,
    language = "en",
    schemeId = null,
  } = {}
) =>
  request("/ai/chat", {
    method: "POST",
    body: {
      message,
      session_id: sessionId,
      language,
      scheme_id: schemeId,
    },
  });

export const getChatHistory = (
  sessionId
) =>
  request(
    `/ai/history/${encodeURIComponent(
      sessionId
    )}`
  );

// ==================================================
// SAVED SCHEMES
// ==================================================

export const saveScheme = (
  schemeId
) =>
  request(
    `/saved/${encodeURIComponent(schemeId)}`,
    {
      method: "POST",
    }
  );

export const unsaveScheme = (
  schemeId
) =>
  request(
    `/saved/${encodeURIComponent(schemeId)}`,
    {
      method: "DELETE",
    }
  );

export const getSavedSchemes = () =>
  request("/saved");

// ==================================================
// CHANNEL PARTNERS
// ==================================================

export const getNearbyPartners = (
  schemeId,
  latitude,
  longitude,
  radiusKm = 50
) =>
  request(
    `/partners/nearby?scheme_id=${encodeURIComponent(
      schemeId
    )}&latitude=${latitude}&longitude=${longitude}&radius_km=${radiusKm}`,
    {
      auth: false,
    }
  );

// ==================================================
// APPLICATIONS
// ==================================================

export const submitApplication = (
  beneficiaryId,
  schemeId,
  notes = null
) =>
  request("/applications", {
    method: "POST",
    body: {
      beneficiary_id: beneficiaryId,
      scheme_id: schemeId,
      notes,
    },
  });

export const getApplication = (
  applicationId
) =>
  request(
    `/applications/${applicationId}`
  );

export const updateApplicationStatus = (
  applicationId,
  status,
  notes = null
) =>
  request(
    `/applications/${applicationId}/status`,
    {
      method: "PUT",
      body: {
        status,
        notes,
      },
    }
  );

// ==================================================
// EXPORT
// ==================================================

export { ApiError };