import React from "react";
import ReactDOM from "react-dom/client";
import "./css/index.css";
import App from "./App.tsx";
import { BrowserRouter } from "react-router-dom";

//const baseUrl = "https://127.0.0.1:8080";
const baseUrl = "https://cordialgerm87.pythonanywhere.com";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <App baseUrl={baseUrl} />
  </BrowserRouter>
);
