import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

function LocationPicker({ onSelect }) {
  useMapEvents({
    click(event) {
      onSelect(event.latlng);
    },
  });

  return null;
}

function App() {
  const [selectedLocation, setSelectedLocation] = useState({
    lat: 20.5937,
    lng: 78.9629,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Tap the map or use your current location.");

  useEffect(() => {
    if (!navigator.geolocation) {
      setStatus("Geolocation is not supported in this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nextLocation = {
          lat: Number(position.coords.latitude.toFixed(5)),
          lng: Number(position.coords.longitude.toFixed(5)),
        };

        setSelectedLocation(nextLocation);
        setStatus("Using your current location.");
      },
      () => {
        setStatus("Location access denied. You can still tap the map manually.");
      }
    );
  }, []);

  const handleMapSelect = (latlng) => {
    const nextLocation = {
      lat: Number(latlng.lat.toFixed(5)),
      lng: Number(latlng.lng.toFixed(5)),
    };

    setSelectedLocation(nextLocation);
    setResult(null);
    setError("");
    setStatus("Location selected.");
  };

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported in this browser.");
      return;
    }

    setLoading(true);
    setError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nextLocation = {
          lat: Number(position.coords.latitude.toFixed(5)),
          lng: Number(position.coords.longitude.toFixed(5)),
        };

        setSelectedLocation(nextLocation);
        setResult(null);
        setStatus("Using your current location.");
        setLoading(false);
      },
      () => {
        setError("Location access was denied. Please allow location access or tap the map manually.");
        setLoading(false);
      }
    );
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          latitude: selectedLocation.lat,
          longitude: selectedLocation.lng,
          lat_abs: Math.abs(selectedLocation.lat),
          lon_abs: Math.abs(selectedLocation.lng),
          lat_sq: selectedLocation.lat * selectedLocation.lat,
          lon_sq: selectedLocation.lng * selectedLocation.lng,
          lat_norm: selectedLocation.lat / 90,
          lon_norm: selectedLocation.lng / 180,
        }),
      });

      if (!response.ok) {
        throw new Error("Could not fetch the prediction result.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="hero-card">
        <div className="badge">U-RESCUE</div>
        <h1>Map-Based Flood Risk Assessment</h1>
        <p>
          Tap the map or use your current location to get flood warnings and
          recommendations.
        </p>
      </div>

      <div className="dashboard">
        <section className="panel map-panel">
          <div className="panel-header">
            <h2>Select Location</h2>
            <p>Click on the map or use your current GPS position.</p>
          </div>

          <div className="coords-row">
            <div className="coord-box">
              <span>Latitude</span>
              <strong>{selectedLocation.lat.toFixed(4)}</strong>
            </div>
            <div className="coord-box">
              <span>Longitude</span>
              <strong>{selectedLocation.lng.toFixed(4)}</strong>
            </div>
          </div>

          <div className="button-row">
            <button
              type="button"
              className="secondary-btn"
              onClick={handleUseCurrentLocation}
              disabled={loading}
            >
              Use my current location
            </button>

            <button
              type="button"
              className="primary-btn"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Get warning"}
            </button>
          </div>

          <div className="status-text">{status}</div>

          <MapContainer
            center={[selectedLocation.lat, selectedLocation.lng]}
            zoom={4}
            className="map"
          >
            <TileLayer
              attribution='&copy; OpenStreetMap contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <LocationPicker onSelect={handleMapSelect} />
            <Marker position={[selectedLocation.lat, selectedLocation.lng]}>
              <Popup>Selected location</Popup>
            </Marker>
          </MapContainer>

          {error ? <div className="error-box">{error}</div> : null}
        </section>

        <section className="panel result-panel">
          <div className="panel-header">
            <h2>Prediction Result</h2>
            <p>Your flood-risk output will appear here.</p>
          </div>

          {result ? (
            <div className="result-card">
              <div className="score-pill">
                <strong>{result.risk_score}/100</strong>
              </div>

              <div className="result-block">
                <h3>{result.risk_level}</h3>
                <p>{result.summary}</p>
              </div>

              <div className="result-block">
                <h4>Recommendations</h4>
                <ul>
                  {result.recommendations.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="result-block">
                <h4>Selected Coordinates</h4>
                <p>
                  Latitude: {result.location.latitude}
                  <br />
                  Longitude: {result.location.longitude}
                </p>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <h3>No assessment yet</h3>
              <p>Choose a location and run the assessment to see warnings.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;