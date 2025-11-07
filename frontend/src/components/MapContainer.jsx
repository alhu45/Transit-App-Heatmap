import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import bmo from "../assets/bmo.png";
import budweiser from "../assets/budweiser.png";
import rogerscentre from "../assets/rogerscentre.png";
import scotiabank from "../assets/scotiabank.png";
import pin from "../assets/pin.png"

export default function MapContainer({ onStationSelect, onVenueSelect }) {
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapRef.current) return;
    const map = L.map("map", { zoomControl: false }).setView([43.7, -79.38], 12);
    mapRef.current = map;
    L.control.zoom({ position: "topright" }).addTo(map);

    // Map Design
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      {
        maxZoom: 19,
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      }
    ).addTo(map);

    const locateButton = L.control({ position: "topright" });

    locateButton.onAdd = function () {
      const button = L.DomUtil.create("button", "locate-btn");
      button.innerHTML = "My Location";
      button.style.background = "#007bff";
      button.style.color = "white";
      button.style.border = "none";
      button.style.padding = "6px 10px";
      button.style.borderRadius = "6px";
      button.style.cursor = "pointer";
      button.style.fontWeight = "600";
      button.style.boxShadow = "0 1px 4px rgba(0,0,0,0.3)";

      // Prevent map dragging when clicking the button
      L.DomEvent.disableClickPropagation(button);

      button.addEventListener("click", () => {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              const { latitude, longitude, accuracy } = position.coords;

              L.circleMarker([latitude, longitude], {
                radius: 6,
                color: "#ffffff",
                weight: 2,
                fillColor: "#007bff",
                fillOpacity: 1,
              })
                .addTo(map)
                .bindPopup("<b>Current Location</b>")
                .openPopup();

              L.circle([latitude, longitude], {
                radius: accuracy,
                color: "#007bff",
                weight: 1,
                fillColor: "#007bff",
                fillOpacity: 0.15,
              }).addTo(map);

              map.flyTo([latitude, longitude], 15, {
                animate: true,
                duration: 1.5, // 1.5 second zoom animation
              });
            },
            () => alert("Unable to retrieve your location.")
          );
        } else {
          alert("Geolocation not supported by your browser.");
        }
      });

      return button;
    };

    locateButton.addTo(map);

    // LINE 1 Stations
    const line1 = [
        { lat: 43.780041, lon: -79.415403, name: "Finch",line: "1", showMarker: true },  
        { lat: 43.768561, lon: -79.412469, name: "North York Centre",line: "1", showMarker: true },   
        { lat: 43.761652, lon: -79.412003, name: "Sheppard-Yonge",line: "1", showMarker: true },   
        { lat: 43.744541, lon: -79.406403, name: "York Mills",line: "1", showMarker: true },   
        { lat: 43.725327, lon: -79.402048, name: "Lawrence",line: "1", showMarker: true },   
        { lat: 43.706069, lon: -79.398549, name: "Eglinton",line: "1", showMarker: true },   
        { lat: 43.698, lon: -79.396966, name: "Davisville",line: "1", showMarker: true },      
        { lat: 43.688196, lon: -79.39282, name: "St Clair",line: "1", showMarker: true },    
        { lat: 43.682271, lon: -79.390781, name: "Summerhill",line: "1", showMarker: true },    
        { lat: 43.676661, lon: -79.389144, name: "Rosedale",line: "1", showMarker: true },   
        { lat: 43.670469, lon: -79.38658, name: "Bloor-Yonge",line: "1", showMarker: true },    
        { lat: 43.665401, lon: -79.38466, name: "Wellesley",line: "1", showMarker: true },   
        { lat: 43.661521, lon: -79.382723, name: "College",line: "1", showMarker: true },   
        { lat: 43.656319, lon: -79.380939, name: "Dundas",line: "1", showMarker: true },   
        { lat: 43.652548, lon: -79.379172, name: "Queen",line: "1", showMarker: true },   
        { lat: 43.649167, lon: -79.377874, name: "King",line: "1", showMarker: true },   
        { lat: 43.647786, lon: -79.377499, showMarker: false},
        { lat: 43.647126, lon: -79.37765, showMarker: false},
        { lat: 43.646661, lon: -79.377725, showMarker: false},
        { lat: 43.646117, lon: -79.378583, showMarker: false},
        { lat: 43.645387, lon: -79.380536, name: "Union",line: "1", showMarker: true },   
        { lat: 43.64545, lon: -79.383111, showMarker: false},
        { lat: 43.645644, lon: -79.383669, showMarker: false},
        { lat: 43.646622, lon: -79.384226, showMarker: false},
        { lat: 43.647646, lon: -79.384818, name: "St Andrew",line: "1", showMarker: true },   
        { lat: 43.650882, lon: -79.386741, name: "Osgoode",line: "1", showMarker: true },   
        { lat: 43.654845, lon: -79.388356, name: "St Patrick",line: "1", showMarker: true },   
        { lat: 43.659925, lon: -79.390539, name: "Queen's Park",line: "1", showMarker: true },   
        { lat: 43.665849, lon: -79.392938, name: "Museum",line: "1", showMarker: true},
        { lat: 43.668208, lon: -79.393979, showMarker: false},
        { lat: 43.668509, lon: -79.394291, showMarker: false},
        { lat: 43.668511, lon: -79.394891, showMarker: false},
        { lat: 43.667541, lon: -79.399815, name: "St George",line: "1", showMarker: true},
        { lat: 43.66678, lon: -79.403635, name: "Spadina",line: "1", showMarker: true},
        { lat: 43.666854, lon: -79.40391, showMarker: false},
        { lat: 43.674836, lon: -79.407132, name: "Dupont",line: "1", showMarker: true},     
        { lat: 43.682028, lon: -79.410051, showMarker: false},   
        { lat: 43.682579, lon: -79.410705, showMarker: false},
        { lat: 43.682758, lon: -79.411864, showMarker: false},
        { lat: 43.682866, lon: -79.413784, showMarker: false},
        { lat: 43.683381, lon: -79.414647, showMarker: false},
        { lat: 43.684902, lon: -79.415664, name: "St Clair West",line: "1", showMarker: true},   
        { lat: 43.688052, lon: -79.417767, showMarker: false},
        { lat: 43.688781, lon: -79.418561, showMarker: false},
        { lat: 43.689511, lon: -79.420127, showMarker: false},
        { lat: 43.690472, lon: -79.424698, showMarker: false},
        { lat: 43.690876, lon: -79.429054, showMarker: false},
        { lat: 43.694196, lon: -79.432852, showMarker: false},
        { lat: 43.698943, lon: -79.436135, name: "Eglinton West",line: "1", showMarker: true},
        { lat: 43.709528, lon: -79.44125, name: "Glencairn",line: "1", showMarker: true}, 
        { lat: 43.716088, lon: -79.444233, name: "Lawerence West",line: "1", showMarker: true},       
        { lat: 43.724923, lon: -79.447636, name: "Yorkdale",line: "1", showMarker: true},       
        { lat: 43.734319, lon: -79.450018, name: "Wilson",line: "1", showMarker: true},   
        { lat: 43.740119, lon: -79.452283, showMarker: false},
        { lat: 43.743964, lon: -79.457175, showMarker: false},
        { lat: 43.747622, lon: -79.462067, showMarker: false},
        { lat: 43.750194, lon: -79.463343, name: "Sheppard West",line: "1", showMarker: true},
        { lat: 43.752125, lon: -79.464068, showMarker: false},
        { lat: 43.753439, lon: -79.465793, showMarker: false},
        { lat: 43.754285, lon: -79.469029, showMarker: false},     
        { lat: 43.754927, lon: -79.471415, showMarker: false},
        { lat: 43.753563, lon: -79.479097, name: "Downsview",line: "1", showMarker: true},
        { lat: 43.753098, lon: -79.482401, showMarker: false},
        { lat: 43.753501, lon: -79.485663, showMarker: false},
        { lat: 43.755423, lon: -79.487766, showMarker: false},
        { lat: 43.759204, lon: -79.489869, showMarker: false},
        { lat: 43.763482, lon: -79.490899, name: "Finch West",line: "1", showMarker: true},
        { lat: 43.770734, lon: -79.493216, showMarker: false},
        { lat: 43.772314, lon: -79.494675, showMarker: false},
        { lat: 43.773762, lon: -79.500141, name: "York University",line: "1", showMarker: true},
        { lat: 43.777751, lon: -79.512972, name: "Pioneer Village",line: "1", showMarker: true},
        { lat: 43.779627, lon: -79.521969, showMarker: false},
        { lat: 43.780638, lon: -79.523764, showMarker: false},
        { lat: 43.782447, lon: -79.525188, name: "Highway 407",line: "1", showMarker: true},
        { lat: 43.794149, lon: -79.528304, name: "Vaughan Metropolitan Centre",line: "1", showMarker: true},
      ];

    // Line 1 Design
    L.polyline(line1.map((p) => [p.lat, p.lon]), {
      color: "gold",
      weight: 5,
      opacity: 0.4,
      smoothFactor: 1.5,
    }).addTo(map);

    line1.forEach((p) => {
      if (p.showMarker) {
        L.circleMarker([p.lat, p.lon], {
          radius: 3,
          color: "black",
          fillColor: "white",
          fillOpacity: 1,
        })
          .on("click", () => onStationSelect(p))
          .addTo(map);
      }
    });

    // LINE 2 Stations
    const line2 = [
        { lat: 43.637448, lon: -79.536127, name: "Kipling", line: "2", showMarker: true},
        { lat: 43.645088, lon: -79.526214, showMarker: false},
        { lat: 43.645457, lon: -79.524077, name: "Islington",line: "2", showMarker: true},
        { lat: 43.648027, lon: -79.511191, name: "Royal York",line: "2", showMarker: true},
        { lat: 43.645088, lon: -79.526214, showMarker: false},
        { lat: 43.650376, lon: -79.499227, showMarker: false},
        { lat: 43.650252, lon: -79.497285, showMarker: false},
        { lat: 43.649813, lon: -79.49498, name: "Old Mill",line: "2", showMarker: true},
        { lat: 43.648501, lon: -79.491397, showMarker: false},
        { lat: 43.647942, lon: -79.489283, showMarker: false},
        { lat: 43.647942, lon: -79.487234, showMarker: false},
        { lat: 43.648249, lon: -79.486095, showMarker: false},
        { lat: 43.649336, lon: -79.484797, showMarker: false},
        { lat: 43.649657, lon: -79.484262, name: "Jane",line: "2", showMarker: true},
        { lat: 43.651816, lon: -79.475913, name: "Runnymede",line: "2", showMarker: true},
        { lat: 43.65359, lon: -79.466203, name: "High Park",line: "2", showMarker: true},
        { lat: 43.655205, lon: -79.459605, name: "Keele",line: "2", showMarker: true},
        { lat: 43.656757, lon: -79.452825, name: "Dundas West",line: "2", showMarker: true},
        { lat: 43.658931, lon: -79.442461, name: "Lansdowne",line: "2", showMarker: true},
        { lat: 43.66211, lon: -79.426331, name: "Ossington",line: "2", showMarker: true},
        { lat: 43.663854, lon: -79.418473, name: "Christie",line: "2", showMarker: true},
        { lat: 43.665701, lon: -79.411156, name: "Bathurst",line: "2", showMarker: true},
        { lat: 43.66678, lon: -79.403635, name: "Spadina",line: "2", showMarker: true},
        { lat: 43.667541, lon: -79.399815, name: "St George",line: "2", showMarker: true},
        { lat: 43.670063, lon: -79.389891, name: "Bay",line: "2", showMarker: true},
        { lat: 43.670469, lon: -79.38658, name: "Bloor-Yonge",line: "2", showMarker: true },    
        { lat: 43.672254, lon: -79.376504, name: "Sherbourne",line: "2", showMarker: true },    
  
    ];

    // Line 2 Design 
    L.polyline(line2.map((p) => [p.lat, p.lon]), {
      color: "green",
      weight: 5,
      opacity: 0.4,
      smoothFactor: 2,
    }).addTo(map);

    line2.forEach((p) => {
      if (p.showMarker) {
        L.circleMarker([p.lat, p.lon], {
          radius: 3,
          color: "black",
          fillColor: "white",
          fillOpacity: 1,
        })
          .on("click", () => onStationSelect(p))
          .addTo(map);
      }
    });

    // Venues
    const venues = [
      { name: "Scotiabank Arena", lat: 43.643369, lon: -79.379012, logo: pin },
      { name: "Rogers Centre", lat: 43.641397, lon: -79.389054, logo: pin },
      { name: "Budweiser Stage", lat: 43.629221, lon: -79.415093, logo: pin },
      { name: "BMO Field", lat: 43.63329, lon: -79.418548, logo: pin },
    ];

    // Zoom affect for venues
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
        .on("click", () => onVenueSelect(v))
        .addTo(map);
      return { m, v };
    });

    map.on("zoomend", () => {
      const zoom = map.getZoom();
      markers.forEach(({ m, v }) => m.setIcon(getScaledIcon(v.logo, zoom)));
    });
  }, [onStationSelect]);

  return <div id="map" style={{ height: "100%", width: "100%" }} />;
}
