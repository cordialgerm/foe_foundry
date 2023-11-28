import * as React from "react";

import { FoeFoundryAppBar } from "./AppBar.tsx";
import { FoeFoundryAppDrawer } from "./Drawer.tsx";
import { MainContent } from "./Main.tsx";
import { Box } from "@mui/material";

export interface SidebarData {
  creatureType: string;
  role: string;
  cr: string;
  drawerOpen: boolean;
}

export interface PageProps {
  baseUrl: string;
  sidebar: SidebarData;
  isMobile: boolean;
  setSidebar: (sidebar: SidebarData) => SidebarData;
  onGenerate: () => void;
}

export function PageLayout(props: React.PropsWithChildren<PageProps>) {
  const sidebar = props.sidebar;

  const setDrawerOpen = (open: boolean) => {
    props.setSidebar({ ...sidebar, drawerOpen: open });
  };

  const setCreatureType = (creatureType: string) => {
    props.setSidebar({ ...sidebar, creatureType: creatureType });
  };

  const setRole = (role: string) => {
    props.setSidebar({ ...sidebar, role: role });
  };

  const setCr = (cr: string) => {
    props.setSidebar({ ...sidebar, cr: cr });
  };

  return (
    <>
      <FoeFoundryAppBar
        drawerOpen={sidebar.drawerOpen}
        setDrawerOpen={setDrawerOpen}
        isMobile={props.isMobile}
      />
      <FoeFoundryAppDrawer
        open={sidebar.drawerOpen}
        setOpen={setDrawerOpen}
        creatureType={sidebar.creatureType}
        setCreatureType={setCreatureType}
        role={sidebar.role}
        setRole={setRole}
        cr={sidebar.cr}
        setCr={setCr}
        onGenerate={props.onGenerate}
        isMobile={props.isMobile}
      />
      <Box style={{ backgroundColor: "#f5f5f5" }}>
        <MainContent drawerOpen={sidebar.drawerOpen}>
          {props.children}
        </MainContent>
      </Box>
    </>
  );
}
