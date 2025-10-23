import React from "react";
import "./Sidebar.css";

export default function Sidebar({ selectedStation, onClose }) {
  return (
    <div className={`sidebar ${selectedStation ? "open" : ""}`}>
      {selectedStation && (
        <>
          <h2>{selectedStation.name}</h2>
          <p>
            <b>Latitude:</b> {selectedStation.lat.toFixed(4)}
          </p>
          <p>
            <b>Longitude:</b> {selectedStation.lon.toFixed(4)}
          </p>
          <button onClick={onClose} className="close-btn">
            Close
          </button>
        </>
      )}
    </div>
  );
}
