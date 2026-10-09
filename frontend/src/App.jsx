import React, { Fragment, useEffect, useState } from "react";
import axios from "axios";
import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000");


// ============================================================
// API HELPER
// ============================================================

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

const HISTORY_TIME_ZONE = "Asia/Kolkata";

const parseApiDate = (value) => {
  if (!value) return null;

  if (typeof value === "string") {
    const trimmedValue = value.trim();
    const hasTimeZone =
      /(?:Z|[+-]\d{2}:?\d{2})$/i.test(trimmedValue);

    return new Date(hasTimeZone ? trimmedValue : `${trimmedValue}Z`);
  }

  return new Date(value);
};


// ============================================================
// FRONTEND DATA CACHE
// ============================================================
// Reuse stable reference data while the SPA is open. This avoids
// repeating the same MongoDB-backed requests during navigation.
const resourceCache = new Map();

const getCachedResource = (key, url) => {
  if (!resourceCache.has(key)) {
    const request = api.get(url)
      .then((response) => response.data)
      .catch((error) => {
        resourceCache.delete(key);
        throw error;
      });

    resourceCache.set(key, request);
  }

  return resourceCache.get(key);
};


// ============================================================
// API ERROR HELPER
// ============================================================

const CHAT_CONTEXT_KEY = "polymer_chat_context";

const saveChatContext = (context) => {
  try {
    localStorage.setItem(CHAT_CONTEXT_KEY, JSON.stringify(context));
  } catch (error) {
    console.warn("Unable to save chatbot context:", error);
  }
};

const loadChatContext = () => {
  try {
    const raw = localStorage.getItem(CHAT_CONTEXT_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    console.warn("Unable to load chatbot context:", error);
    return null;
  }
};

const AuthContext = React.createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  const loadSession = async () => {
    try {
      const response = await api.get("/auth/me");
      setUser(response.data.user);
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error("Unable to check authentication session:", error);
      }
      setUser(null);
    } finally {
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    loadSession();
  }, []);

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } finally {
      localStorage.removeItem(CHAT_CONTEXT_KEY);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, authLoading, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  return React.useContext(AuthContext);
}


const getApiErrorMessage = (error, fallbackMessage) => {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const location = Array.isArray(item?.loc)
          ? item.loc.filter(
              (part) => part !== "body"
            )
          : [];

        const field = location.length
          ? location.join(" → ")
          : "Request";

        return `${field}: ${item?.msg || "Validation error."}`;
      })
      .join(" | ");
  }

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  return fallbackMessage;
};


