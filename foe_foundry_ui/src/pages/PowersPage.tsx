import React from "react";
import { PageLayout, PageProps } from "../components/PageLayout.tsx";
import "../css/statblocks.css";
import Markdown from "react-markdown";
import { Grid, Card, CardContent, Typography, Box } from "@mui/material";
import rehypeRaw from "rehype-raw";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";

interface Power {
  key: string;
  name: string;
  power_type: string;
  source: string;
  theme: string;
  power_level: string;
  features: Feature[];
  creature_types: string[];
  roles: string[];
  damage_types: string[];
}

interface Feature {
  name: string;
  action: string;
  recharge: number | null;
  uses: number | null;
  replaces_multiattack: number;
  modifies_attack: boolean;
  description_md: string;
}

const data: Power[] = [
  {
    key: "divine-smite",
    name: "Divine Smite",
    power_type: "Theme",
    source: "FoeFoundryOriginal",
    theme: "holy",
    power_level: "Medium Power",
    features: [
      {
        name: "Divine Smite",
        action: "BonusAction",
        recharge: 5,
        uses: null,
        replaces_multiattack: 0,
        modifies_attack: false,
        description_md:
          "Immediately after hitting a target, the leader forces the target to make a DC 14 Constitution saving throw. On a failure, the target is **Burning** [11 (2d10) radiant]. A burning creature suffers 11 (2d10) ongoing radiant damage at the start of each of its turns. A creature may use an action to end the condition.",
      },
    ],
    creature_types: ["humanoid"],
    roles: ["leader"],
    damage_types: ["radiant"],
  },
  {
    key: "divine-mercy",
    name: "Divine Mercy",
    power_type: "Creature",
    source: "FoeFoundryOriginal",
    theme: "Celestial",
    power_level: "Low Power",
    features: [
      {
        name: "Divine Mercy",
        action: "Reaction",
        recharge: null,
        uses: null,
        replaces_multiattack: 0,
        modifies_attack: false,
        description_md:
          "Whenever a creature that is within 60 feet of the celestial that can see or hear it is hit by an attack, fails a saving throw, or is reduced to 0 hitpoints,                 the celestial may offer divine mercy to that creature. If the creature accepts, it heals 15 hitpoints and the celestial may choose to end any negative conditions affecting that creature.                 The creature becomes **Charmed** by the celestial and follows its instructions to the best of its ability.                 Whenever the creature completes a long rest, it may make a DC 14 Charisma saving throw. On a success, the creature is no longer charmed.                 After three failures, the creature is permanently charmed and its alignment changes to match the celestial",
      },
    ],
    creature_types: ["celestial"],
    roles: [],
    damage_types: [],
  },
  {
    key: "divine-law",
    name: "Divine Law",
    power_type: "Creature",
    source: "FoeFoundryOriginal",
    theme: "Celestial",
    power_level: "High Power",
    features: [
      {
        name: "Divine Law",
        action: "Action",
        recharge: null,
        uses: 1,
        replaces_multiattack: 1,
        modifies_attack: false,
        description_md:
          "The celestial pronounces a divine law.                 Each humanoid creature within 60 feet that can hear the celestial must make DC 15 Charisma saving throw.                 A creature that worships the same deity or follows the same precepts as the celestial automatically fails this save.                 On a failure, the creature is bound by the divine law for 24 hours. On a success, the creature is immune to this effect for 24 hours.                 At the start of each of its turns, the affected creature may choose to break the divine law. If it does so, it suffers 24 (7d6) radiant damage and may repeat the save to end the effect.                  The game master may choose an appropriate divine law, or roll a d6 and select one of the following:                   <ol>                 <li>**Tranquility**: Affected creatures immediately end concentrating on any spells or abilities and may not cast a new spell that requires concentration.</li>                <li>**Peace**: Affected creatures may not wield weapons of a specified type. </li>                <li>**Forbiddance**: Affected creatures may not cast spells from a specified school of magic. </li>                <li>**Awe**: Affected creatures may not look upon any Celestial beings and are **Blinded** while within 60 feet of a Celestial. </li>                <li>**Adherance**: Affected creatures cannot take hostile actions towards creatures of a specified alignment</li>                <li>**Repentance**: Affected creatures must confess their darkest or most shameful transgressions or become **Stunned** for 1 minute. </li>                </ol>",
      },
    ],
    creature_types: ["celestial"],
    roles: [],
    damage_types: [],
  },
  {
    key: "word-of-radiance",
    name: "Word of Radiance",
    power_type: "Theme",
    source: "SRD 5.1 Word of Radiance",
    theme: "holy",
    power_level: "Medium Power",
    features: [
      {
        name: "Word of Radiance",
        action: "Action",
        recharge: null,
        uses: null,
        replaces_multiattack: 1,
        modifies_attack: false,
        description_md:
          "The leader utters a divine word and it shines with burning radiance.                 Each hostile creature within 10 feet must make a DC 14 Constitution saving throw or take 7 (2d6) radiant damage.",
      },
    ],
    creature_types: ["humanoid"],
    roles: ["leader"],
    damage_types: ["radiant"],
  },
  {
    key: "reject-divinity",
    name: "Reject Divinity",
    power_type: "Theme",
    source: "FoeFoundryOriginal",
    theme: "cursed",
    power_level: "High Power",
    features: [
      {
        name: "Reject Divinity",
        action: "Reaction",
        recharge: null,
        uses: null,
        replaces_multiattack: 0,
        modifies_attack: false,
        description_md:
          "When a creature the fey can see within 30 feet regains hit points from a Divine source,                 the fey reduces the number of hit points gained to 0                 and the fey instead deals 7 (2d6) necrotic damage to that creature.",
      },
    ],
    creature_types: ["fey", "fiend", "undead"],
    roles: ["leader", "controller"],
    damage_types: ["necrotic"],
  },
  {
    key: "cleric",
    name: "Cleric",
    power_type: "Theme",
    source: "FoeFoundryOriginal",
    theme: "class",
    power_level: "High Power",
    features: [
      {
        name: "Favored by the Gods",
        action: "Reaction",
        recharge: null,
        uses: 1,
        replaces_multiattack: 0,
        modifies_attack: false,
        description_md:
          "When the Cleric fails a saving throw or misses an attack it may add 2d4 to that result",
      },
      {
        name: "Word of Radiance",
        action: "Action",
        recharge: null,
        uses: null,
        replaces_multiattack: 1,
        modifies_attack: false,
        description_md:
          "The cleric utters a divine word and it shines with burning radiance.                 Each hostile creature within 10 feet must make a DC 14 Constitution saving throw or take 7 (2d6) radiant damage.",
      },
    ],
    creature_types: ["humanoid"],
    roles: [],
    damage_types: ["radiant"],
  },
  {
    key: "paladin",
    name: "Paladin",
    power_type: "Theme",
    source: "FoeFoundryOriginal",
    theme: "class",
    power_level: "High Power",
    features: [
      {
        name: "Inspiring Commander",
        action: "Action",
        recharge: null,
        uses: null,
        replaces_multiattack: 2,
        modifies_attack: false,
        description_md:
          "The humanoid inspires other creatures of its choice within 30 feet that can hear and understand it.                 For the next minute, inspired creatures gain a +2 bonus to attack rolls and saving throws.",
      },
      {
        name: "Divine Smite",
        action: "BonusAction",
        recharge: 5,
        uses: null,
        replaces_multiattack: 0,
        modifies_attack: false,
        description_md:
          "Immediately after hitting a target, the Paladin forces the target to make a DC 14 Constitution saving throw. On a failure, the target is **Burning** [5 (1d10) radiant]. A burning creature suffers 5 (1d10) ongoing radiant damage at the start of each of its turns. A creature may use an action to end the condition.",
      },
    ],
    creature_types: ["humanoid"],
    roles: [],
    damage_types: ["radiant"],
  },
];

