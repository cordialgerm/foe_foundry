import * as React from "react";
import { drawerWidth } from "./Drawer";
import { styled } from "@mui/material";

interface MainContentProps {
  drawerOpen: boolean;
}

export const MainContent = styled("main", {
  shouldForwardProp: (prop) => prop !== "drawerOpen",
})<MainContentProps>(({ theme, drawerOpen }) => ({
  flexGrow: 1,
  transition: theme.transitions.create("margin", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: 0,
  ...(drawerOpen && {
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: `${drawerWidth - 7}px`,
  }),
}));
