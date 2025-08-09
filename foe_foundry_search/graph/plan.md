# Plan for Mapping Custom Monsters to SRD Monsters

## Objective
Map each monster in the `data/5e_nl2` folder to the most similar D&D SRD monster(s) using the summaries in `srd_monsters.md`. Record the mapping in `monster_to_srd.json` as specified.

## Steps
1. **List Monsters**: Enumerate all JSON files in `data/5e_nl2` alphabetically.
2. **Load Monster Data**: For each monster, load its JSON object.
3. **Compare to SRD Monsters**: For each monster, compare its attributes, description, and abilities to the SRD monster summaries in `srd_monsters.md`.
4. **Determine Closest Match**: Decide which SRD monster(s) it most closely resembles. If none are a good match, record `null`.
5. **Record Mapping**: Add the mapping to `monster_to_srd.json` in the specified format.
6. **Proceed Alphabetically**: Work through the monsters in alphabetical order for easy tracking.
7. **Iterative Updates**: Update `monster_to_srd.json` incrementally as each mapping is completed.

## Notes
- Use monster names as keys and a list of SRD monster names (or `null`) as values.
- Refer to `srd_monsters.md` for SRD monster names and descriptions.
- If a monster is a variant or hybrid, list all relevant SRD monsters.
- If no SRD monster is similar, use `null`.
- Create sharded files by starting letter of the monster. For example, monster_to_srd_a_b.json
- Complete existing files before moving on to new ones
- Confirm that no monsters are missing before moving on to new ones

## Output
- `monster_to_srd_<start>_<end>.json`: The mapping file.
- This `plan.md`: Documents the approach for transparency and reproducibility.
