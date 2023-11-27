import { MenuItem, FormControl, InputLabel, Select } from "@mui/material";

export function CreateTypeSelector({ value, onChange }) {
  return (
    <FormControl style={{ padding: 15, width: "200px" }}>
      <InputLabel id="creature-type-select-label">Creature Type</InputLabel>
      <Select
        labelId="creature-type-select-label"
        id="creature-type-select"
        value={value}
        onChange={onChange}
        autoWidth
        label="Creature Type"
      >
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
        <MenuItem value="monstrosity">Monstrosity</MenuItem>
        <MenuItem value="ooze">Ooze</MenuItem>
        <MenuItem value="plant">Plant</MenuItem>
        <MenuItem value="undead">Undead</MenuItem>
      </Select>
    </FormControl>
  );
}

export function RoleSelector({ value, onChange }) {
  return (
    <FormControl style={{ padding: 15, width: "200px" }}>
      <InputLabel id="monster-role-select-label">Monster Role</InputLabel>
      <Select
        labelId="monster-role-select-label"
        id="monster-role-select"
        value={value}
        onChange={onChange}
        autoWidth
        label="Monster Role"
      >
        <MenuItem value="ambusher">Ambusher</MenuItem>
        <MenuItem value="artillery">Artillery</MenuItem>
        <MenuItem value="bruiser">Bruiser</MenuItem>
        <MenuItem value="controller">Controller</MenuItem>
        <MenuItem value="defender">Defender</MenuItem>
        <MenuItem value="leader">Leader</MenuItem>
        <MenuItem value="skirmisher">Skirmisher</MenuItem>
      </Select>
    </FormControl>
  );
}

export function CrSelector({ value, onChange }) {
  return (
    <FormControl style={{ padding: 15, width: "200px" }}>
      <InputLabel id="cr-select-label">Challenge Rating (CR)</InputLabel>
      <Select
        labelId="cr-select-label"
        id="cr-select"
        value={value}
        onChange={onChange}
        autoWidth
        label="Challenge Rating"
      >
        <MenuItem value="minion">Minion (CR 1/8)</MenuItem>
        <MenuItem value="soldier">Soldier (CR 1/2) </MenuItem>
        <MenuItem value="brute">Brute (CR 2)</MenuItem>
        <MenuItem value="specialist">Specialist (CR 4)</MenuItem>
        <MenuItem value="myrmidon">Myrmidon (CR 7)</MenuItem>
        <MenuItem value="sentinel">Sentinel (CR 11)</MenuItem>
        <MenuItem value="champion">Champion (CR 15)</MenuItem>
      </Select>
    </FormControl>
  );
}