// ============================================================
// LAYOUT
// ============================================================

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app">

      <style>{`
        .engineering-suitability-section {
          margin-top: 28px;
        }

        .engineering-section-heading {
          margin-bottom: 18px;
        }

        .engineering-section-heading h3 {
          margin: 6px 0 0;
          font-size: 24px;
          line-height: 1.25;
        }

        .engineering-summary-grid {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 16px;
          margin-bottom: 16px;
        }

        .engineering-summary-card {
          background: #ffffff;
          border: 1px solid #dfe3eb;
          border-radius: 14px;
          padding: 18px 20px;
          min-height: 88px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          gap: 8px;
          box-sizing: border-box;
        }

        .engineering-summary-card span {
          font-size: 13px;
          color: #64748b;
          font-weight: 600;
        }

        .engineering-summary-card strong {
          font-size: 24px;
          line-height: 1.1;
          color: #172b4d;
          font-weight: 700;
        }

        .engineering-explanation-box,
        .engineering-observation-box {
          background: #ffffff;
          border: 1px solid #dfe3eb;
          border-radius: 14px;
          padding: 22px 24px;
          box-sizing: border-box;
        }

        .engineering-explanation-box h4,
        .engineering-observation-box h4 {
          margin: 0 0 12px;
          font-size: 16px;
          color: #172b4d;
        }

        .engineering-explanation-box p,
        .engineering-observation-box p {
          margin: 0;
          line-height: 1.7;
          font-size: 15px;
          color: #17365d;
        }

        .engineering-observation-box {
          margin-top: 14px;
        }

        @media (max-width: 800px) {
          .engineering-summary-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <header className="header">

        <div className="header-content">

          <NavLink to="/" className="brand-link">

            <div className="brand">

              <div className="brand-icon">
                🧪
              </div>

              <div>
                <h1>
                  Intelligent Polymer Selection
                </h1>

                <p>
                  Material Selection & Recommendation System
                </p>
              </div>

            </div>

          </NavLink>


          {user && <nav className="navigation">

            <NavLink
              to="/"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              end
            >
              Dashboard
            </NavLink>

            <NavLink
              to="/recommendation"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Material Recommendation
            </NavLink>

            <NavLink
              to="/custom"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Custom Selection
            </NavLink>

            <NavLink
              to="/history"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              History
            </NavLink>

          </nav>}


          <div className="status user-status">

            <span className="status-dot"></span>

            <span className="user-status-name">{user?.display_name || "System Ready"}</span>
            {user && (
              <button
                type="button"
                className="logout-button"
                onClick={async () => {
                  await logout();
                  navigate("/login");
                }}
              >
                Logout
              </button>
            )}

          </div>

        </div>

      </header>


      {/* PAGE */}

      {children}


      <footer className="footer">
        <p>© 2026 — Polymer Engineering Decision Support System</p>
      </footer>
      <PolymerChatbot />

    </div>
  );
}

function ProtectedRoute({ children }) {
  const { user, authLoading } = useAuth();
  const location = useLocation();

  if (authLoading) {
    return <main className="main-container"><p>Checking your session…</p></main>;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

function PasswordVisibilityButton({ visible, onClick, label }) {
  return (
    <button
      type="button"
      className="password-visibility-button"
      onClick={onClick}
      aria-label={visible ? `Hide ${label}` : `Show ${label}`}
      title={visible ? `Hide ${label}` : `Show ${label}`}
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        {visible ? (
          <>
            <path d="M3 3l18 18" />
            <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
            <path d="M9.9 5.3A11.7 11.7 0 0 1 12 5c5 0 8.7 4.1 9.8 7a12.8 12.8 0 0 1-3.1 4.5" />
            <path d="M6.6 6.6A12.5 12.5 0 0 0 2.2 12c1.1 2.9 4.8 7 9.8 7a10.8 10.8 0 0 0 3.1-.5" />
          </>
        ) : (
          <>
            <path d="M2.2 12C3.3 9.1 7 5 12 5s8.7 4.1 9.8 7c-1.1 2.9-4.8 7-9.8 7S3.3 14.9 2.2 12Z" />
            <circle cx="12" cy="12" r="3" />
          </>
        )}
      </svg>
    </button>
  );
}

function AuthPage({ mode }) {
  const isRegister = mode === "register";
  const navigate = useNavigate();
  const location = useLocation();
  const { user, setUser } = useAuth();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) navigate("/", { replace: true });
  }, [user, navigate]);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    if (isRegister && !displayName.trim()) {
      setError("Please enter your name.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (isRegister && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    try {
      setLoading(true);
      const response = await api.post(
        isRegister ? "/auth/register" : "/auth/login",
        isRegister
          ?           {
              email,
              display_name: displayName,
              password,
            }
          : { email, password },
      );
      localStorage.removeItem(CHAT_CONTEXT_KEY);
      setUser(response.data.user);
      const destination = location.state?.from?.pathname || "/";
      navigate(destination, { replace: true });
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to complete authentication."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-card-heading">
          <div>
            <span className="section-label">{isRegister ? "CREATE ACCOUNT" : "WELCOME BACK"}</span>
            <p className="auth-kicker">PolyGuide AI workspace</p>
          </div>
        </div>
        <h2>{isRegister ? "Create your account" : "Sign in to PolyGuide AI"}</h2>
        <p className="auth-description">
          
            
        </p>
        {error && <div className="error-message">{error}</div>}
        <form className="auth-form" onSubmit={submit}>
          {isRegister && (
            <label className="auth-field">
              Full name
              <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} autoComplete="name" required />
            </label>
          )}
          <label className="auth-field">
            Email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required />
          </label>
          <label className="auth-field">
            Password
            <span className="password-input-wrap">
              <input type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} autoComplete={isRegister ? "new-password" : "current-password"} minLength={8} required />
              <PasswordVisibilityButton visible={showPassword} onClick={() => setShowPassword((current) => !current)} label="password" />
            </span>
          </label>
          {isRegister && (
            <label className="auth-field">
              Confirm Password
              <span className="password-input-wrap">
                <input type={showConfirmPassword ? "text" : "password"} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" minLength={8} required />
                <PasswordVisibilityButton visible={showConfirmPassword} onClick={() => setShowConfirmPassword((current) => !current)} label="confirm password" />
              </span>
            </label>
          )}
          <button className="primary-button auth-submit" type="submit" disabled={loading}>
            {loading ? "Please wait…" : isRegister ? "Create account" : "Sign in"}
          </button>
        </form>
        <p className="auth-switch">
          {isRegister ? "Already have an account? " : "Need an account? "}
          <NavLink to={isRegister ? "/login" : "/register"}>
            {isRegister ? "Sign in" : "Register"}
          </NavLink>
        </p>
      </section>
    </main>
  );
}


// ============================================================
// PROFESSIONAL APPLICATION DISPLAY NAMES
// ============================================================

const getApplicationDisplayName = (applicationName) => {
  const names = {
    Automotive_Underhood_Bracket:
      "Automotive Underhood Structural Bracket",
    Transparent_Safety_Shield:
      "Transparent Safety Shield",
    Consumer_Drink_Closure:
      "Consumer Beverage Closure",
    High_Temperature_Aerospace_Connector:
      "High-Temperature Aerospace Connector",
    Medical_Autoclave_Tray:
      "Medical Autoclave Tray",
    Precision_Actuator_Gear:
      "Precision Actuator Gear",
    "Air Cooler Water-Distribution Tray":
      "Air Cooler Water Distribution Tray",
  };

  return names[applicationName] || applicationName;
};


// ============================================================
// DASHBOARD
// ============================================================

function Dashboard() {

  const navigate = useNavigate();

  const [applications, setApplications] = useState([]);
  const [polymerCount, setPolymerCount] = useState(0);
  const [propertyCount, setPropertyCount] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {

    loadDashboardData();

  }, []);


  const loadDashboardData = async () => {

    try {

      setLoading(true);
      setError("");

      const [
        applicationsData,
        polymersData,
        propertiesData,
      ] = await Promise.all([
        getCachedResource("applications", "/applications"),
        getCachedResource("polymers", "/polymers"),
        getCachedResource("properties", "/properties"),
      ]);

      setApplications(
        applicationsData.applications || []
      );

      setPolymerCount(
        (polymersData.polymers || []).length
      );

      setPropertyCount(
        (propertiesData.properties || []).length
      );

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load dashboard data. Make sure FastAPI is running."
      );

    } finally {

      setLoading(false);

    }

  };


  return (

    <main className="main-container">

      {/* HERO */}

      <section className="hero-section">

        <span className="section-label">
          ENGINEERING DECISION SUPPORT
        </span>

        <h2>
          Intelligent Polymer Selection
          for Engineering Applications.
        </h2>

        <p>
          Select suitable polymer materials using application
          requirements, hard constraints and weighted
          Multi-Criteria Decision-Making (MCDM).
        </p>

      </section>


      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}


      {/* SYSTEM OVERVIEW */}

      <section className="dashboard-stats">

        <div className="dashboard-stat-card">

          <span>
            APPLICATION SCENARIOS
          </span>

          <strong>
            {loading ? "—" : applications.length}
          </strong>

          <p>
            Predefined engineering applications
          </p>

        </div>


        <div className="dashboard-stat-card">

          <span>
            POLYMER MATERIALS
          </span>

          <strong>
            {loading ? "—" : polymerCount}
          </strong>

          <p>
            Materials available for evaluation
          </p>

        </div>


        <div className="dashboard-stat-card">

          <span>
            SUPPORTED PROPERTIES
          </span>

          <strong>
            {loading ? "—" : propertyCount}
          </strong>

          <p>
            Selection criteria supported
          </p>

        </div>

      </section>


      {/* QUICK START */}

      <section className="dashboard-card">

        <div>

          <span className="section-label">
            QUICK START
          </span>

          <h3>
            Find the best polymer for your application
          </h3>

          <p>
            Choose from predefined application scenarios
            and let the recommendation engine rank the
            most suitable materials.
          </p>

        </div>


        <button
          className="primary-button"
          onClick={() => navigate("/recommendation")}
        >
          Start Recommendation
          <span>→</span>
        </button>

      </section>


      {/* APPLICATION LIST */}

      <section className="applications-section">

        <div className="section-heading">

          <div>

            <span className="section-label">
              AVAILABLE SCENARIOS
            </span>

            <h3>
              Application Scenarios
            </h3>

          </div>

        </div>


        <div className="application-grid">

          {applications.map((application) => (

            <div
              className="application-card"
              key={application.Analysis_ID}
            >

              <div className="application-id">
                {application.Analysis_ID}
              </div>

              <div>

                <h4>
                  {getApplicationDisplayName(application.Application_Name)}
                </h4>

                <p>
                  Predefined MCDM selection scenario
                </p>

              </div>

            </div>

          ))}

        </div>

      </section>

    </main>

  );
}




// ============================================================
// POLYMER DETAIL PANEL
// ============================================================

function PolymerDetailPanel({ material, polymer }) {

  return (

    <div className="polymer-detail-panel">

      <div className="polymer-detail-header">

        <div>

          <span className="detail-label">
            MATERIAL DETAILS
          </span>

          <h4>
            {polymer?.Polymer_Name ||
              material?.polymer_id}
          </h4>

          <p>
            {polymer?.Polymer_ID ||
              material?.polymer_id}

            {polymer?.Polymer_Family
              ? ` • ${polymer.Polymer_Family}`
              : ""}
          </p>

        </div>

        <div className="detail-score">

          <span>
            MCDM SCORE
          </span>

          <strong>
            {Number(
              material?.mcdm_score || 0
            ).toFixed(4)}
          </strong>

        </div>

      </div>


      {/* MATERIAL INFORMATION */}

      <div className="detail-meta-grid">

        <div className="detail-meta-item">

          <span>
            Material Type
          </span>

          <strong>
            {polymer?.Material_Type || "—"}
          </strong>

        </div>


        <div className="detail-meta-item">

          <span>
            Manufacturer
          </span>

          <strong>
            {polymer?.Manufacturer || "—"}
          </strong>

        </div>


        <div className="detail-meta-item">

          <span>
            Grade
          </span>

          <strong>
            {polymer?.Grade || "—"}
          </strong>

        </div>


        <div className="detail-meta-item">

          <span>
            Processing
          </span>

          <strong>
            {polymer?.Processing_Method || "—"}
          </strong>

        </div>


        <div className="detail-meta-item">

          <span>
            Recyclability
          </span>

          <strong>
            {polymer?.Recyclability || "—"}
          </strong>

        </div>


        <div className="detail-meta-item">

          <span>
            Rank
          </span>

          <strong>
            #{material?.rank}
          </strong>

        </div>


        <div className="detail-meta-item">

          <span>
            Screening Status
          </span>

          <strong className="passed-status">
            ✓ Passed
          </strong>

        </div>

      </div>


      {/* APPLICATION / DESCRIPTION */}

      {(polymer?.Common_Applications ||
        polymer?.Description) && (

        <div className="polymer-context-grid">

          {polymer?.Common_Applications && (

            <div className="polymer-context-item">

              <span>
                Common Applications
              </span>

              <p>
                {polymer.Common_Applications}
              </p>

            </div>

          )}


          {polymer?.Description && (

            <div className="polymer-context-item">

              <span>
                Description
              </span>

              <p>
                {polymer.Description}
              </p>

            </div>

          )}

        </div>

      )}


    </div>

  );
}


// ============================================================
// RECOMMENDATION OVERVIEW
// ============================================================

function RecommendationOverview({ recommendations, polymers }) {

  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  const topMaterial = recommendations[0];

  const topPolymer = polymers.find(
    (polymer) =>
      polymer.Polymer_ID === topMaterial.polymer_id
  );

  const score = Number(
    topMaterial.mcdm_score || 0
  );

  const topContributions = Object.entries(
    topMaterial.weighted_contributions || {}
  )
    .map(([criterion, value]) => ({
      criterion,
      value: Number(value || 0),
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 3);

  return (
    <div className="recommendation-overview">

      <div className="overview-top">

        <div className="overview-material">

          <span className="overview-eyebrow">
            TOP RECOMMENDED MATERIAL
          </span>

          <h3>
            {topPolymer?.Polymer_Name ||
              topMaterial.polymer_id}
          </h3>

          <p>
            {topMaterial.polymer_id}

            {topPolymer?.Polymer_Family
              ? ` • ${topPolymer.Polymer_Family}`
              : ""}
          </p>

        </div>

        <div className="overview-score">

          <span>
            MCDM SCORE
          </span>

          <strong>
            {score.toFixed(4)}
          </strong>

          <small>
            {(score * 100).toFixed(1)}% performance
          </small>

        </div>

      </div>


      <div className="overview-status">

        <div className="overview-status-item">
          <span>Rank</span>
          <strong>#1</strong>
        </div>

        <div className="overview-status-item">
          <span>Screening</span>
          <strong className="passed-status">
            ✓ Passed
          </strong>
        </div>

        <div className="overview-status-item">
          <span>Recommended Materials</span>
          <strong>
            {recommendations.length}
          </strong>
        </div>

      </div>


      <div className="overview-comparison">

        <div className="overview-comparison-header">
          <h4>
            Recommendation Comparison
          </h4>

          <span>
            Higher score indicates stronger overall fit
          </span>
        </div>

        <div className="comparison-list">

          {recommendations.map(
            (material, index) => {

              const materialScore =
                Number(
                  material.mcdm_score || 0
                );

              const polymer =
                polymers.find(
                  (item) =>
                    item.Polymer_ID ===
                    material.polymer_id
                );

              return (
                <div
                  className="comparison-row"
                  key={`${material.polymer_id}-${index}`}
                >

                  <div className="comparison-name">

                    <strong>
                      #{material.rank}
                    </strong>

                    <span>
                      {polymer?.Polymer_Name ||
                        material.polymer_id}
                    </span>

                  </div>

                  <div className="comparison-bar">

                    <div
                      className="comparison-fill"
                      style={{
                        width: `${Math.max(
                          0,
                          Math.min(
                            100,
                            materialScore * 100
                          )
                        )}%`,
                      }}
                    />

                  </div>

                  <strong className="comparison-score">
                    {materialScore.toFixed(4)}
                  </strong>

                </div>
              );
            }
          )}

        </div>

      </div>


      <div className="overview-strengths">

        <div>

          <h4>
            Main scoring strengths
          </h4>

          <p>
            The leading material passed mandatory
            screening and achieved the highest overall
            weighted MCDM score.
          </p>

        </div>

        {topContributions.length > 0 && (

          <div className="strength-tags">

            {topContributions.map(
              ({ criterion, value }) => (

                <span
                  className="strength-tag"
                  key={criterion}
                >
                  {criterion}: {value.toFixed(4)}
                </span>

              )
            )}

          </div>

        )}

      </div>

    </div>
  );
}


// ============================================================
// ENGINEERING SUITABILITY ASSESSMENT
// ============================================================

function EngineeringSuitabilityAssessment({ material, polymers }) {

  if (!material) {
    return null;
  }

  const explanation =
    material.engineering_explanation || {};

  const polymer = polymers?.find(
    (item) => item.Polymer_ID === material.polymer_id
  );

  const materialName =
    polymer?.Polymer_Name ||
    material.polymer_id ||
    "Selected Material";

  const whySuitable =
    explanation.why_this_material_is_suitable ||
    explanation.final_summary ||
    "The recommendation is based on the combined performance of the selected engineering criteria using weighted MCDM.";

  const observation =
    explanation.key_observation ||
    "The final recommendation reflects the combined performance of the selected engineering criteria.";

  const suitability =
    explanation.overall_suitability ||
    "—";

  const score = Number(
    explanation.mcdm_score ?? material.mcdm_score ?? 0
  );

  const rank =
    explanation.rank ?? material.rank ?? "—";

  return (

    <section className="engineering-suitability-section">

      <div className="engineering-section-heading">

        <span className="section-label">
          ENGINEERING ANALYSIS
        </span>

        <h3>
          Engineering Suitability Assessment
        </h3>

      </div>

      <div className="engineering-summary-grid">

        <div className="engineering-summary-card">
          <span>Overall Suitability</span>
          <strong>{suitability}</strong>
        </div>

        <div className="engineering-summary-card">
          <span>MCDM Score</span>
          <strong>{score.toFixed(4)}</strong>
        </div>

        <div className="engineering-summary-card">
          <span>Rank</span>
          <strong>#{rank}</strong>
        </div>

      </div>

      <div className="engineering-explanation-box">

        <h4>
          Material Selection Rationale
        </h4>

        <p>
          <strong>{materialName}</strong> — {whySuitable}
        </p>

      </div>

      <div className="engineering-observation-box">

        <h4>
          Key Observation
        </h4>

        <p>
          {observation}
        </p>

      </div>

    </section>
  );
}


// ============================================================
// RECOMMENDATION PAGE
// ============================================================

function RecommendationPage() {

  const [applications, setApplications] = useState([]);

  const [selectedApplication, setSelectedApplication] =
    useState("");

  const [topN, setTopN] = useState(5);

  const [recommendations, setRecommendations] =
    useState([]);

  const [polymers, setPolymers] =
    useState([]);

  const [expandedPolymer, setExpandedPolymer] =
    useState(null);

  const [applicationName, setApplicationName] =
    useState("");

  const [totalEligible, setTotalEligible] =
    useState(0);

  const [rejectedCount, setRejectedCount] =
    useState(0);

  const [loadingApplications, setLoadingApplications] =
    useState(true);

  const [loadingRecommendation, setLoadingRecommendation] =
    useState(false);

  const [error, setError] = useState("");


  useEffect(() => {

    loadApplications();
    loadPolymers();

  }, []);


  const loadPolymers = async () => {

    try {

      const data = await getCachedResource("polymers", "/polymers");

      setPolymers(data.polymers || []);

    } catch (err) {

      console.error(err);

    }

  };


  const loadApplications = async () => {

    try {

      setLoadingApplications(true);

      const responseData = await getCachedResource(
        "applications",
        "/applications"
      );

      const data = responseData.applications || [];

      setApplications(data);

      if (data.length > 0) {

        setSelectedApplication(
          data[0].Analysis_ID
        );

      }

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load applications."
      );

    } finally {

      setLoadingApplications(false);

    }

  };


  const handleRecommendation = async () => {

    if (!selectedApplication) {

      setError(
        "Please select an application."
      );

      return;

    }


    try {

      setLoadingRecommendation(true);
      setError("");

      const response = await api.post(
        "/recommend",
        {
          analysis_id: selectedApplication,
          top_n: Number(topN),
        }
      );

      const data = response.data;

      setApplicationName(
        data.application_name
      );

      const recommendationResults =
        data.recommendations || [];

      setRecommendations(
        recommendationResults
      );

      setTotalEligible(
        data.total_eligible
      );

      setRejectedCount(
        data.rejected_count
      );

      saveChatContext({
        type: "predefined",
        history_id: data.history_id,
        analysis_id: data.analysis_id || selectedApplication,
        application_name: data.application_name,
        total_eligible: data.total_eligible,
        rejected_count: data.rejected_count,
        requirements: data.requirements || [],
        recommendations: recommendationResults.slice(0, 10),
        materials: recommendationResults.slice(0, 10).map((material) => {
          const polymer = polymers.find(
            (item) => item.Polymer_ID === material.polymer_id
          );

          return {
            polymer_id: material.polymer_id,
            polymer_name: polymer?.Polymer_Name || "",
            polymer_family: polymer?.Polymer_Family || "",
            material_type: polymer?.Material_Type || "",
            manufacturer: polymer?.Manufacturer || "",
            grade: polymer?.Grade || "",
          };
        }),
      });

    } catch (err) {

      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Recommendation failed."
        )
      );

    } finally {

      setLoadingRecommendation(false);

    }

  };


  return (

    <main className="main-container">

      {/* PAGE HEADER */}

      <section className="page-header">

        <span className="section-label">
          MATERIAL RECOMMENDATION
        </span>

        <h2>
          Find the Right Polymer
        </h2>

        <p>
          Select a predefined Engineering Application
          and Evaluate the Available Polymer materials.
        </p>

      </section>


      {/* SELECTION CARD */}

      <section className="selection-card">

        <div className="card-header">

          <h3>
            Application Requirements
          </h3>

          <p>
            Select an application scenario and the number
            of recommendations required.
          </p>

        </div>


        <div className="form-grid">

          <div className="form-group">

            <label>
              Application
            </label>

            <select
              value={selectedApplication}
              onChange={(event) =>
                setSelectedApplication(
                  event.target.value
                )
              }
              disabled={loadingApplications}
            >

              {loadingApplications ? (

                <option>
                  Loading applications...
                </option>

              ) : (

                applications.map((application) => (

                  <option
                    key={application.Analysis_ID}
                    value={application.Analysis_ID}
                  >
                    {application.Analysis_ID} —{" "}
                    {getApplicationDisplayName(application.Application_Name)}
                  </option>

                ))

              )}

            </select>

          </div>


          <div className="form-group">

            <label>
              Number of Recommendations
            </label>

            <select
              value={topN}
              onChange={(event) =>
                setTopN(
                  Number(event.target.value)
                )
              }
            >

              <option value={3}>
                Top 3
              </option>

              <option value={5}>
                Top 5
              </option>

              <option value={10}>
                Top 10
              </option>

            </select>

          </div>

        </div>


        <button
          className="primary-button recommendation-button"
          onClick={handleRecommendation}
          disabled={
            loadingApplications ||
            loadingRecommendation ||
            !selectedApplication
          }
        >

          {loadingRecommendation
            ? "Calculating..."
            : "Find Recommended Materials"}

          {!loadingRecommendation && (
            <span>→</span>
          )}

        </button>

      </section>


      {error && (

        <div className="error-message">

          <strong>Error:</strong>{" "}
          {error}

        </div>

      )}


      {/* RESULTS */}

      {recommendations.length > 0 && (

        <section className="results-section">

          <div className="page-header result-heading">

            <span className="section-label">
              RECOMMENDATION RESULTS
            </span>

            <h2>
              {applicationName}
            </h2>

          </div>


          {/* SUMMARY */}

          <div className="summary-grid">

            <div className="summary-card">

              <span className="summary-label">
                Eligible Materials
              </span>

              <strong>
                {totalEligible}
              </strong>

            </div>


            <div className="summary-card">

              <span className="summary-label">
                Rejected Materials
              </span>

              <strong>
                {rejectedCount}
              </strong>

            </div>


            <div className="summary-card">

              <span className="summary-label">
                Recommendations
              </span>

              <strong>
                {recommendations.length}
              </strong>

            </div>

          </div>


          {/* RECOMMENDATION OVERVIEW */}

          <RecommendationOverview
            recommendations={recommendations}
            polymers={polymers}
          />


          {/* TABLE */}

          <div className="table-container">

            <div className="table-title">
              Ranked Polymer Materials
            </div>

            <table>

              <thead>

                <tr>

                  <th>
                    Rank
                  </th>

                  <th>
                    Polymer ID
                  </th>

                  <th>
                    MCDM Score
                  </th>

                  <th>
                    Performance
                  </th>

                </tr>

              </thead>

              <tbody>

                {recommendations.map(
                  (material, index) => (

                    <Fragment
                      key={`${material.polymer_id}-${index}`}
                    >

                      <tr
                        className="clickable-result-row"
                        onClick={() =>
                          setExpandedPolymer(
                            expandedPolymer === material.polymer_id
                              ? null
                              : material.polymer_id
                          )
                        }
                      >

                        <td>
                          <span className="rank-badge">
                            #{material.rank}
                          </span>
                        </td>

                        <td>
                          <strong>
                            {polymers.find(
                              (polymer) =>
                                polymer.Polymer_ID === material.polymer_id
                            )?.Polymer_Name || material.polymer_id}
                          </strong>
                          <small className="polymer-id-subtext">
                            {material.polymer_id}
                          </small>
                        </td>

                        <td>
                          <strong className="score">
                            {Number(material.mcdm_score || 0).toFixed(4)}
                          </strong>
                        </td>

                        <td>
                          <div className="score-bar-container">
                            <div className="score-bar">
                              <div
                                className="score-fill"
                                style={{
                                  width: `${
                                    Number(material.mcdm_score || 0) * 100
                                  }%`,
                                }}
                              ></div>
                            </div>
                            <span>
                              {(Number(material.mcdm_score || 0) * 100).toFixed(1)}%
                            </span>
                            <span className="details-hint">
                              {expandedPolymer === material.polymer_id ? "Hide" : "Details"}
                            </span>
                          </div>
                        </td>

                      </tr>

                      {expandedPolymer === material.polymer_id && (
                        <tr key={`${material.polymer_id}-${index}-details`}>
                          <td colSpan="4">
                            <PolymerDetailPanel
                              material={material}
                              polymer={polymers.find(
                                (polymer) =>
                                  polymer.Polymer_ID === material.polymer_id
                              )}
                            />
                          </td>
                        </tr>
                      )}

                    </Fragment>

                  )
                )}

              </tbody>

            </table>

          </div>


          {/* ENGINEERING SUITABILITY ASSESSMENT */}

          <EngineeringSuitabilityAssessment
            material={recommendations[0]}
            polymers={polymers}
          />


          {/* METHOD */}

          <div className="explanation-card">

            <div className="explanation-icon">
              💡
            </div>

            <div>

              <h3>
                How the recommendation works
              </h3>

              <p>
                Materials are evaluated against the selected
                engineering requirements. Mandatory constraints,
                when specified, are checked first. Eligible
                materials are then compared using normalized
                criterion scores and Multi-Criteria Decision-Making
                (MCDM) to produce the final ranking.
              </p>

            </div>

          </div>

        </section>

      )}

    </main>

  );
}


// ============================================================
// CUSTOM PAGE PLACEHOLDER
// ============================================================

// ============================================================
// CUSTOM RECOMMENDATION PAGE
// ============================================================

const getDefaultUnit = (propertyName) => {
  const units = {
    Density: "g/cm³",
    Tensile_Strength: "MPa",
    Tensile_Modulus: "MPa",
    Impact_Strength: "kJ/m²",
    Max_Service_Temperature: "°C",
    Melting_or_Softening_Temperature: "°C",
    Water_Absorption: "%",
  };

  return units[propertyName] || "";
};


const getPropertyDisplayName = (propertyName) => {
  const displayNames = {
    Chemical_Resistance: "Chemical Resistance",
    Cost_Category: "Cost Category",
    Density: "Density (g/cm³)",
    Heat_Resistance: "Heat Resistance",
    Impact_Strength: "Impact Strength (kJ/m²)",
    Injection_Molding_Suitability: "Injection Molding Suitability",
    Max_Service_Temperature: "Max Service Temperature (°C)",
    Melting_or_Softening_Temperature:
      "Melting / Softening Temperature (°C)",
    Optical_Transparency: "Optical Transparency",
    Tensile_Modulus: "Tensile Modulus (MPa)",
    Tensile_Strength: "Tensile Strength (MPa)",
    UV_Resistance: "UV Resistance",
    Water_Absorption: "Water Absorption (%)",
    Wear_Resistance: "Wear Resistance",
  };

  return displayNames[propertyName] || propertyName;
};

function CustomPage() {

  const [properties, setProperties] = useState([]);

  const [polymers, setPolymers] = useState([]);

  const [expandedPolymer, setExpandedPolymer] = useState(null);

  const [requirements, setRequirements] = useState([
    {
      property_name: "",
      required_value: "",
      required_unit: "",
      requirement_level: "High",
      weight: 1,
      hard_constraint: "No",
    },
  ]);

  const [applicationName, setApplicationName] = useState("");

  const [topN, setTopN] = useState(5);

  const [recommendations, setRecommendations] = useState([]);

  const [applicationResult, setApplicationResult] = useState("");

  const [totalEligible, setTotalEligible] = useState(0);

  const [rejectedCount, setRejectedCount] = useState(0);

  const [engineeringExplanation, setEngineeringExplanation] =
    useState(null);

  const [loadingProperties, setLoadingProperties] =
    useState(true);

  const [loadingRecommendation, setLoadingRecommendation] =
    useState(false);

  const [error, setError] = useState("");

  const [success, setSuccess] = useState("");


  // ==========================================================
  // PROPERTY TYPES
  // ==========================================================

  const categoricalProperties = [
    "Chemical_Resistance",
    "Wear_Resistance",
    "UV_Resistance",
    "Heat_Resistance",
    "Optical_Transparency",
    "Cost_Category",
    "Injection_Molding_Suitability",
  ];


  const propertyOptions = {
    Chemical_Resistance: [
      "Low",
      "Medium",
      "High",
    ],

    Wear_Resistance: [
      "Low",
      "Medium",
      "High",
    ],

    UV_Resistance: [
      "Low",
      "Medium",
      "High",
    ],

    Heat_Resistance: [
      "Low",
      "Medium",
      "High",
    ],

    Optical_Transparency: [
      "Low",
      "Medium",
      "High",
    ],

    Cost_Category: [
      "Low",
      "Medium",
      "High",
    ],

    Injection_Molding_Suitability: [
      "Low",
      "Medium",
      "High",
    ],
  };


  const isCategoricalProperty = (propertyName) => {

    return categoricalProperties.includes(
      propertyName
    );

  };


  // ==========================================================
  // LOAD PROPERTIES
  // ==========================================================

  useEffect(() => {

    loadProperties();
    loadPolymers();

  }, []);


  const loadPolymers = async () => {

    try {

      const data = await getCachedResource("polymers", "/polymers");
      setPolymers(data.polymers || []);

    } catch (err) {

      console.error(err);

    }

  };


  const loadProperties = async () => {

    try {

      setLoadingProperties(true);

      setError("");

      const data = await getCachedResource(
        "properties",
        "/properties"
      );

      setProperties(
        data.properties || []
      );

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load supported properties."
      );

    } finally {

      setLoadingProperties(false);

    }

  };


  // ==========================================================
  // ADD REQUIREMENT
  // ==========================================================

  const addRequirement = () => {

    setRequirements((currentRequirements) => [
      ...currentRequirements,
      {
        property_name: "",
        required_value: "",
        required_unit: "",
        requirement_level: "High",
        weight: 1,
        hard_constraint: "No",
      },
    ]);

  };


  // ==========================================================
  // REMOVE REQUIREMENT
  // ==========================================================

  const removeRequirement = (index) => {

    setRequirements((currentRequirements) => {
      if (currentRequirements.length === 1) {
        return currentRequirements;
      }

      return currentRequirements.filter(
        (_, requirementIndex) =>
          requirementIndex !== index
      );
    });

  };


  // ==========================================================
  // UPDATE REQUIREMENT
  // ==========================================================

  const updateRequirement = (
    index,
    field,
    value
  ) => {

    const updatedRequirements =
      [...requirements];

    updatedRequirements[index] = {
      ...updatedRequirements[index],
      [field]: value,
    };

    // Reset requirement fields and apply the property's default unit
    if (field === "property_name") {

      updatedRequirements[index].required_value = "";
      updatedRequirements[index].required_unit = getDefaultUnit(value);
    }

    setRequirements(
      updatedRequirements
    );

  };


  // ==========================================================
  // INTERNAL DECISION WEIGHTS
  // ==========================================================
  // Decision weights are handled internally and are not shown
  // to the user. Selected requirements receive equal weight.
  const getInternalWeights = (count) => {
    if (count <= 0) return [];

    const baseWeight = Math.floor((100 / count) * 100) / 100;
    const weights = Array(count).fill(baseWeight);
    const usedWeight = baseWeight * count;

    weights[count - 1] = Number(
      (baseWeight + (100 - usedWeight)).toFixed(2)
    );

    return weights;
  };


  // ==========================================================
  // VALIDATE REQUIREMENTS
  // ==========================================================

  const validateRequirements = () => {

    if (!applicationName.trim()) {

      return "Please enter an application name.";

    }


    if (requirements.length === 0) {

      return "Please add at least one requirement.";

    }


    const selectedProperties =
      requirements.map(
        (requirement) =>
          requirement.property_name
      );


    if (
      selectedProperties.some(
        (property) => !property
      )
    ) {

      return "Please select a property for every requirement.";

    }


    const duplicateProperties =
      selectedProperties.filter(
        (property, index) =>
          selectedProperties.indexOf(property) !== index
      );


    if (duplicateProperties.length > 0) {

      return "Each property can only be selected once.";

    }


    const missingValues =
      requirements.some(
        (requirement) =>
          requirement.required_value === "" ||
          requirement.required_value === null
      );


    if (missingValues) {

      return "Please enter a required value for every property.";

    }


    return null;

  };


  // ==========================================================
  // GENERATE CUSTOM RECOMMENDATION
  // ==========================================================

  const handleCustomRecommendation =
    async () => {

      setError("");
      setSuccess("");

      const validationError =
        validateRequirements();

      if (validationError) {

        setError(validationError);

        return;

      }


      try {

        setLoadingRecommendation(true);


        const formattedRequirements =
          requirements.map(
            (requirement, index) => {

              let requiredValue =
                requirement.required_value;

              // Convert numeric values to numbers
              if (
                !isCategoricalProperty(
                  requirement.property_name
                )
              ) {

                requiredValue =
                  Number(requiredValue);

              }

              return {
                property_name:
                  requirement.property_name,

                required_value:
                  requiredValue,

                required_unit:
                  requirement.required_unit,

                requirement_level:
                  requirement.requirement_level,

                // Internal weight: not exposed in the UI.
                weight:
                  getInternalWeights(requirements.length)[index],

                hard_constraint:
                  requirement.hard_constraint,
              };

            }
          );


        const response = await api.post(
          "/recommend/custom",
          {
            application_name:
              applicationName.trim(),

            requirements:
              formattedRequirements,

            top_n:
              Number(topN),
          }
        );


        const data =
          response.data;


        setApplicationResult(
          data.application_name
        );

        const recommendationResults =
          data.recommendations || [];

        setRecommendations(
          recommendationResults
        );

        setTotalEligible(
          data.total_eligible
        );

        setRejectedCount(
          data.rejected_count
        );

        saveChatContext({
          type: "custom",
          history_id: data.history_id,
          analysis_id: data.analysis_id || null,
          application_name: data.application_name,
          total_eligible: data.total_eligible,
          rejected_count: data.rejected_count,
          requirements: formattedRequirements,
          recommendations: recommendationResults.slice(0, 10),
          materials: recommendationResults.slice(0, 10).map((material) => {
            const polymer = polymers.find(
              (item) => item.Polymer_ID === material.polymer_id
            );

            return {
              polymer_id: material.polymer_id,
              polymer_name: polymer?.Polymer_Name || "",
              polymer_family: polymer?.Polymer_Family || "",
              material_type: polymer?.Material_Type || "",
              manufacturer: polymer?.Manufacturer || "",
              grade: polymer?.Grade || "",
            };
          }),
        });


        setSuccess(
          "Custom recommendation generated successfully."
        );


        // Scroll to results
        setTimeout(() => {

          document
            .getElementById(
              "custom-results"
            )
            ?.scrollIntoView({
              behavior: "smooth",
            });

        }, 100);

      } catch (err) {

        console.error(err);

        setError(
          getApiErrorMessage(
            err,
            "Custom recommendation failed."
          )
        );

      } finally {

        setLoadingRecommendation(false);

      }

    };


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <main className="main-container">

      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <section className="page-header">

        <span className="section-label">
          CUSTOM MATERIAL SELECTION
        </span>

        <h2>
          Build your Own Requirements
        </h2>

        <p>
          Define the engineering requirements that matter
          for your application. The system will evaluate
          the polymer database using hard constraints and
          MCDM-based material ranking.
        </p>

      </section>


      {/* ======================================================
          CUSTOM FORM
      ====================================================== */}

      <section className="custom-builder-card">

        {/* APPLICATION NAME */}

        <div className="custom-top-grid">

          <div className="form-group">

            <label>
              Application / Component Name
            </label>

            <input
              type="text"
              value={applicationName}
              onChange={(event) =>
                setApplicationName(
                  event.target.value
                )
              }
              placeholder="e.g. High-Temperature Engineering Polymer Component"
            />

          </div>


          <div className="form-group">

            <label>
              Number of Recommendations
            </label>

            <select
              value={topN}
              onChange={(event) =>
                setTopN(
                  Number(event.target.value)
                )
              }
            >

              <option value={3}>
                Top 3
              </option>

              <option value={5}>
                Top 5
              </option>

              <option value={10}>
                Top 10
              </option>

            </select>

          </div>

        </div>


        {/* REQUIREMENTS HEADER */}

        <div className="requirements-header">

          <div>

            <h3>
              Selection Criteria
            </h3>

            <p>
              Enter the required properties and values for
              your application.
            </p>

          </div>



        </div>


        {/* LOADING */}

        {loadingProperties && (

          <div className="loading-card">
            Loading supported properties...
          </div>

        )}


        {/* REQUIREMENT ROWS */}

        {!loadingProperties && (

          <div className="requirements-list">

            {requirements.map(
              (requirement, index) => (

                <div
                  className="requirement-row"
                  key={index}
                >

                  {/* PROPERTY */}

                  <div className="form-group">

                    <label>
                      Properties
                    </label>

                    <select
                      value={
                        requirement.property_name
                      }
                      onChange={(event) =>
                        updateRequirement(
                          index,
                          "property_name",
                          event.target.value
                        )
                      }
                    >

                      <option value="">
                        Select property
                      </option>

                      {properties.map(
                        (property) => (

                          <option
                            key={
                              property.property_name
                            }
                            value={
                              property.property_name
                            }
                          >
                            {getPropertyDisplayName(
                              property.property_name
                            )}
                          </option>

                        )
                      )}

                    </select>

                  </div>


                  {/* REQUIRED VALUE */}

                  <div className="form-group">

                    <label>
                      Required Value
                    </label>

                    {isCategoricalProperty(
                      requirement.property_name
                    ) ? (

                      <select
                        value={
                          requirement.required_value
                        }
                        onChange={(event) =>
                          updateRequirement(
                            index,
                            "required_value",
                            event.target.value
                          )
                        }
                      >

                        <option value="">
                          Select value
                        </option>

                        {(
                          propertyOptions[
                            requirement.property_name
                          ] || []
                        ).map(
                          (option) => (

                            <option
                              key={option}
                              value={option}
                            >
                              {option}
                            </option>

                          )
                        )}

                      </select>

                    ) : (

                      <input
                        type="number"
                        step="any"
                        value={
                          requirement.required_value
                        }
                        onChange={(event) =>
                          updateRequirement(
                            index,
                            "required_value",
                            event.target.value
                          )
                        }
                        placeholder="Enter value"
                      />

                    )}

                  </div>


                  {/* UNIT */}

                  <div className="form-group">

                    <label>
                      Unit
                    </label>

                    <input
                      type="text"
                      value={
                        requirement.required_unit
                      }
                      onChange={(event) =>
                        updateRequirement(
                          index,
                          "required_unit",
                          event.target.value
                        )
                      }
                      placeholder={
                        getDefaultUnit(requirement.property_name) ||
                        "°C, MPa, %, etc."
                      }
                      disabled={isCategoricalProperty(
                        requirement.property_name
                      )}
                    />

                  </div>


                  {/* HARD CONSTRAINT */}

                  <div className="form-group">

                    <label>
                      Constraint Type
                    </label>

                    <select
                      value={
                        requirement.hard_constraint
                      }
                      onChange={(event) =>
                        updateRequirement(
                          index,
                          "hard_constraint",
                          event.target.value
                        )
                      }
                    >

                      <option value="No">
                        Soft
                      </option>

                      <option value="Yes">
                        Hard
                      </option>

                    </select>

                  </div>


                  {/* REMOVE */}

                  <button
                    type="button"
                    className="remove-button"
                    onClick={() =>
                      removeRequirement(index)
                    }
                    disabled={
                      requirements.length === 1
                    }
                    title="Remove requirement"
                  >
                    ×
                  </button>

                </div>

              )
            )}

          </div>

        )}


        {/* ADD REQUIREMENT */}

        <button
          type="button"
          className="secondary-button"
          onClick={addRequirement}
          disabled={
            loadingProperties ||
            requirements.length >= properties.length
          }
        >
          + Add Requirement
        </button>


        {/* GENERATE */}

        <div className="custom-actions">

          <button
            className="primary-button"
            onClick={
              handleCustomRecommendation
            }
            disabled={
              loadingProperties ||
              loadingRecommendation
            }
          >

            {loadingRecommendation
              ? "Calculating..."
              : "Generate Recommendation"}

            {!loadingRecommendation && (
              <span>→</span>
            )}

          </button>

        </div>

      </section>


      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (

        <div className="error-message">

          <strong>Error:</strong>{" "}
          {error}

        </div>

      )}


      {/* ======================================================
          SUCCESS
      ====================================================== */}

      {success && (

        <div className="success-message">

          ✓ {success}

        </div>

      )}


      {/* ======================================================
          RESULTS
      ====================================================== */}

      {recommendations.length > 0 && (

        <section
          className="results-section"
          id="custom-results"
        >

          <div className="page-header result-heading">

            <span className="section-label">
              CUSTOM RECOMMENDATION RESULTS
            </span>

            <h2>
              {applicationResult}
            </h2>

          </div>


          {/* SUMMARY */}

          <div className="summary-grid">

            <div className="summary-card">

              <span className="summary-label">
                Eligible Materials
              </span>

              <strong>
                {totalEligible}
              </strong>

            </div>


            <div className="summary-card">

              <span className="summary-label">
                Rejected Materials
              </span>

              <strong>
                {rejectedCount}
              </strong>

            </div>


            <div className="summary-card">

              <span className="summary-label">
                Recommendations
              </span>

              <strong>
                {recommendations.length}
              </strong>

            </div>

          </div>


          {/* RECOMMENDATION OVERVIEW */}

          <RecommendationOverview
            recommendations={recommendations}
            polymers={polymers}
          />


          {/* RESULTS TABLE */}

          <div className="table-container">

            <div className="table-title">
              Ranked Polymer Materials
            </div>

            <table>

              <thead>

                <tr>

                  <th>
                    Rank
                  </th>

                  <th>
                    Polymer ID
                  </th>

                  <th>
                    MCDM Score
                  </th>

                  <th>
                    Performance
                  </th>

                </tr>

              </thead>

              <tbody>

                {recommendations.map(
                  (material, index) => (

                    <Fragment
                      key={`${material.polymer_id}-${index}`}
                    >

                      <tr
                        className="clickable-result-row"
                        onClick={() =>
                          setExpandedPolymer(
                            expandedPolymer === material.polymer_id
                              ? null
                              : material.polymer_id
                          )
                        }
                      >

                        <td>
                          <span className="rank-badge">
                            #{material.rank}
                          </span>
                        </td>

                        <td>
                          <strong>
                            {polymers.find(
                              (polymer) =>
                                polymer.Polymer_ID === material.polymer_id
                            )?.Polymer_Name || material.polymer_id}
                          </strong>
                          <small className="polymer-id-subtext">
                            {material.polymer_id}
                          </small>
                        </td>

                        <td>
                          <strong className="score">
                            {Number(material.mcdm_score || 0).toFixed(4)}
                          </strong>
                        </td>

                        <td>
                          <div className="score-bar-container">
                            <div className="score-bar">
                              <div
                                className="score-fill"
                                style={{
                                  width: `${
                                    Number(material.mcdm_score || 0) * 100
                                  }%`,
                                }}
                              ></div>
                            </div>
                            <span>
                              {(Number(material.mcdm_score || 0) * 100).toFixed(1)}%
                            </span>
                            <span className="details-hint">
                              {expandedPolymer === material.polymer_id ? "Hide" : "Details"}
                            </span>
                          </div>
                        </td>

                      </tr>

                      {expandedPolymer === material.polymer_id && (
                        <tr key={`${material.polymer_id}-${index}-details`}>
                          <td colSpan="4">
                            <PolymerDetailPanel
                              material={material}
                              polymer={polymers.find(
                                (polymer) =>
                                  polymer.Polymer_ID === material.polymer_id
                              )}
                            />
                          </td>
                        </tr>
                      )}

                    </Fragment>

                  )
                )}

              </tbody>

            </table>

          </div>


          {/* ENGINEERING SUITABILITY ASSESSMENT */}

          <EngineeringSuitabilityAssessment
            material={recommendations[0]}
            polymers={polymers}
          />


          {/* EXPLANATION */}

          <div className="explanation-card">

            <div className="explanation-icon">
              💡
            </div>

            <div>

              <h3>
                Decision methodology
              </h3>

              <p>
                The system first evaluates hard constraints
                and removes materials that do not satisfy
                mandatory requirements. The remaining
                materials are scored using normalized
                criteria and weighted Multi-Criteria
                Decision-Making (MCDM).
              </p>

            </div>

          </div>

        </section>

      )}

    </main>

  );
}

// ============================================================
// ============================================================
// HISTORY REPORT EXPORT
// ============================================================

const escapeHtml = (value) => {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

const exportHistoryReport = (record, polymers) => {
  const recommendations = record.recommendations || [];

  const getPolymer = (polymerId) =>
    polymers.find((item) => item.Polymer_ID === polymerId);

  const getFamily = (polymerId) => {
    const polymer = getPolymer(polymerId);
    return (
      polymer?.Polymer_Family ||
      polymer?.Polymer_Type ||
      "Polymer Material"
    );
  };

  const getName = (polymerId) => {
    const polymer = getPolymer(polymerId);
    return (
      polymer?.Polymer_Name ||
      polymer?.Grade ||
      polymerId ||
      "Unknown Material"
    );
  };

  const requirements = record.requirements || [];

  const requirementRows = requirements.length
    ? requirements
        .map((item) => `
          <tr>
            <td>${escapeHtml(
              item.Property_Name || item.property_name || "—"
            )}</td>
            <td>${escapeHtml(
              item.Required_Value ?? item.required_value ?? "—"
            )}</td>
            <td>${escapeHtml(
              item.Required_Unit ?? item.required_unit ?? "—"
            )}</td>
            <td>${escapeHtml(
              (item.Hard_Constraint ?? item.hard_constraint) ? "Hard" : "Soft"
            )}</td>
          </tr>
        `)
        .join("")
    : `<tr><td colspan="4">Requirement details were not stored for this analysis.</td></tr>`;

  const rankingRows = recommendations
    .map((material) => `
      <tr>
        <td>#${escapeHtml(material.rank)}</td>
        <td>${escapeHtml(getFamily(material.polymer_id))}</td>
        <td>${escapeHtml(getName(material.polymer_id))}</td>
        <td>${escapeHtml(material.polymer_id)}</td>
        <td>${Number(material.mcdm_score || 0).toFixed(4)}</td>
      </tr>
    `)
    .join("");

  const top = recommendations[0];
  const explanation = top?.engineering_explanation || {};
  const whySuitable =
    explanation.why_this_material_is_suitable ||
    explanation.final_summary ||
    "The recommendation is based on the combined performance of the selected engineering criteria using weighted MCDM.";
  const keyObservation =
    explanation.key_observation ||
    "The final recommendation reflects the combined performance of the selected engineering criteria.";

  const reportWindow = window.open(
    "",
    "_blank",
    "width=1000,height=800"
  );

  if (!reportWindow) {
    alert(
      "Please allow pop-ups to export the analysis report."
    );
    return;
  }

  reportWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>Material Selection Analysis Report</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #172a46;
            line-height: 1.5;
          }
          h1 {
            margin-bottom: 4px;
            font-size: 25px;
          }
          h2 {
            margin-top: 28px;
            font-size: 18px;
            border-bottom: 1px solid #dce3ec;
            padding-bottom: 8px;
          }
          h3 {
            margin: 0 0 12px;
            font-size: 15px;
          }
          .subtitle {
            color: #6c7b90;
            margin-bottom: 24px;
          }
          .summary {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin: 20px 0;
          }
          .box {
            padding: 14px;
            border: 1px solid #dce3ec;
            border-radius: 8px;
          }
          .label {
            display: block;
            font-size: 11px;
            color: #718096;
            text-transform: uppercase;
            font-weight: bold;
          }
          .value {
            display: block;
            margin-top: 4px;
            font-size: 17px;
            font-weight: bold;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
          }
          th, td {
            border: 1px solid #dce3ec;
            padding: 9px;
            text-align: left;
            font-size: 12px;
          }
          th {
            background: #f3f6fa;
          }
          .top, .rationale, .observation {
            padding: 16px;
            border: 1px solid #dce3ec;
            border-radius: 8px;
            margin-top: 12px;
          }
          .rationale p, .observation p {
            margin: 0;
          }
          .footer {
            margin-top: 36px;
            font-size: 11px;
            color: #7a8798;
          }
          @media print {
            body { margin: 20px; }
          }
        </style>
      </head>
      <body>
        <h1>Intelligent Polymer Material Selection System</h1>
        <div class="subtitle">Material Selection Analysis Report</div>

        <div class="summary">
          <div class="box">
            <span class="label">Application</span>
            <span class="value">${escapeHtml(
              record.application_name || "—"
            )}</span>
          </div>
          <div class="box">
            <span class="label">Analysis Type</span>
            <span class="value">${escapeHtml(
              record.analysis_id ? "Predefined" : "Custom"
            )}</span>
          </div>
          <div class="box">
            <span class="label">Analysis ID</span>
            <span class="value">${escapeHtml(
              record.analysis_id || "Custom"
            )}</span>
          </div>
          <div class="box">
            <span class="label">Generated</span>
            <span class="value">${escapeHtml(
              record.created_at
                ? parseApiDate(record.created_at).toLocaleString("en-IN", {
                    timeZone: HISTORY_TIME_ZONE,
                  })
                : "—"
            )}</span>
          </div>
          <div class="box">
            <span class="label">Eligible Materials</span>
            <span class="value">${escapeHtml(
              record.total_eligible ?? "—"
            )}</span>
          </div>
          <div class="box">
            <span class="label">Rejected Materials</span>
            <span class="value">${escapeHtml(
              record.rejected_count ?? "—"
            )}</span>
          </div>
        </div>

        <h2>Selection Criteria</h2>
        <table>
          <thead>
            <tr>
              <th>Property</th>
              <th>Required Value</th>
              <th>Unit</th>
              <th>Constraint</th>
            </tr>
          </thead>
          <tbody>${requirementRows}</tbody>
        </table>

        <h2>Material Ranking</h2>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Polymer Family</th>
              <th>Material / Grade</th>
              <th>Polymer ID</th>
              <th>MCDM Score</th>
            </tr>
          </thead>
          <tbody>${rankingRows ||
            `<tr><td colspan="5">No recommendation results stored.</td></tr>`}</tbody>
        </table>

        ${
          top
            ? `
              <h2>Engineering Suitability Assessment</h2>
              <div class="top">
                <strong>${escapeHtml(getName(top.polymer_id))}</strong><br />
                ${escapeHtml(top.polymer_id)} • Rank #${escapeHtml(top.rank)}<br />
                MCDM Score: ${Number(top.mcdm_score || 0).toFixed(4)}
              </div>

              <div class="rationale">
                <h3>Material Selection Rationale</h3>
                <p>${escapeHtml(whySuitable)}</p>
              </div>

              <div class="observation">
                <h3>Key Observation</h3>
                <p>${escapeHtml(keyObservation)}</p>
              </div>
            `
            : ""
        }

        <div class="footer">
          Generated by the Intelligent Polymer Material Selection and
          Recommendation System.
        </div>
      </body>
    </html>
  `);

  reportWindow.document.close();
  reportWindow.focus();

  setTimeout(() => {
    reportWindow.print();
  }, 400);
};


