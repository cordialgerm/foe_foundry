import * as React from 'react'
import { styled, useTheme, ThemeProvider, createTheme } from '@mui/material/styles';

import { useState, useEffect } from 'react';

import { InputLabel, Toolbar, Typography, Paper, FormControl, Select, MenuItem, Container, Drawer, Divider, List, ListItem, ListItemIcon, ListItemButton, ListItemText, AppBar, CssBaseline } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ConstructionIcon from '@mui/icons-material/Construction';
import LoopIcon from '@mui/icons-material/Loop';


const drawerWidth = 240

const customTheme = createTheme({});


const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

const MuiAppBar = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth - 10}px`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    flexGrow: 1,
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: `-${drawerWidth}px`,
    ...(open && {
      transition: theme.transitions.create('margin', {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen,
      }),
      marginLeft: 0,
    }),
  }),
);

function MyAppBar({ drawerOpen, setDrawerOpen }) {

  const handleDrawerOpen = () => {
    setDrawerOpen(true);
  }

  return (
    <MuiAppBar position="static" open={drawerOpen}>
      <Container>
        <Toolbar disableGutters>
          {!drawerOpen &&
            (<IconButton onClick={handleDrawerOpen}>
              <MenuIcon />
            </IconButton>)
          }
          <ConstructionIcon style={{ marginRight: "10px" }} />
          <Typography
            variant="h6"
            noWrap
            component="a"
            sx={{
              mr: 2,
              display: { xs: 'none', md: 'flex' },
              fontFamily: 'monospace',
              fontWeight: 700,
              letterSpacing: '.2rem',
              color: 'inherit',
              textDecoration: 'none',
            }}>
            Foe Foundry
          </Typography>
        </Toolbar>
      </Container>
    </MuiAppBar>
  );
}

function PersistentDrawerLeft({ creatureType, setCreatureType, role, setRole, cr, setCr, refreshCount, setRefreshCount, open, setOpen }) {
  const theme = useTheme();

  const handleDrawerClose = () => {
    setOpen(false);
  }

  const onCreatureTypeChanged = event => {
    setCreatureType(event.target.value);
  }

  const onRoleChanged = event => {
    setRole(event.target.value)
  }

  const onCrChanged = event => {
    setCr(event.target.value)
  }

  const onRefreshClicked = event => {
    setRefreshCount(refreshCount + 1)
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      width={drawerWidth}
      elevation={3}
      open={open}>
      <DrawerHeader>
        <IconButton onClick={handleDrawerClose}>
          {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </DrawerHeader>
      <Divider />
      <List>
        <ListItem key="creatureTyp">
          <CreateTypeSelector value={creatureType} onChange={onCreatureTypeChanged} />
        </ListItem>
        <ListItem key="role">
          <RoleSelector value={role} onChange={onRoleChanged} />
        </ListItem>
        <ListItem key="cr">
          <CrSelector value={cr} onChange={onCrChanged} />
        </ListItem>
        <ListItem key="refresh">
          <ListItemButton onClick={onRefreshClicked} variant="contained">
            <ListItemIcon>
              <LoopIcon />
            </ListItemIcon>
            <ListItemText primary="Refresh" />
          </ListItemButton>
        </ListItem>
      </List>
    </Drawer>
  )
}


function App() {

  const [drawerOpen, setDrawerOpen] = useState(true);
  const [refreshCount, setRefreshCount] = useState(0)
  const [creatureType, setCreatureType] = useState("humanoid")
  const [role, setRole] = useState("bruiser")
  const [cr, setCr] = useState("specialist")

  return (
    <ThemeProvider theme={customTheme}>
      <CssBaseline />
      <MyAppBar drawerOpen={drawerOpen} setDrawerOpen={setDrawerOpen} />
      <PersistentDrawerLeft
        open={drawerOpen} setOpen={setDrawerOpen}
        creatureType={creatureType} setCreatureType={setCreatureType}
        role={role} setRole={setRole}
        cr={cr} setCr={setCr}
        refreshCount={refreshCount} setRefreshCount={setRefreshCount} />
      <Main open={drawerOpen}>
        <Paper elevation={1}>
          <RandomStatblock creatureType={creatureType} role={role} cr={cr} counter={refreshCount} />
        </Paper>
      </Main>
    </ThemeProvider>
  );
}

function CreateTypeSelector({ value, onChange }) {
  return (
    <FormControl style={{ padding: 15 }}>
      <InputLabel id="creature-type-select-label">Creature Type</InputLabel>
      <Select labelId="creature-type-select-label"
        id="creature-type-select"
        value={value}
        onChange={onChange}
        autoWidth
        label="Creature Type">
        <MenuItem value="aberration">Aberration</MenuItem>
        <MenuItem value="beast">Beast</MenuItem>
        <MenuItem value="celestial">Celestial</MenuItem>
        <MenuItem value="construct">Construct</MenuItem>
        <MenuItem value="dragon">Dragon</MenuItem>
        <MenuItem value="elemental">Elemental</MenuItem>
        <MenuItem value="fey">Fey</MenuItem>
        <MenuItem value="fiend">Fiend</MenuItem>
        <MenuItem value="giant">Giant</MenuItem>
        <MenuItem value="humanoid">Humanoid</MenuItem>
        <MenuItem value="monstrosity">monstrosity</MenuItem>
        <MenuItem value="ooze">Ooze</MenuItem>
        <MenuItem value="plant">Plant</MenuItem>
        <MenuItem value="undead">Undead</MenuItem>
      </Select>
    </FormControl>
  )
}

function RoleSelector({ value, onChange }) {
  return (
    <FormControl style={{ padding: 15 }}>
      <InputLabel id="monster-role-select-label">Monster Role</InputLabel>
      <Select labelId="monster-role-select-label"
        id="monster-role-select"
        value={value}
        onChange={onChange}
        autoWidth
        label="Monster Role">
        <MenuItem value="ambusher">Ambusher</MenuItem>
        <MenuItem value="artillery">Artillery</MenuItem>
        <MenuItem value="bruiser">Bruiser</MenuItem>
        <MenuItem value="controller">Controller</MenuItem>
        <MenuItem value="defender">Defender</MenuItem>
        <MenuItem value="leader">Leader</MenuItem>
        <MenuItem value="skirmisher">Skirmisher</MenuItem>
      </Select>
    </FormControl>
  )
}

function CrSelector({ value, onChange }) {
  return (
    <FormControl style={{ padding: 15 }}>
      <InputLabel id="cr-select-label">Challenge Rating (CR)</InputLabel>
      <Select labelId="cr-select-label"
        id="cr-select"
        value={value}
        onChange={onChange}
        autoWidth
        label="Challenge Rating">
        <MenuItem value="minion">Minion (CR 1/8)</MenuItem>
        <MenuItem value="soldier">Soldier (CR 1/2) </MenuItem>
        <MenuItem value="brute">Brute (CR 2)</MenuItem>
        <MenuItem value="specialist">Specialist (CR 4)</MenuItem>
        <MenuItem value="myrmidon">Myrmidon (CR 7)</MenuItem>
        <MenuItem value="sentinel">Sentinel (CR 11)</MenuItem>
        <MenuItem value="champion">Champion (CR 15)</MenuItem>
      </Select>
    </FormControl>
  )
}

function RandomStatblock({ creatureType, role, cr, counter }) {
  const url = `http://127.0.0.1:8080/statblocks/random/${creatureType}/${role}/${cr}?render=partial`
  const id = `${creatureType}-${role}-${cr}-${counter}`

  const [state, setState] = useState({ loaded: false, rawHtml: "loading..." })

  useEffect(() => {
    let ignore = false;

    async function startFetching() {
      const response = await fetch(url)
      const rawHtml = await response.text()
      if (!ignore) {
        setState({ loaded: true, rawHtml: rawHtml })
      }
    }

    startFetching();

    return () => {
      ignore = true;
    };
  }, [creatureType, role, cr, counter, url]);

  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100vh", textAlign: "left", padding: "20px", marginLeft: drawerWidth }}>
      <div key={id} id={id} dangerouslySetInnerHTML={{ __html: state.rawHtml }} style={{ color: "black" }} />
    </div>
  )
}


export default App;
