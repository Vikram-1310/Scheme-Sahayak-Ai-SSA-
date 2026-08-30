import { useState } from "react";
import { getNearbyPartners } from "../api/client";
import { useLanguage } from "../context/LanguageContext";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const userIcon = L.divIcon({
  className: "user-map-pin",
  html: '<span style="display:block;width:16px;height:16px;border-radius:50%;background:#1769e0;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.3)"></span>',
  iconSize: [16,16], iconAnchor: [8,8]
});

const partnerIcon = L.divIcon({
  className: "partner-map-pin",
  html: '<span style="display:block;width:14px;height:14px;border-radius:50%;background:#19734a;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.3)"></span>',
  iconSize: [14,14], iconAnchor: [7,7]
});

function Recenter({ position }) {
  const map = useMap();
  map.setView(position, Math.max(map.getZoom(), 12), { animate: false });
  return null;
}

export default function NearbyPartners({ schemeId }) {
  const { t } = useLanguage();
  const [position, setPosition] = useState(null);
  const [partners, setPartners] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const locate = () => {
    if (!navigator.geolocation) {
      setStatus(t("locationUnavailable"));
      return;
    }
    setLoading(true);
    setStatus("");
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        const p = [coords.latitude, coords.longitude];
        setPosition(p);
        try {
          const data = await getNearbyPartners(schemeId, coords.latitude, coords.longitude, 50);
          setPartners(data.partners || []);
          if (!(data.partners || []).length) setStatus(t("noPartners"));
        } catch (e) {
          setStatus(e.detail || t("locationUnavailable"));
        } finally {
          setLoading(false);
        }
      },
      (err) => {
        setLoading(false);
        setStatus(err.code === 1 ? t("locationDenied") : t("locationUnavailable"));
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
  };

  const defaultCenter = [20.5937, 78.9629];

  return (
    <div>
      <button className="btn btn-secondary" type="button" onClick={locate} disabled={loading}>
        {loading ? t("locating") : t("useLocation")}
      </button>
      {status && <div className="location-status">{status}</div>}
      {position && (
        <div className="nearby-layout">
          <div className="map-shell">
            <MapContainer center={position} zoom={12} scrollWheelZoom className="leaflet-container">
              <TileLayer
                attribution='&copy; OpenStreetMap contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Recenter position={position} />
              <Marker position={position} icon={userIcon}>
                <Popup>Your current location</Popup>
              </Marker>
              {partners.map(p => (
                <Marker key={p.id} position={[p.latitude, p.longitude]} icon={partnerIcon}>
                  <Popup>
                    <strong>{p.name}</strong><br />
                    {p.partner_type}<br />
                    {p.address || ""}<br />
                    {p.distance_km} km away
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
          <div className="partner-list">
            {partners.length ? partners.map(p => (
              <article className="partner-card" key={p.id}>
                <span className="partner-distance">{p.distance_km} km</span>
                <h3>{p.name}</h3>
                <p>{p.partner_type}</p>
                <p>{p.address || "Address not provided"}</p>
                {p.phone && <p>☎ {p.phone}</p>}
              </article>
            )) : <div className="partner-empty">{t("noPartners")}</div>}
          </div>
        </div>
      )}
    </div>
  );
}
