import React from "react";
import { PageLayout, PageProps } from "../components/PageLayout.tsx";
import "../css/statblocks.css";
import Markdown from "react-markdown";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  IconButton,
  Stack,
  Chip,
} from "@mui/material";
import rehypeRaw from "rehype-raw";
import SearchIcon from "@mui/icons-material/Search";

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
    ...new Set(
      [
        ...[power.theme],
        ...power.creature_types,
        ...power.roles,
        ...power.damage_types,
      ].map((tag) => capitalize(tag))
    ),
  ];
  tags.sort();

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
    <Stack direction="row" flexWrap="wrap" spacing={1}>
      {tags.map((tag, index) => (
        <Chip key={index} label={tag} variant="filled" />
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

function SearchBar({
  setSearchQuery,
}: {
  setSearchQuery: (query: string) => void;
}) {
  const [searchText, setSearchText] = React.useState("");

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(event.target.value);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSearchQuery(searchText);
  };

  const handleClick = () => {
    setSearchQuery(searchText);
  };

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        label="Search Powers"
        placeholder="Search Powers..."
        variant="outlined"
        size="small"
        value={searchText}
        onChange={handleChange}
      />
      <IconButton type="submit" aria-label="search" onClick={handleClick}>
        <SearchIcon />
      </IconButton>
    </form>
  );
}

function NoContent({ searchQuery }: { searchQuery: string }) {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", m: 1, p: 1 }}>
      <Typography variant="h5" textAlign="center" sx={{ flexGrow: 1 }}>
        No powers found matching '{searchQuery}'
      </Typography>
    </Box>
  );
}

export default function PowersPage(props: PageProps) {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [powers, setPowers] = React.useState<Power[]>([]);
  const firstLoad = React.useRef(true);

  const baseUrl = `${props.baseUrl}/api/v1/powers`;

  const fetchData = React.useCallback(async () => {
    const url = firstLoad.current
      ? `${baseUrl}/random?` + new URLSearchParams({ limit: "4" })
      : `${baseUrl}/search?` + new URLSearchParams({ keyword: searchQuery });
    firstLoad.current = false;
    const response = await fetch(url);
    const powers = await response.json();
    setPowers(powers);
  }, [baseUrl, firstLoad, searchQuery]);

  React.useEffect(() => {
    fetchData().catch(console.error);
  }, [fetchData]);

  return (
    <PageLayout {...props}>
      <Box padding={1}>
        <Stack direction="row">
          <Typography
            variant="h5"
            component="h2"
            style={{ margin: "5px", marginLeft: "10px" }}
          >
            Powers
          </Typography>
          <SearchBar setSearchQuery={setSearchQuery} />
        </Stack>
        {powers.length > 0 && <PowersGrid powers={powers} />}
        {powers.length === 0 && <NoContent searchQuery={searchQuery} />}
      </Box>
    </PageLayout>
  );
}
