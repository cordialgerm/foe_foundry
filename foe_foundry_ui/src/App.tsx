import * as React from "react";
import { ThemeProvider } from "@mui/material/styles";
import { CssBaseline } from "@mui/material";

import { useNavigate } from "react-router-dom";
import useMediaQuery from "@mui/material/useMediaQuery";
import theme from "./components/Theme.js";

interface AppProps {
  baseUrl: string;
}

function App({ baseUrl, children }: React.PropsWithChildren<AppProps>) {
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const defaultSidebar = {
    creatureType: "aberration",
    role: "controller",
    cr: "specialist",
    drawerOpen: !isMobile,
  };

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
      navigate("/statblocks");
    },
  };

  const renderPage = () => {
    return React.Children.map(children, (child) => {
      return React.cloneElement(child, pageProps);
    });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {renderPage()}
    </ThemeProvider>
  );
}

export default App;
