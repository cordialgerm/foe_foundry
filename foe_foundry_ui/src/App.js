import * as React from 'react';

import { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles'

import { CssBaseline } from '@mui/material';
import { FoeFoundryAppBar } from './AppBar.js';
import { PersistentDrawerLeft } from './Drawer.js';
import { RandomStatblock } from './Statblock.js'
import { Main } from './Main.js'
import { RandomBackgroundImage } from './Background.js';
import theme from './Theme.js';


function App({ baseUrl }) {

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
        <RandomBackgroundImage counter={refreshCount}>
          <RandomStatblock baseUrl={baseUrl} creatureType={creatureType} role={role} cr={cr} counter={refreshCount} />
        </RandomBackgroundImage>
      </Main>
    </ThemeProvider>
  );
}



export default App;
