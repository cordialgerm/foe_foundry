import './App.css';
import * as React from 'react'
import { useState } from 'react';
import { InputLabel, FormControl, Select, MenuItem, Button, Paper, Stack, Container } from '@mui/material';

function App() {

  const [refreshCount, setRefreshCount] = useState(0)
  const [creatureType, setCreatureType] = useState("humanoid")
  const [role, setRole] = useState("bruiser")
  const [cr, setCr] = useState("specialist")

  const onCreatureTypeChanged = event => {
    setCreatureType(event.target.value);
  }

  const onRoleChanged = event => {
    setRole(event.target.value)
  }

  const onCrChanged = event => {
    setCr(event.target.value)
  }

  const onGenerateClicked = event => {
    console.log("refreshCount", refreshCount)
    setRefreshCount(refreshCount + 1)
  }

  return (
    <div className="App">
      <Container>
        <Paper elevation={0} variant="outlined" style={{ paddingLeft: 30, paddingRight: 30, paddingBottom: 30 }}>
          <h2>Foe Foundry</h2>
          <Stack>
            <CreateTypeSelector value={creatureType} onChange={onCreatureTypeChanged} />
            <RoleSelector value={role} onChange={onRoleChanged} />
            <CrSelector value={cr} onChange={onCrChanged} />
            <Button variant="contained" onClick={onGenerateClicked}>Generate Random Monster</Button>
          </Stack>
        </Paper>
      </Container>
      <Container>
        <RandomStatblock creatureType={creatureType} role={role} cr={cr} counter={refreshCount} />
      </Container>
    </div >
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
  const src = `https://cordialgerm87.pythonanywhere.com/statblocks/random/${creatureType}/${role}/${cr}`
  const id = `${creatureType}/${role}/${cr}-${counter}`
  return (
    <div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100vh" }}>
      <iframe key={id} id={id} title="statblock" src={src} style={{ borderWidth: "0px", flex: "1 1 auto" }}></iframe>
    </div>
  )
}

export default App;
