import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";
import bmo from "./assets/bmo.png";
import budweiser from "./assets/budweiser.png";
import rogerscentre from "./assets/rogerscentre.png";
import scotiabank from "./assets/scotiabank.png";

export default function App() {
  const [selectedStation, setSelectedStation] = useState(null);
  const mapRef = useRef(null); // ✅ keeps Leaflet map across re-renders

  useEffect(() => {
    // 🧩 Guard so map is only created once
    if (mapRef.current) return;

    const map = L.map("map").setView([43.7, -79.38], 12);
    mapRef.current = map;

    // --- Map design ---
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      {
        maxZoom: 19,
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> ' +
          '&copy; <a href="https://carto.com/attributions">CARTO</a>',
      }
    ).addTo(map);

    // --- Geolocation dot ---
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude, accuracy } = position.coords;
            const blueDot = L.circleMarker([latitude, longitude], {
              radius: 6,
              color: "#ffffff",        // white border
              weight: 2,
              fillColor: "#007bff",    // blue fill
              fillOpacity: 1,
            })
            .addTo(map)
            .bindPopup("<b>Your Location</b>")
            .openPopup();
      
            const accuracyCircle = L.circle([latitude, longitude], {
              radius: accuracy,    
              color: "#007bff",
              weight: 1,
              fillColor: "#007bff",
              fillOpacity: 0.15,  
            }).addTo(map);
            map.setView([latitude, longitude], 14);
          },
          () => {
            alert("Sorry, no position available.");
          }
        );
      } else {
        alert("Geolocation is not supported by this browser.");
      }

    // --- Line 1 data & drawing ---
    const line1 = [
        { lat: 43.780041, lon: -79.415403, name: "Finch", showMarker: true },  
        { lat: 43.768561, lon: -79.412469, name: "North York Centre", showMarker: true },   
        { lat: 43.761652, lon: -79.412003, name: "Sheppard-Yonge", showMarker: true },   
        { lat: 43.744541, lon: -79.406403, name: "York Mills", showMarker: true },   
        { lat: 43.725327, lon: -79.402048, name: "Lawrence", showMarker: true },   
        { lat: 43.706069, lon: -79.398549, name: "Eglinton", showMarker: true },   
        { lat: 43.698, lon: -79.396966, name: "Davisville", showMarker: true },      
        { lat: 43.688196, lon: -79.39282, name: "St Clair", showMarker: true },    
        { lat: 43.682271, lon: -79.390781, name: "Summerhill", showMarker: true },    
        { lat: 43.676661, lon: -79.389144, name: "Rosedale", showMarker: true },   
        { lat: 43.670469, lon: -79.38658, name: "Bloor-Yonge", showMarker: true },    
        { lat: 43.665401, lon: -79.38466, name: "Wellesley", showMarker: true },   
        { lat: 43.661521, lon: -79.382723, name: "College", showMarker: true },   
        { lat: 43.656319, lon: -79.380939, name: "Dundas", showMarker: true },   
        { lat: 43.652548, lon: -79.379172, name: "Queen", showMarker: true },   
        { lat: 43.649167, lon: -79.377874, name: "King", showMarker: true },   
        { lat: 43.647786, lon: -79.377499, showMarker: false},
        { lat: 43.647126, lon: -79.37765, showMarker: false},
        { lat: 43.646661, lon: -79.377725, showMarker: false},
        { lat: 43.646117, lon: -79.378583, showMarker: false},
        { lat: 43.645387, lon: -79.380536, name: "Union", showMarker: true },   
        { lat: 43.64545, lon: -79.383111, showMarker: false},
        { lat: 43.645644, lon: -79.383669, showMarker: false},
        { lat: 43.646622, lon: -79.384226, showMarker: false},
        { lat: 43.647646, lon: -79.384818, name: "St Andrew", showMarker: true },   
        { lat: 43.650882, lon: -79.386741, name: "Osgoode", showMarker: true },   
        { lat: 43.654845, lon: -79.388356, name: "St Patrick", showMarker: true },   
        { lat: 43.659925, lon: -79.390539, name: "Queen's Park", showMarker: true },   
        { lat: 43.665849, lon: -79.392938, name: "Museum", showMarker: true},
        { lat: 43.668208, lon: -79.393979, showMarker: false},
        { lat: 43.668509, lon: -79.394291, showMarker: false},
        { lat: 43.668511, lon: -79.394891, showMarker: false},
        { lat: 43.667541, lon: -79.399815, name: "St George", showMarker: true},
        { lat: 43.66678, lon: -79.403635, name: "Spadina", showMarker: true},
        { lat: 43.666854, lon: -79.40391, showMarker: false},
        { lat: 43.674836, lon: -79.407132, name: "Dupont", showMarker: true},     
        { lat: 43.682028, lon: -79.410051, showMarker: false},   
        { lat: 43.682579, lon: -79.410705, showMarker: false},
        { lat: 43.682758, lon: -79.411864, showMarker: false},
        { lat: 43.682866, lon: -79.413784, showMarker: false},
        { lat: 43.683381, lon: -79.414647, showMarker: false},
        { lat: 43.684902, lon: -79.415664, name: "St Clair West", showMarker: true},   
        { lat: 43.688052, lon: -79.417767, showMarker: false},
        { lat: 43.688781, lon: -79.418561, showMarker: false},
        { lat: 43.689511, lon: -79.420127, showMarker: false},
        { lat: 43.690472, lon: -79.424698, showMarker: false},
        { lat: 43.690876, lon: -79.429054, showMarker: false},
        { lat: 43.694196, lon: -79.432852, showMarker: false},
        { lat: 43.698943, lon: -79.436135, name: "Eglinton West", showMarker: true},
        { lat: 43.709528, lon: -79.44125, name: "Glencairn", showMarker: true}, 
        { lat: 43.716088, lon: -79.444233, name: "Lawerence West", showMarker: true},       
        { lat: 43.724923, lon: -79.447636, name: "Yorkdale", showMarker: true},       
        { lat: 43.734319, lon: -79.450018, name: "Wilson", showMarker: true},   
        { lat: 43.740119, lon: -79.452283, showMarker: false},
        { lat: 43.743964, lon: -79.457175, showMarker: false},
        { lat: 43.747622, lon: -79.462067, showMarker: false},
        { lat: 43.750194, lon: -79.463343, name: "Sheppard West", showMarker: true},
        { lat: 43.752125, lon: -79.464068, showMarker: false},
        { lat: 43.753439, lon: -79.465793, showMarker: false},
        { lat: 43.754285, lon: -79.469029, showMarker: false},     
        { lat: 43.754927, lon: -79.471415, showMarker: false},
        { lat: 43.753563, lon: -79.479097, name: "Downsview", showMarker: true},
        { lat: 43.753098, lon: -79.482401, showMarker: false},
        { lat: 43.753501, lon: -79.485663, showMarker: false},
        { lat: 43.755423, lon: -79.487766, showMarker: false},
        { lat: 43.759204, lon: -79.489869, showMarker: false},
        { lat: 43.763482, lon: -79.490899, name: "Finch West", showMarker: true},
        { lat: 43.770734, lon: -79.493216, showMarker: false},
        { lat: 43.772314, lon: -79.494675, showMarker: false},
        { lat: 43.773762, lon: -79.500141, name: "York University", showMarker: true},
        { lat: 43.777751, lon: -79.512972, name: "Pioneer Village", showMarker: true},
        { lat: 43.779627, lon: -79.521969, showMarker: false},
        { lat: 43.780638, lon: -79.523764, showMarker: false},
        { lat: 43.782447, lon: -79.525188, name: "Highway 407", showMarker: true},
        { lat: 43.794149, lon: -79.528304, name: "Vaughan Metropolitan Centre", showMarker: true},
      ];
    L.polyline(line1.map((p) => [p.lat, p.lon]), {
      color: "gold",
      weight: 5,
      opacity: 0.4,
      smoothFactor: 1.5,
    }).addTo(map);
    line1.forEach((p) => {
      if (p.showMarker) {
        L.circleMarker([p.lat, p.lon], {
          radius: 4,
          color: "black",
          fillColor: "white",
          fillOpacity: 1,
        })
          .on("click", () => setSelectedStation(p))
          .addTo(map);
      }
    });

    // --- Line 2 data & drawing (same pattern) ---
    const line2 = [
        { lat: 43.637448, lon: -79.536127, name: "Kipling", showMarker: true},
        { lat: 43.645088, lon: -79.526214, showMarker: false},
        { lat: 43.645457, lon: -79.524077, name: "Islington", showMarker: true},
        { lat: 43.648027, lon: -79.511191, name: "Royal York", showMarker: true},
        { lat: 43.645088, lon: -79.526214, showMarker: false},
        { lat: 43.650376, lon: -79.499227, showMarker: false},
        { lat: 43.650252, lon: -79.497285, showMarker: false},
        { lat: 43.649813, lon: -79.49498, name: "Old Mill", showMarker: true},
        { lat: 43.648501, lon: -79.491397, showMarker: false},
        { lat: 43.647942, lon: -79.489283, showMarker: false},
        { lat: 43.647942, lon: -79.487234, showMarker: false},
        { lat: 43.648249, lon: -79.486095, showMarker: false},
        { lat: 43.649336, lon: -79.484797, showMarker: false},
        { lat: 43.649657, lon: -79.484262, name: "Jane", showMarker: true},
        { lat: 43.651816, lon: -79.475913, name: "Runnymede", showMarker: true},
        { lat: 43.65359, lon: -79.466203, name: "High Park", showMarker: true},
        { lat: 43.655205, lon: -79.459605, name: "Keele", showMarker: true},
        { lat: 43.656757, lon: -79.452825, name: "Dundas West", showMarker: true},
        { lat: 43.658931, lon: -79.442461, name: "Lansdowne", showMarker: true},
        { lat: 43.66211, lon: -79.426331, name: "Ossington", showMarker: true},
        { lat: 43.663854, lon: -79.418473, name: "Christie", showMarker: true},
        { lat: 43.665701, lon: -79.411156, name: "Bathurst", showMarker: true},
        { lat: 43.66678, lon: -79.403635, name: "Spadina", showMarker: true},
        { lat: 43.667541, lon: -79.399815, name: "St George", showMarker: true},
        { lat: 43.670063, lon: -79.389891, name: "Bay", showMarker: true},
        { lat: 43.670469, lon: -79.38658, name: "Bloor-Yonge", showMarker: true },    
        { lat: 43.672254, lon: -79.376504, name: "Sherbourne", showMarker: true },    
  
    ];
    
    L.polyline(line2.map((p) => [p.lat, p.lon]), {
      color: "green",
      weight: 5,
      opacity: 0.4,
      smoothFactor: 2,
    }).addTo(map);
    line2.forEach((p) => {
      if (p.showMarker) {
        L.circleMarker([p.lat, p.lon], {
          radius: 4,
          color: "black",
          fillColor: "white",
          fillOpacity: 1,
        })
          .on("click", () => setSelectedStation(p))
          .addTo(map);
      }
    });

    // --- Venues with logos ---
    const venues = [
      { name: "Scotiabank Arena", lat: 43.643369, lon: -79.379012, logo: scotiabank },
      { name: "Rogers Centre", lat: 43.641397, lon: -79.389054, logo: rogerscentre },
      { name: "Budweiser Stage", lat: 43.629221, lon: -79.415093, logo: budweiser },
      { name: "BMO Field", lat: 43.63329, lon: -79.418548, logo: bmo },
    ];

    const getScaledIcon = (logoUrl, zoom) =>
      L.icon({
        iconUrl: logoUrl,
        iconSize: [40 * (zoom / 14), 40 * (zoom / 14)],
        iconAnchor: [20 * (zoom / 14), 40 * (zoom / 14)],
        popupAnchor: [0, -36 * (zoom / 14)],
      });

    const markers = venues.map((v) => {
      const icon = getScaledIcon(v.logo, map.getZoom());
      const m = L.marker([v.lat, v.lon], { icon })
        .bindPopup(`<b>${v.name}</b>`)
        .addTo(map);
      return { m, v };
    });

    map.on("zoomend", () => {
      const zoom = map.getZoom();
      markers.forEach(({ m, v }) => m.setIcon(getScaledIcon(v.logo, zoom)));
    });
  }, [setSelectedStation]); // depend only on setter, not map itself

  // --- Sidebar + map layout ---
  return (
    <div style={{ display: "flex", height: "100vh", width: "100%" }}>
      {selectedStation && (
        <div
          style={{
            width: "300px",
            background: "white",
            boxShadow: "2px 0 5px rgba(0,0,0,0.1)",
            padding: "20px",
            zIndex: 1000,
            overflowY: "auto",
          }}
        >
          <h2>{selectedStation.name}</h2>
          <p>
            <b>Latitude:</b> {selectedStation.lat.toFixed(4)}
          </p>
          <p>
            <b>Longitude:</b> {selectedStation.lon.toFixed(4)}
          </p>
          <button
            onClick={() => setSelectedStation(null)}
            style={{
              marginTop: "10px",
              padding: "8px 12px",
              background: "#007bff",
              border: "none",
              color: "white",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Close
          </button>
        </div>
      )}
      <div id="map" style={{ flex: 1 }} />
    </div>
  );
}