// HISTORY PAGE
// ============================================================

function HistoryPage() {

  const [history, setHistory] = useState([]);
  const [polymers, setPolymers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [historyType, setHistoryType] = useState("All");
  const [expandedHistory, setExpandedHistory] = useState(null);
  const [deletingHistory, setDeletingHistory] = useState(null);

  useEffect(() => {
    loadHistory();
    loadPolymers();
  }, []);

  const loadPolymers = async () => {
    try {
      const data = await getCachedResource("polymers", "/polymers");
      setPolymers(data.polymers || []);
    } catch (err) {
      console.error("Unable to load polymer master data:", err);
    }
  };

  const getPolymerData = (polymerId) => {
    return polymers.find(
      (item) => item.Polymer_ID === polymerId
    );
  };

  const getPolymerFamily = (polymerId) => {
    const polymer = getPolymerData(polymerId);

    return (
      polymer?.Polymer_Family ||
      polymer?.Polymer_Type ||
      "Polymer Material"
    );
  };

  const getPolymerGrade = (polymerId) => {
    const polymer = getPolymerData(polymerId);

    return (
      polymer?.Polymer_Name ||
      polymer?.Grade ||
      polymerId ||
      "Unknown Material"
    );
  };

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/history");
      setHistory(response.data.history || []);

    } catch (err) {
      console.error(err);
      setError("Unable to load recommendation history.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteHistory = async (record) => {
    const historyId = record.history_id;

    if (!historyId) {
      setError(
        "This history record does not have a database ID. Please refresh the page and try again."
      );
      return;
    }

    const confirmed = window.confirm(
      `Delete this analysis history record?\n\n${record.application_name || "Unnamed Analysis"}\n\nThis action cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingHistory(historyId);
      setError("");

      await api.delete(`/history/${historyId}`);

      if (
        expandedHistory &&
        expandedHistory === `${record.created_at}`
      ) {
        setExpandedHistory(null);
      }

      // Update the current page immediately after the server
      // confirms deletion; no second GET /history is needed.
      setHistory((currentHistory) =>
        currentHistory.filter(
          (item) => item.history_id !== historyId
        )
      );

    } catch (err) {
      console.error(err);

      setError(
        getApiErrorMessage(
          err,
          "Unable to delete this analysis history record."
        )
      );
    } finally {
      setDeletingHistory(null);
    }
  };


  const formatDate = (value) => {
    if (!value) return "Date unavailable";

    const date = parseApiDate(value);

    if (!date || Number.isNaN(date.getTime())) {
      return "Date unavailable";
    }

    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: HISTORY_TIME_ZONE,
    });
  };

  const getRecordType = (record) => {
    return record.analysis_id ? "Predefined" : "Custom";
  };

  const filteredHistory = history.filter((record) => {

    const applicationName =
      String(record.application_name || "").toLowerCase();

    const analysisId =
      String(record.analysis_id || "").toLowerCase();

    const query = searchTerm.trim().toLowerCase();

    const matchesSearch =
      !query ||
      applicationName.includes(query) ||
      analysisId.includes(query);

    const matchesType =
      historyType === "All" ||
      getRecordType(record) === historyType;

    return matchesSearch && matchesType;
  });

  const totalAnalyses = history.length;

  const predefinedCount = history.filter(
    (record) => Boolean(record.analysis_id)
  ).length;

  const customCount = totalAnalyses - predefinedCount;

  return (

    <main className="main-container">

      {/* PAGE HEADER */}
      <section className="page-header">

        <span className="section-label">
          RECOMMENDATION HISTORY
        </span>

        <h2>
          Analysis History
        </h2>

        <p>
          Review previous material-selection analyses,
          recommendation results, and decision scores.
        </p>

      </section>


      {error && (
        <div className="error-message">
          <strong>Error:</strong>{" "}
          {error}
        </div>
      )}


      {/* HISTORY OVERVIEW */}
      {!loading && history.length > 0 && (

        <section className="history-overview-grid">

          <div className="history-overview-card">
            <span>Total Analyses</span>
            <strong>{totalAnalyses}</strong>
            <small>Saved recommendation runs</small>
          </div>

          <div className="history-overview-card">
            <span>Predefined Analyses</span>
            <strong>{predefinedCount}</strong>
            <small>Application scenarios</small>
          </div>

          <div className="history-overview-card">
            <span>Custom Analyses</span>
            <strong>{customCount}</strong>
            <small>User-defined requirements</small>
          </div>

        </section>

      )}


      {/* FILTERS */}
      {!loading && history.length > 0 && (

        <section className="history-controls-card">

          <div className="history-search-group">

            <label>
              Search Analyses
            </label>

            <input
              type="text"
              value={searchTerm}
              onChange={(event) =>
                setSearchTerm(event.target.value)
              }
              placeholder="Search by application name or analysis ID"
            />

          </div>


          <div className="history-filter-group">

            <label>
              Analysis Type
            </label>

            <select
              value={historyType}
              onChange={(event) =>
                setHistoryType(event.target.value)
              }
            >
              <option value="All">
                All Analyses
              </option>

              <option value="Predefined">
                Predefined
              </option>

              <option value="Custom">
                Custom
              </option>
            </select>

          </div>


          <button
            type="button"
            className="secondary-button history-refresh-button"
            onClick={loadHistory}
            disabled={loading}
          >
            ↻ Refresh
          </button>

        </section>

      )}


      {loading && (
        <div className="loading-card">
          Loading recommendation history...
        </div>
      )}


      {!loading && history.length === 0 && (

        <div className="empty-state">

          <div className="empty-icon">
            📋
          </div>

          <h3>
            No Analysis History
          </h3>

          <p>
            Run a predefined or custom recommendation
            to create your first analysis record.
          </p>

        </div>

      )}


      {!loading && history.length > 0 &&
       filteredHistory.length === 0 && (

        <div className="empty-state">

          <div className="empty-icon">
            🔎
          </div>

          <h3>
            No Matching Analyses
          </h3>

          <p>
            Try a different application name, analysis ID,
            or analysis type.
          </p>

        </div>

      )}


      {/* HISTORY LIST */}
      {!loading && filteredHistory.length > 0 && (

        <section className="history-list">

          <div className="history-list-heading">

            <div>
              <span className="section-label">
                SAVED ANALYSES
              </span>

              <h3>
                {filteredHistory.length}{" "}
                {filteredHistory.length === 1
                  ? "Analysis"
                  : "Analyses"}
              </h3>
            </div>

            <span className="history-result-count">
              Showing {filteredHistory.length} of {history.length}
            </span>

          </div>


          {filteredHistory.map((record, index) => {

            const recommendations =
              record.recommendations || [];

            const topMaterial =
              recommendations.length > 0
                ? recommendations[0]
                : null;

            const isExpanded =
              expandedHistory ===
              `${record.created_at}-${index}`;

            const recordKey =
              `${record.created_at}-${index}`;

            return (

              <article
                className={`history-card ${
                  isExpanded
                    ? "history-card-expanded"
                    : ""
                }`}
                key={recordKey}
              >

                {/* CARD HEADER */}
                <div className="history-card-header">

                  <div className="history-title-block">

                    <div className="history-badges">

                      <span className="history-id">
                        {record.analysis_id || "CUSTOM"}
                      </span>

                      <span
                        className={`history-type-badge ${
                          record.analysis_id
                            ? "predefined"
                            : "custom"
                        }`}
                      >
                        {getRecordType(record)}
                      </span>

                    </div>

                    <h3>
                      {record.application_name ||
                        "Unnamed Application"}
                    </h3>

                    <span className="history-date">
                      {formatDate(record.created_at)}
                    </span>

                  </div>


                  <div className="history-card-actions">

                    <button
                      type="button"
                      className="history-view-button"
                      onClick={() =>
                        setExpandedHistory(
                          isExpanded ? null : recordKey
                        )
                      }
                    >
                      {isExpanded
                        ? "Hide Details"
                        : "View Analysis"}
                      <span>
                        {isExpanded ? "↑" : "→"}
                      </span>
                    </button>

                    <button
                      type="button"
                      className="history-export-button"
                      onClick={() =>
                        exportHistoryReport(
                          record,
                          polymers
                        )
                      }
                    >
                      Export Report
                    </button>

                    <button
                      type="button"
                      className="history-delete-button"
                      onClick={() =>
                        handleDeleteHistory(record)
                      }
                      disabled={
                        deletingHistory ===
                        record.history_id
                      }
                    >
                      {deletingHistory ===
                      record.history_id
                        ? "Deleting..."
                        : "Delete"}
                    </button>

                  </div>

                </div>


                {/* SUMMARY */}
                <div className="history-summary">

                  <div>
                    <span>Eligible Materials</span>
                    <strong>
                      {record.total_eligible ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Rejected Materials</span>
                    <strong>
                      {record.rejected_count ?? "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Recommendations</span>
                    <strong>
                      {recommendations.length}
                    </strong>
                  </div>

                  <div className="history-top-score">

                    <span>Top MCDM Score</span>

                    <strong>
                      {topMaterial
                        ? Number(
                            topMaterial.mcdm_score || 0
                          ).toFixed(4)
                        : "—"}
                    </strong>

                  </div>

                </div>


                {/* TOP MATERIAL */}
                {topMaterial && (

                  <div className="history-top-material">

                    <div>

                      <span>
                        TOP RECOMMENDED MATERIAL
                      </span>

                      <strong>
                        {getPolymerFamily(topMaterial.polymer_id)}
                      </strong>

                      <small className="history-top-grade">
                        {getPolymerGrade(topMaterial.polymer_id)}
                        {" • "}
                        {topMaterial.polymer_id}
                      </small>

                    </div>

                    <div className="history-top-rank">
                      Rank #{topMaterial.rank || 1}
                    </div>

                  </div>

                )}


                {/* EXPANDED DETAILS */}
                {isExpanded && (

                  <div className="history-expanded-details">

                    <div className="history-detail-section">

                      <h4>
                        Ranked Materials
                      </h4>

                      {recommendations.length > 0 ? (

                        <div className="history-ranked-list">

                          {recommendations.map(
                            (material, materialIndex) => {

                              const score =
                                Number(
                                  material.mcdm_score || 0
                                );

                              return (

                                <div
                                  className="history-ranked-item"
                                  key={`${material.polymer_id}-${materialIndex}`}
                                >

                                  <div className="history-ranked-name">

                                    <span className="rank-badge">
                                      #{material.rank}
                                    </span>

                                    <div>
                                      <strong>
                                        {getPolymerFamily(material.polymer_id)}
                                      </strong>

                                      <small>
                                        {getPolymerGrade(material.polymer_id)}
                                        {" • "}
                                        {material.polymer_id}
                                      </small>
                                    </div>

                                  </div>

                                  <div className="history-ranked-score">

                                    <div className="history-mini-bar">
                                      <div
                                        className="history-mini-fill"
                                        style={{
                                          width: `${Math.max(
                                            0,
                                            Math.min(
                                              100,
                                              score * 100
                                            )
                                          )}%`,
                                        }}
                                      />
                                    </div>

                                    <strong>
                                      {score.toFixed(4)}
                                    </strong>

                                  </div>

                                </div>

                              );
                            }
                          )}

                        </div>

                      ) : (

                        <p className="detail-empty">
                          No recommendation results were stored
                          for this analysis.
                        </p>

                      )}

                    </div>


                  </div>

                )}

              </article>

            );

          })}

        </section>

      )}

    </main>

  );
}


// ============================================================
// GROQ POLYMER ENGINEERING CHATBOT
// ============================================================

const renderChatMessage = (content) => {
  const text = String(content ?? "");
  const parts = text.split(/(\*\*[^*]+\*\*)/g);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index}>
          {part.slice(2, -2)}
        </strong>
      );
    }

    return <Fragment key={index}>{part}</Fragment>;
  });
};


function PolymerChatbot() {

  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [context, setContext] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I’m PolyGuide AI. I can explain the current polymer recommendation using the project’s MCDM results and polymer data. Ask me about the selected material, its properties, ranking, rejected materials, or MCDM calculation.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setContext(loadChatContext());
    }
  }, [isOpen]);

  useEffect(() => {
    setContext(null);
    setMessages([
      {
        role: "assistant",
        content: user
          ? "Hello! I’m PolyGuide AI. I can explain the current polymer recommendation using the project’s MCDM results and polymer data."
          : "Sign in to use PolyGuide AI with your private recommendation context.",
      },
    ]);
  }, [user?.user_id]);

  const sendMessage = async (presetMessage = null) => {
    const text = String(presetMessage ?? input).trim();

    if (!text || loading || !user) return;

    const activeContext = context || loadChatContext();
    const userMessage = { role: "user", content: text };
    const nextMessages = [...messages, userMessage];

    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const response = await api.post("/chat", {
        message: text,
        context: activeContext || {},
        history: nextMessages.slice(-8),
      });

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            response.data?.answer ||
            "I could not generate an answer.",
        },
      ]);
    } catch (error) {
      console.error("Chatbot error:", error);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: getApiErrorMessage(
            error,
            "The AI assistant is currently unavailable. Please make sure FastAPI is running and GROQ_API_KEY is configured."
          ),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: "assistant",
        content: user
          ? "Chat cleared. Ask me about the current polymer recommendation."
          : "Sign in to use PolyGuide AI with your private recommendation context.",
      },
    ]);
  };

  const hasRecommendation =
    Array.isArray(context?.recommendations) &&
    context.recommendations.length > 0;

  const topMaterialFamily =
    context?.materials?.[0]?.polymer_family ||
    context?.polymer_details?.[0]?.Polymer_Family ||
    "Polymer family unavailable";

  const quickQuestions = [
   
  ]

  return (
    <>
      <style>{`
        .polymer-chatbot-launcher {
          position: fixed;
          right: 24px;
          bottom: 24px;
          width: 58px;
          height: 58px;
          border: none;
          border-radius: 50%;
          background: #172b4d;
          color: #ffffff;
          font-size: 25px;
          cursor: pointer;
          box-shadow: 0 10px 28px rgba(23, 43, 77, 0.25);
          z-index: 9999;
        }

        .polymer-chatbot-window {
          position: fixed;
          right: 24px;
          bottom: 94px;
          width: min(390px, calc(100vw - 32px));
          height: min(590px, calc(100vh - 125px));
          background: #ffffff;
          border: 1px solid #dfe3eb;
          border-radius: 18px;
          box-shadow: 0 18px 55px rgba(23, 43, 77, 0.22);
          display: flex;
          flex-direction: column;
          overflow: hidden;
          z-index: 9999;
        }

        .polymer-chatbot-header {
          padding: 15px 17px;
          background: #172b4d;
          color: #ffffff;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 10px;
        }

        .polymer-chatbot-title {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .polymer-chatbot-title strong {
          display: block;
          font-size: 14px;
        }

        .polymer-chatbot-title small {
          display: block;
          margin-top: 2px;
          font-size: 11px;
          opacity: 0.78;
        }

        .polymer-chatbot-close {
          border: none;
          background: transparent;
          color: #ffffff;
          font-size: 21px;
          cursor: pointer;
        }

        .polymer-chatbot-context {
          margin: 10px 12px 0;
          padding: 9px 11px;
          border: 1px solid #e1e7ef;
          border-radius: 10px;
          background: #f7f9fc;
          color: #526174;
          font-size: 11px;
          line-height: 1.45;
        }

        .polymer-chatbot-context strong {
          color: #172b4d;
        }

        .polymer-chatbot-quick {
          padding: 9px 12px 0;
          display: flex;
          gap: 6px;
          overflow-x: auto;
        }

        .polymer-chatbot-quick button {
          flex: 0 0 auto;
          border: 1px solid #d8e0eb;
          background: #ffffff;
          color: #29415f;
          border-radius: 16px;
          padding: 6px 9px;
          font-size: 11px;
          cursor: pointer;
        }

        .polymer-chatbot-messages {
          flex: 1;
          overflow-y: auto;
          padding: 12px;
        }

        .polymer-chatbot-message {
          display: flex;
          margin-bottom: 10px;
        }

        .polymer-chatbot-message.user {
          justify-content: flex-end;
        }

        .polymer-chatbot-bubble {
          max-width: 86%;
          padding: 10px 12px;
          border-radius: 13px;
          font-size: 13px;
          line-height: 1.5;
          white-space: pre-wrap;
        }

        .polymer-chatbot-message.assistant .polymer-chatbot-bubble {
          background: #f0f4f9;
          color: #17365d;
          border-bottom-left-radius: 4px;
        }

        .polymer-chatbot-message.user .polymer-chatbot-bubble {
          background: #172b4d;
          color: #ffffff;
          border-bottom-right-radius: 4px;
        }

        .polymer-chatbot-input-area {
          border-top: 1px solid #e3e8ef;
          padding: 10px;
          background: #ffffff;
        }

        .polymer-chatbot-input-row {
          display: flex;
          gap: 7px;
          align-items: flex-end;
        }

        .polymer-chatbot-input {
          flex: 1;
          resize: none;
          min-height: 38px;
          max-height: 90px;
          border: 1px solid #ccd5e1;
          border-radius: 10px;
          padding: 9px 10px;
          font-family: inherit;
          font-size: 13px;
          outline: none;
          box-sizing: border-box;
        }

        .polymer-chatbot-send {
          border: none;
          border-radius: 10px;
          min-width: 42px;
          height: 38px;
          background: #172b4d;
          color: #ffffff;
          cursor: pointer;
          font-size: 17px;
        }

        .polymer-chatbot-send:disabled {
          opacity: 0.55;
          cursor: not-allowed;
        }

        .polymer-chatbot-bottom-row {
          margin-top: 6px;
          display: flex;
          justify-content: flex-end;
        }

        .polymer-chatbot-clear {
          border: none;
          background: transparent;
          color: #64748b;
          font-size: 11px;
          cursor: pointer;
        }
      `}</style>

      {!isOpen && (
        <button
          type="button"
          className="polymer-chatbot-launcher"
          onClick={() => setIsOpen(true)}
          aria-label="Open Polymer Engineering Assistant"
          title="Polymer Engineering Assistant"
        >
          🤖
        </button>
      )}

      {isOpen && (
        <div className="polymer-chatbot-window">
          <div className="polymer-chatbot-header">
            <div className="polymer-chatbot-title">
              <span>🤖</span>
              <div>
                <strong>PolyGuide AI</strong>
                <small>Intelligent Polymer Engineering Assistant</small>
              </div>
            </div>

            <button
              type="button"
              className="polymer-chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chatbot"
            >
              ×
            </button>
          </div>

          <div className="polymer-chatbot-context">
            {hasRecommendation ? (
              <>
                <strong>Current analysis:</strong>{" "}
                {context.application_name || "Selected application"}
                {context.analysis_id
                  ? ` • ${context.analysis_id}`
                  : ""}
                {context.recommendations?.[0]?.polymer_id
                  ? ` • Top material ${context.recommendations[0].polymer_id} - ${topMaterialFamily}`
                  : ""}
              </>
            ) : (
              <>
                <strong>No recommendation context yet.</strong> Run a
                predefined or custom recommendation first for project-specific
                answers.
              </>
            )}
          </div>

          <div className="polymer-chatbot-quick">
            {quickQuestions.map((question) => (
              <button
                type="button"
                key={question}
                onClick={() => sendMessage(question)}
                disabled={loading}
              >
                {question}
              </button>
            ))}
          </div>

          <div className="polymer-chatbot-messages">
            {messages.map((message, index) => (
              <div
                className={`polymer-chatbot-message ${message.role}`}
                key={`${message.role}-${index}`}
              >
                <div className="polymer-chatbot-bubble">
                  {renderChatMessage(message.content)}
                </div>
              </div>
            ))}

            {loading && (
              <div className="polymer-chatbot-message assistant">
                <div className="polymer-chatbot-bubble">
                  Thinking about the engineering data…
                </div>
              </div>
            )}
          </div>

          <div className="polymer-chatbot-input-area">
            <div className="polymer-chatbot-input-row">
              <textarea
                className="polymer-chatbot-input"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask about the recommendation..."
                rows={1}
                disabled={loading}
              />

              <button
                type="button"
                className="polymer-chatbot-send"
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                aria-label="Send message"
              >
                →
              </button>
            </div>

            <div className="polymer-chatbot-bottom-row">
              <button
                type="button"
                className="polymer-chatbot-clear"
                onClick={clearChat}
              >
                Clear chat
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}


// ============================================================
// APP
// ============================================================

function App() {

  return (

    <BrowserRouter>

      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/login" element={<AuthPage mode="login" />} />
            <Route path="/register" element={<AuthPage mode="register" />} />
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/recommendation" element={<ProtectedRoute><RecommendationPage /></ProtectedRoute>} />
            <Route path="/custom" element={<ProtectedRoute><CustomPage /></ProtectedRoute>} />
            <Route path="/history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
          </Routes>
        </Layout>
      </AuthProvider>

    </BrowserRouter>

  );
}

export default App;