function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function PowersGrid({ powers }: { powers: Power[] }) {
  return (
    <Grid container spacing={1}>
      {powers.map((power, index) => (
        <Grid item xs={12} sm={12} md={6} key={index}>
          <PowerCard power={power} />
        </Grid>
      ))}
    </Grid>
  );
}

function PowerCard({ power }: { power: Power }) {
  const tags = [
    ...power.creature_types,
    ...power.roles,
    ...power.damage_types,
  ].map((tag) => capitalize(tag));

  return (
    <Card
      variant="outlined"
      sx={{
        minHeight: {
          md: 300,
        },
      }}
    >
      <CardContent style={{ paddingBottom: "8px" }}>
        <Typography variant="h6" component="div">
          {power.name}
        </Typography>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 1,
            gridTemplateRows: "auto",
            gridTemplateAreas: `"theme power source"
            "tags tags tags"`,
          }}
        >
          <Box sx={{ gridArea: "theme" }}>
            <PowerProperty name="Theme" value={capitalize(power.theme)} />
          </Box>
          <Box sx={{ gridArea: "power" }}>
            <PowerProperty name="Power Level" value={power.power_level} />
          </Box>
          <Box sx={{ gridArea: "source" }}>
            <PowerProperty name="Source" value={power.source} />
          </Box>
          <Box sx={{ gridArea: "tags" }}>
            <PowerTags tags={tags} />
          </Box>
        </Box>
        <Box sx={{ marginTop: "0.5vh", marginBottom: "0.5vh" }}>
          <FeaturesBlock features={power.features} />
        </Box>
      </CardContent>
    </Card>
  );
}

