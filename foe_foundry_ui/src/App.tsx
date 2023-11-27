import * as React from "react";
import { Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import { CssBaseline } from "@mui/material";

import StatblockPage from "./pages/StatblockPage.tsx";
import HomePage from "./pages/HomePage.tsx";
import CreditPage from "./pages/CreditPage.tsx";
import ConditionPage from "./pages/ConditionsPage.tsx";
import { OglPage } from "./pages/OglPage.tsx";
import { useNavigate } from "react-router-dom";
import useMediaQuery from "@mui/material/useMediaQuery";
import theme from "./components/Theme.js";

interface AppProps {
  baseUrl: string;
}

function App({ baseUrl }: AppProps) {
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const defaultSidebar = {
    creatureType: "aberration",
    role: "controller",
    cr: "specialist",
    drawerOpen: !isMobile,
  };
  console.log("defaultSidebar", defaultSidebar);

  const navigate = useNavigate();
  const [sidebar, setSidebar] = React.useState(defaultSidebar);
  const pageProps = {
    baseUrl: baseUrl,
    sidebar: sidebar,
    isMobile: isMobile,
    setSidebar: setSidebar,
    onGenerate: () => {
      //on mobile devices, close the drawer after generating a new statblock so user can see it better
      if (isMobile) {
        setSidebar({ ...sidebar, drawerOpen: false });
      }

      const newUrl =
        "/statblocks/" +
        sidebar.creatureType +
        "/" +
        sidebar.role +
        "/" +
        sidebar.cr;

      navigate(newUrl);
    },
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        <Route path="/" element={<HomePage {...pageProps} />} />
        <Route path="/statblocks" element={<StatblockPage {...pageProps} />}>
          <Route
            path=":creatureType"
            element={<StatblockPage {...pageProps} />}
          />
          <Route
            path=":creatureType/:creatureRole"
            element={<StatblockPage {...pageProps} />}
          />
          <Route
            path=":creatureType/:creatureRole/:cr"
            element={<StatblockPage {...pageProps} />}
          />
        </Route>
        <Route path="/credits" element={<CreditPage {...pageProps} />} />
        <Route path="/conditions" element={<ConditionPage {...pageProps} />} />
        <Route path="/ogl" element={<OglPage {...pageProps} />} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;
