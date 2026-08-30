import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";

export default function Navbar(){
 const {isAuthenticated,user,logout}=useAuth(); const {language,changeLanguage}=useLanguage(); const navigate=useNavigate();
 return <header className="site-header"><div className="nav-wrap">
  <NavLink to="/" className="brand"><span className="brand-icon">✦</span><span><strong>Scheme Sahayak</strong><b> AI</b><small>Government Scheme Intelligence</small></span></NavLink>
  <nav className="public-nav"><NavLink to="/">Home</NavLink><NavLink to="/how-it-works">How it works</NavLink><NavLink to="/schemes">Explore schemes</NavLink><NavLink to="/about">About</NavLink><NavLink to="/faq">FAQ</NavLink></nav>
  <div className="nav-actions"><select aria-label="Language" value={language} onChange={e=>changeLanguage(e.target.value)}><option value="en">English</option><option value="hi">हिन्दी</option><option value="ta">தமிழ்</option><option value="te">తెలుగు</option><option value="kn">ಕನ್ನಡ</option><option value="ml">മലയാളം</option></select>{isAuthenticated?<><NavLink className="nav-dashboard" to="/dashboard">Dashboard</NavLink><button className="avatar" onClick={()=>navigate('/profile')}>{(user?.username||'U').slice(0,1).toUpperCase()}</button><button className="link-button" onClick={()=>{logout();navigate('/')}}>Sign out</button></>:<><NavLink to="/login">Sign in</NavLink><NavLink className="btn btn-primary btn-small" to="/register">Get started</NavLink></>}</div>
 </div></header>;
}
