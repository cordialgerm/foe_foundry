import React from "react";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import { MonsterIcon } from "./MonsterIcons.tsx";

function capitalize(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export function CreateTypeSelector({
  value,
  onCreatureTypeChanged,
}: {
  value: string;
  onCreatureTypeChanged: (creatureType: string) => void;
}) {
  const onChange = (event) => {
    onCreatureTypeChanged(event.target.value);
  };

  const creatureTypes = [
    "aberration",
    "beast",
    "celestial",
    "construct",
    "dragon",
    "elemental",
    "fey",
    "fiend",
    "giant",
    "humanoid",
    "monstrosity",
    "ooze",
    "plant",
    "undead",
  ];

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
        {creatureTypes.map((creatureType) => (
          <MenuItem value={creatureType} key={creatureType}>
            <MonsterIcon iconType={creatureType} /> {capitalize(creatureType)}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

export function RoleSelector({
  value,
  onRoleChanged,
}: {
  value: string;
  onRoleChanged: (role: string) => void;
}) {
  const onChange = (event) => {
    onRoleChanged(event.target.value);
  };

  const roles = [
    "ambusher",
    "artillery",
    "bruiser",
    "controller",
    "defender",
    "leader",
    "skirmisher",
  ];

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
        {roles.map((role) => (
          <MenuItem value={role} key={role}>
            <MonsterIcon iconType={role} /> {capitalize(role)}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

export function CrSelector({
  value,
  onCrChanged,
}: {
  value: string;
  onCrChanged: (cr: string) => void;
}) {
  const onChange = (event) => {
    onCrChanged(event.target.value);
  };

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
        style={{ fontSize: "14px" }}
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
