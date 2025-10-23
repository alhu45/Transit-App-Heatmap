import "./Overlay.css";

export default function Overlay({ show, onClick }) {
  return (
    <div
      className={`overlay ${show ? "visible" : ""}`}
      onClick={onClick}
    />
  );
}