function PowerProperty({ name, value }: { name: string; value: string }) {
  return (
    <>
      <Typography
        variant="body2"
        color="text.secondary"
        component="span"
        sx={{
          display: { xs: "none" },
        }}
      >
        {name}:{" "}
      </Typography>
      <Typography variant="body2" component="span">
        {value}
      </Typography>
    </>
  );
}

function PowerTags({ tags }: { tags: string[] }) {
  return (
    <Stack direction="row" spacing={1}>
      {tags.map((tag, index) => (
        <Chip key={index} label={tag} variant="outlined" />
      ))}
    </Stack>
  );
}

function FeaturesBlock({ features }: { features: Feature[] }) {
  const noActions = features.filter((feature) => feature.action === "Feature");
  const attacks = features.filter((feature) => feature.action === "Attack");
  const actions = features.filter((feature) => feature.action === "Action");
  const bonusActions = features.filter(
    (feature) => feature.action === "BonusAction"
  );
  const reactions = features.filter((feature) => feature.action === "Reaction");

  const groupedFeatures = [
    { header: undefined, features: noActions },
    { header: "Attacks", features: attacks },
    { header: "Actions", features: actions },
    { header: "Bonus Actions", features: bonusActions },
    { header: "Reactions", features: reactions },
  ];

  return (
    <div className="statblock">
      <div className="bar"></div>
      <ContentWrap>
        {groupedFeatures.map((grp, index) => (
          <FeatureGroup key={index} {...grp} />
        ))}
      </ContentWrap>
      <div className="bar"></div>
    </div>
  );
}

function FeatureGroup({
  key,
  header,
  features,
}: {
  key: string | number;
  header: string | undefined;
  features: Feature[];
}) {
  return (
    <div key={key}>
      {header && features.length > 0 && <ActionHeader name={header} />}
      {features.length > 0 &&
        features.map((feature, index) => (
          <FeatureBlock key={index} feature={feature} />
        ))}
    </div>
  );
}

function FeatureBlock({
  key,
  feature,
}: {
  key: string | number;
  feature: Feature;
}) {
  let name = "";
  if (feature.recharge === 6) {
    name = `${feature.name} (Recharge 6)`;
  } else if (feature.recharge) {
    name = `${feature.name} (Recharge ${feature.recharge}-6)`;
  } else if (feature.uses) {
    name = `${feature.name} (${feature.uses}/day)`;
  } else {
    name = feature.name;
  }

  const description_md = feature.description_md;
  return (
    <PropertyBlock key={key} name={name} description_md={description_md} />
  );
}

function PropertyBlock({
  name,
  description_md,
}: {
  name: string;
  description_md: string;
}) {
  return (
    <div className="property-line">
      <h4>{name}. </h4>
      <Markdown skipHtml={false} rehypePlugins={[rehypeRaw]}>
        {description_md}
      </Markdown>
    </div>
  );
}

function ActionHeader({ name }: { name: string }) {
  return <h3>{name}</h3>;
}

function ContentWrap({ children }: React.PropsWithChildren<{}>) {
  return <div className="content-wrap">{children}</div>;
}

export default function PowersPage(props: PageProps) {
  return (
    <PageLayout {...props}>
      <PowersGrid powers={data} />
    </PageLayout>
  );
}
