import * as React from "react";
import { Routes, Route, BrowserRouter } from "react-router-dom";

import StatblockPage from "./pages/StatblockPage.tsx";
import HomePage from "./pages/HomePage.tsx";

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
      </Routes>
    </BrowserRouter>
  );
}

export default App;
