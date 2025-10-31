import React, { useState, useEffect } from "react";
import "./WelcomePopup.css";

export default function WelcomePopup() {
  const [showPopup, setShowPopup] = useState(true);
  if (!showPopup) return null;

  return (
    <div className="popup-overlay">
      <div className="popup-box">
        <h1>Welcome!</h1>
        <p>Explore real-time TTC station data and predictions.</p>
        <button onClick={() => setShowPopup(false)}>Get Started</button>
      </div>
    </div>
  );
}
