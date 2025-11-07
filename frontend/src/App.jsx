import { useState } from "react";
import "./App.css";
import Sidebar from "./components/Sidebar.jsx";
import Overlay from "./components/Overlay.jsx";
import MapContainer from "./components/MapContainer.jsx";
import WelcomePopup from "./components/WelcomePopup";

export default function App() {
  const [selectedStation, setSelectedStation] = useState(null);

  return (
    <div style={{ position: "relative", height: "100vh", width: "100%" }}>
      {/* Sidebar */}
      <Sidebar
        selectedStation={selectedStation}
        onClose={() => setSelectedStation(null)}
      />

      {/* Overlay for background dim + click-to-close */}
      <Overlay
        show={!!selectedStation}
        onClick={() => setSelectedStation(null)}
      />

      <WelcomePopup />

      {/* Leaflet Map */}
      <MapContainer onStationSelect={setSelectedStation} />
    </div>
  );
}
