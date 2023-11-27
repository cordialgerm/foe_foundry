import React from "react";
import ReactDOM from "react-dom/client";
import "./css/index.css";
import App from "./App.tsx";
import { BrowserRouter } from "react-router-dom";

function isLocalhost() {
  return window.location.hostname === "localhost";
}

const baseUrl = isLocalhost()
  ? "http://localhost:8080"
  : "https://cordialgerm87.pythonanywhere.com";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <App baseUrl={baseUrl} />
  </BrowserRouter>
);
