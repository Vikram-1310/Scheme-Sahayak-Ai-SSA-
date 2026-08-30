import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LanguageProvider } from "./context/LanguageContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import AIChat from "./components/AIChat";
import Home from "./pages/Home";
import HowItWorks from "./pages/HowItWorks";
import Schemes from "./pages/Schemes";
import About from "./pages/About";
import FAQ from "./pages/FAQ";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Eligibility from "./pages/Eligibility";
import Recommendations from "./pages/Recommendations";
import Applications from "./pages/Applications";
import SchemeDetail from "./pages/SchemeDetail";
import Saved from "./pages/Saved"; import Compare from "./pages/Compare"; import Assistant from "./pages/Assistant"; import Notifications from "./pages/Notifications"; import Settings from "./pages/Settings";

function AppShell() {
  const { isAuthenticated } = useAuth();
  return <><Navbar /><Routes>
    <Route path="/" element={<Home />} />
    <Route path="/how-it-works" element={<HowItWorks />} />
    <Route path="/schemes" element={<Schemes />} />
    <Route path="/about" element={<About />} />
    <Route path="/faq" element={<FAQ />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
    <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
    <Route path="/eligibility" element={<ProtectedRoute><Eligibility /></ProtectedRoute>} />
    <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
    <Route path="/applications" element={<ProtectedRoute><Applications /></ProtectedRoute>} />
    <Route path="/saved" element={<ProtectedRoute><Saved /></ProtectedRoute>} />
    <Route path="/compare" element={<ProtectedRoute><Compare /></ProtectedRoute>} />
    <Route path="/assistant" element={<ProtectedRoute><Assistant /></ProtectedRoute>} />
    <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
    <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
    <Route path="/schemes/:schemeId" element={<SchemeDetail />} />
    <Route path="/go" element={<Navigate to={isAuthenticated ? "/dashboard" : "/"} replace />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes><AIChat /></>;
}

export default function App() { return <LanguageProvider><AuthProvider><BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><AppShell /></BrowserRouter></AuthProvider></LanguageProvider>; }
