import * as React from 'react';

import { ThemeProvider } from '@mui/material/styles'

import { CssBaseline } from '@mui/material';
import { FoeFoundryAppBar } from './AppBar.js';
import { PersistentDrawerLeft } from './Drawer.js';
import { MainContent } from './Main.tsx'
import theme from './Theme.js';
import { useNavigate } from 'react-router-dom';

export interface SidebarData {
  creatureType: string;
  role: string;
  cr: string;
  drawerOpen: boolean;
}

export const DefaultSidebarData: SidebarData = {
  creatureType: "humanoid",
  role: "bruiser",
  cr: "specialist",
  drawerOpen: true,
}

export interface DefaultPageProps {
  baseUrl: string;
}

export interface PageProps extends DefaultPageProps {
  sidebar: SidebarData;
  setSidebar: (sidebar: SidebarData) => void;
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

  const setCr = (cr: string) => { props.setSidebar({ ...sidebar, cr: cr }); };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <FoeFoundryAppBar drawerOpen={sidebar.drawerOpen} setDrawerOpen={setDrawerOpen} />
      <PersistentDrawerLeft
        open={sidebar.drawerOpen} setOpen={setDrawerOpen}
        creatureType={sidebar.creatureType} setCreatureType={setCreatureType}
        role={sidebar.role} setRole={setRole}
        cr={sidebar.cr} setCr={setCr}
        onGenerate={props.onGenerate} />
      <MainContent drawerOpen={sidebar.drawerOpen}>
        {props.children}
      </MainContent>
    </ThemeProvider>
  );
}

export function DefaultPageLayout(props: React.PropsWithChildren<DefaultPageProps>) {

  const navigate = useNavigate();
  const [sidebar, setSidebar] = React.useState(DefaultSidebarData);
  const pageProps = {
      baseUrl: props.baseUrl,
      sidebar: sidebar,
      setSidebar: setSidebar,
      onGenerate: () => {
          navigate("/statblocks/" + sidebar.creatureType + "/" + sidebar.role + "/" + sidebar.cr);
      }
  }

  return (
    <PageLayout {...pageProps}>
      {props.children}
    </PageLayout>
  );
}