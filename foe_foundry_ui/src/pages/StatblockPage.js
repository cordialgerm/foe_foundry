import * as React from 'react';

import { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles'

import { CssBaseline } from '@mui/material';
import { FoeFoundryAppBar } from '../components/AppBar.js';
import { PersistentDrawerLeft } from '../components/Drawer.js';
import { RandomStatblock } from '../components/Statblock.js'
import { Main } from '../components/Main.js'
import { RandomBackgroundImage } from '../components/Background.js';
import theme from '../components/Theme.js';


function StatblockPage({ baseUrl }) {

  const [drawerOpen, setDrawerOpen] = useState(true);
  const [refreshCount, setRefreshCount] = useState(0)
  const [creatureType, setCreatureType] = useState("humanoid")
  const [role, setRole] = useState("bruiser")
  const [cr, setCr] = useState("specialist")

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <FoeFoundryAppBar drawerOpen={drawerOpen} setDrawerOpen={setDrawerOpen} />
      <PersistentDrawerLeft
        open={drawerOpen} setOpen={setDrawerOpen}
        creatureType={creatureType} setCreatureType={setCreatureType}
        role={role} setRole={setRole}
        cr={cr} setCr={setCr}
        refreshCount={refreshCount} setRefreshCount={setRefreshCount} />
      <Main open={drawerOpen}>
        <RandomBackgroundImage creatureType={creatureType} counter={refreshCount}>
          <RandomStatblock baseUrl={baseUrl} creatureType={creatureType} role={role} cr={cr} counter={refreshCount} />
        </RandomBackgroundImage>
      </Main>
    </ThemeProvider>
  );
}



export default StatblockPage;
