import * as React from "react";
import { Routes, Route, BrowserRouter } from "react-router-dom";

import StatblockPage from "./pages/StatblockPage.tsx";
import HomePage from "./pages/HomePage.tsx";
import CreditPage from "./pages/CreditPage.tsx";
import ConditionPage from "./pages/ConditionsPage.tsx";
import { OglPage } from "./pages/OglPage.tsx";

function App({ baseUrl }) {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage baseUrl={baseUrl} />} />
        <Route path="/statblocks" element={<StatblockPage baseUrl={baseUrl} />}>
          <Route
            path=":creatureType"
            element={<StatblockPage baseUrl={baseUrl} />}
          />
          <Route
            path=":creatureType/:creatureRole"
            element={<StatblockPage baseUrl={baseUrl} />}
          />
          <Route
            path=":creatureType/:creatureRole/:cr"
            element={<StatblockPage baseUrl={baseUrl} />}
          />
        </Route>
        <Route path="/credits" element={<CreditPage />} />
        <Route path="/conditions" element={<ConditionPage />} />
        <Route path="/ogl" element={<OglPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
