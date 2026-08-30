const API_URL = import.meta.env.VITE_API_URL || "";

const TOKEN_KEY = "scheme_sahayak_token";
const USER_KEY = "scheme_sahayak_user";

// Production backend on Render.
// Local development still uses Vite's /api proxy.
const API_BASE =
  import.meta.env.VITE_API_URL || "";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
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

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (auth) {
    const token = getToken();

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const res = await fetch(`${API_URL}/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;

  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const detail = data?.detail || res.statusText;

    if (res.status === 401) {
      clearSession();
    }

    throw new ApiError(detail, res.status, detail);
  }

  return data;
}


// ==================== AUTH ====================

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

export const loginUser = (username, password) =>
  request("/auth/login", {
    method: "POST",
    body: {
      username,
      password,
    },
    auth: false,
  });


// ==================== PROFILES ====================

export const createProfile = (profile) =>
  request("/profiles", {
    method: "POST",
    body: profile,
  });

export const getProfile = (profileId) =>
  request(`/profiles/${profileId}`);

export const updateProfile = (profileId, profile) =>
  request(`/profiles/${profileId}`, {
    method: "PUT",
    body: profile,
  });

export const getProfileApplications = (profileId) =>
  request(`/profiles/${profileId}/applications`);


// ==================== FEATURES ====================

export const getFeatures = () =>
  request("/features");

export const getFeature = (featureId) =>
  request(`/features/${featureId}`);


// ==================== ELIGIBILITY ====================

export const checkEligibility = (profile) =>
  request("/eligibility/check", {
    method: "POST",
    body: profile,
  });


// ==================== RECOMMENDATIONS ====================

export const getRecommendations = (profileWithAmount) =>
  request("/recommendations", {
    method: "POST",
    body: profileWithAmount,
  });


// ==================== APPLICATIONS ====================

export const submitApplication = (
  beneficiaryId,
  schemeId,
  notes
) =>
  request("/applications", {
    method: "POST",
    body: {
      beneficiary_id: beneficiaryId,
      scheme_id: schemeId,
      notes,
    },
  });

export const getApplication = (applicationId) =>
  request(`/applications/${applicationId}`);

export const updateApplicationStatus = (
  applicationId,
  status,
  notes
) =>
  request(`/applications/${applicationId}/status`, {
    method: "PUT",
    body: {
      status,
      notes,
    },
  });


// ==================== SCHEMES ====================

export const searchSchemes = (
  category,
  state,
  keyword
) => {
  const q = new URLSearchParams();

  if (category) q.set("category", category);
  if (state) q.set("state", state);
  if (keyword) q.set("keyword", keyword);

  return request(
    `/schemes/search${
      q.toString() ? `?${q.toString()}` : ""
    }`,
    {
      auth: false,
    }
  );
};

export const getScheme = (schemeId) =>
  request(
    `/schemes/${encodeURIComponent(schemeId)}`,
    {
      auth: false,
    }
  );


// ==================== AI ====================

export const chatWithAI = (
  message,
  {
    sessionId,
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

export const getChatHistory = (sessionId) =>
  request(
    `/ai/history/${encodeURIComponent(sessionId)}`
  );


// ==================== SAVED SCHEMES ====================

export const saveScheme = (schemeId) =>
  request(
    `/saved/${encodeURIComponent(schemeId)}`,
    {
      method: "POST",
    }
  );

export const unsaveScheme = (schemeId) =>
  request(
    `/saved/${encodeURIComponent(schemeId)}`,
    {
      method: "DELETE",
    }
  );

export const getSavedSchemes = () =>
  request("/saved");


// ==================== PARTNERS ====================

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

export { ApiError };