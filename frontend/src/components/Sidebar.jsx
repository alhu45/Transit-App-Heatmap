import React from "react";
import "./Sidebar.css";
import { useEffect, useState} from "react";

// useEffect

// useState

export default function Sidebar({ selectedStation, onClose }) {
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    if (!selectedStation) return;

    const now = new Date();
    const day = now.toLocaleString("en-US", { weekday: "long" }); // e.g., "Monday"
    const hour = now.getHours(); // 0–23

    const payload = {
      records: {
        station: selectedStation.name, 
        line: selectedStation.line,                     
        day: day,
        hour: hour,
      },
    };

    console.log("Sending payload:", payload);

    fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        console.log("Prediction:", data);
        setPrediction(data);
      })
      .catch((err) => {
        console.error("Error fetching prediction:", err);
        setPrediction(null);
      });
  }, [selectedStation]);

  return (
    <div className={`sidebar ${selectedStation ? "open" : ""} line-${selectedStation?.line}`}>
      {selectedStation && (
        <>
          <div className="sidebar-header">
            <h2>{selectedStation.name} Station</h2>
          </div>

          <p><b>Latitude:</b> {selectedStation.lat.toFixed(4)}</p>
          <p><b>Longitude:</b> {selectedStation.lon.toFixed(4)}</p>

          {prediction ? (
            <>
              <p><b>Day:</b> {prediction.predictions[0].day}</p>
              <p><b>Hour:</b> {prediction.predictions[0].hour}:00</p>
              <p><b>Estimated Riders:</b> {Math.round(prediction.predictions[0].riders).toLocaleString()}</p>
            </>
          ) : (
            <p>Loading prediction...</p>
          )}

          <button onClick={onClose} className="close-btn">Close</button>
        </>
      )}
    </div>
  );
}
