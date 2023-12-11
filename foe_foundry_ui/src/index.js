import React from "react";
import ReactDOM from "react-dom/client";
import "./css/index.css";
import App from "./App.tsx";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import StatblockPage from "./pages/StatblockPage.tsx";
import HomePage from "./pages/HomePage.tsx";
import CreditPage from "./pages/CreditPage.tsx";
import ConditionPage from "./pages/ConditionsPage.tsx";
import PowersPage from "./pages/PowersPage.tsx";
import { OglPage } from "./pages/OglPage.tsx";

function isLocalhost() {
  return window.location.hostname === "localhost";
}

const baseUrl = isLocalhost()
  ? "http://localhost:8080"
  : "https://cordialgerm87.pythonanywhere.com";

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <App baseUrl={baseUrl}>
        <HomePage />
      </App>
    ),
  },
  {
    path: "/credits",
    element: (
      <App baseUrl={baseUrl}>
        <CreditPage />
      </App>
    ),
  },
  {
    path: "/conditions",
    element: (
      <App baseUrl={baseUrl}>
        <ConditionPage />
      </App>
    ),
  },
  {
    path: "/ogl",
    element: (
      <App baseUrl={baseUrl}>
        <OglPage />
      </App>
    ),
  },
  {
    path: "/statblocks",
    element: (
      <App baseUrl={baseUrl}>
        <StatblockPage />
      </App>
    ),
  },
  {
    path: "/powers",
    element: (
      <App baseUrl={baseUrl}>
        <PowersPage />
      </App>
    ),
  },
  {
    path: "/powers/:tab",
    element: (
      <App baseUrl={baseUrl}>
        <PowersPage />
      </App>
    ),
  },
]);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<RouterProvider router={router} />);
