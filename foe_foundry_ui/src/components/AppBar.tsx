import * as React from "react";

import { FoeFoundryIcon } from "./FoeFoundryIcon.tsx";
import MenuIcon from "@mui/icons-material/Menu";
import { AppBar, Container, Toolbar, Typography, Button } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import { drawerWidth } from "./Drawer.tsx";
import { useNavigate } from "react-router-dom";

interface MuiAppBarProps {
  open: boolean;
}

function MuiAppBar({
  open,
  children,
}: React.PropsWithChildren<MuiAppBarProps>) {
  return (
    <AppBar
      position="static"
      sx={{
        transition: (theme) =>
          theme.transitions.create(["margin", "width"], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        ...(open && {
          width: `calc(100% - ${drawerWidth}px + 8px)`,
          marginLeft: `${drawerWidth - 8}px`,
          transition: (theme) =>
            theme.transitions.create(["margin", "width"], {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            }),
        }),
      }}
    >
      {children}
    </AppBar>
  );
}

interface MenuLinkProps {
  key: string;
  display: string;
  url: string;
}

function MenuLink({ ...props }: MenuLinkProps) {
  const navigate = useNavigate();

  const onClick = () => {
    navigate(props.url);
  };

  return (
    <Button key={props.key} color="inherit" onClick={onClick}>
      {props.display}
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
        display: "flex",
        // display: { xs: "none", md: "flex" },
        flexGrow: 1,
        justifyContent: "flex-start",
      }}
    >
      <FoeFoundryIcon
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

export interface AppBarProps {
  drawerOpen: boolean;
  setDrawerOpen: (open: boolean) => void;
  isMobile: boolean;
}

export function FoeFoundryAppBar({
  drawerOpen,
  setDrawerOpen,
  isMobile,
}: AppBarProps) {
  const handleDrawerOpen = () => {
    setDrawerOpen(true);
  };

  const menus = [
    { display: "Statblocks", url: "/statblocks" },
    { display: "Conditions", url: "/conditions" },
    { display: "Credits", url: "/credits" },
  ];

  return (
    <MuiAppBar open={drawerOpen}>
      <Container>
        <Toolbar disableGutters>
          {!drawerOpen && (
            <IconButton onClick={handleDrawerOpen}>
              <MenuIcon />
            </IconButton>
          )}
          <HomeLink />
          {!isMobile &&
            menus.map((m) => (
              <MenuLink key={m.display} display={m.display} url={m.url} />
            ))}
        </Toolbar>
      </Container>
    </MuiAppBar>
  );
}
