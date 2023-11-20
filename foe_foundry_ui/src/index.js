import React from "react";
import ReactDOM from "react-dom/client";
import "./css/index.css";
import App from "./App";

// const baseUrl = "127.0.0.1:8080"
const baseUrl = "cordialgerm87.pythonanywhere.com";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App baseUrl={baseUrl} />);
