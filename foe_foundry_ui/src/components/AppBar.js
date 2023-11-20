import { styled } from "@mui/material/styles";
import * as React from "react";

import ConstructionIcon from "@mui/icons-material/Construction";
import MenuIcon from "@mui/icons-material/Menu";
import { AppBar, Container, Toolbar, Typography, Button } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import { drawerWidth } from "./Drawer";
import { useNavigate } from "react-router-dom";

const MuiAppBar = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== "open",
})(({ theme, open }) => ({
  transition: theme.transitions.create(["margin", "width"], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px + 8px)`,
    marginLeft: `${drawerWidth - 8}px`,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

function MenuLink({ display, url }) {
  const navigate = useNavigate();

  const onClick = () => {
    navigate(url);
  };

  return (
    <Button key={display} color="inherit" onClick={onClick}>
      {display}
    </Button>
  );
}

function HomeLink() {
  const navigate = useNavigate();

  const onClick = () => {
    navigate("/");
  };

  return (
    <Button
      onClick={onClick}
      sx={{
        display: { xs: "none", md: "flex" },
        flexGrow: 1,
        justifyContent: "flex-start",
      }}
    >
      <ConstructionIcon
        sx={{ color: "primary.contrastText" }}
        style={{ marginRight: "10px" }}
      />
      <Typography
        variant="h6"
        noWrap
        component="a"
        sx={{
          mr: 2,
          fontFamily: "monospace",
          fontWeight: 700,
          letterSpacing: ".2rem",
          color: "primary.contrastText",
          textDecoration: "none",
        }}
      >
        Foe Foundry
      </Typography>
    </Button>
  );
}

export function FoeFoundryAppBar({ drawerOpen, setDrawerOpen }) {
  const handleDrawerOpen = () => {
    setDrawerOpen(true);
  };

  const menus = [
    { display: "Statblocks", url: "/statblocks" },
    { display: "Powers", url: "/powers" },
    { display: "Credits", url: "/credits" },
  ];

  return (
    <MuiAppBar position="static" open={drawerOpen}>
      <Container>
        <Toolbar disableGutters>
          {!drawerOpen && (
            <IconButton onClick={handleDrawerOpen}>
              <MenuIcon />
            </IconButton>
          )}
          <HomeLink />
          {menus.map((m) => (
            <MenuLink key={m.display} display={m.display} url={m.url} />
          ))}
        </Toolbar>
      </Container>
    </MuiAppBar>
  );
}
