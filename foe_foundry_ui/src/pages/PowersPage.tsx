import React from "react";
import { PageLayout, PageProps } from "../components/PageLayout.tsx";
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
  Tabs,
  Tab,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import {
  Feature,
  ContentWrap,
  FeatureGroup,
} from "../components/StatblockPieces.tsx";
import useStickyState from "../components/StickyState.tsx";
import { useParams, useSearchParams } from "react-router-dom";

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
  tags: string[];
}

function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function PowersPage(props: PageProps) {
  const { tab } = useParams();

  const tabs = ["new", "search", "random"];
  const initialValue = tab ? tabs.indexOf(tab) ?? 0 : 0;
  const [value, setValue] = useStickyState(initialValue, "powersTab");

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    const newTab = tabs[newValue];
    window.history.pushState(null, "", "/powers/" + newTab);
    setValue(newValue);
  };

  return (
    <PageLayout {...props}>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={value} onChange={handleChange}>
          <Tab label="New Powers" id="tab-new-powers" />
          <Tab label="Search Powers" id="tab-search-powers" />
          <Tab label="Random Powers" id="tab-random-powers" />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <NewPowers baseUrl={props.baseUrl} />
      </TabPanel>
      <TabPanel value={value} index={1}>
        <SearchPowers baseUrl={props.baseUrl} />
      </TabPanel>
      <TabPanel value={value} index={2}>
        <RandomPowers baseUrl={props.baseUrl} />
      </TabPanel>
    </PageLayout>
  );
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`vertical-tabpanel-${index}`}
      aria-labelledby={`vertical-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 0.5 }}>{children}</Box>}
    </div>
  );
}

function NewPowers({ baseUrl }: { baseUrl: string }) {
  const [powers, setPowers] = React.useState<Power[]>([]);

  const fetchData = React.useCallback(async () => {
    const url =
      `${baseUrl}/api/v1/powers/new?` + new URLSearchParams({ limit: "20" });
    const response = await fetch(url);
    const powers = await response.json();
    setPowers(powers);
  }, [baseUrl]);

  React.useEffect(() => {
    fetchData().catch(console.error);
  }, [fetchData]);

  return (
    <Box padding={1}>
      <Stack direction="row">
        <Typography
          variant="h5"
          component="h2"
          style={{ margin: "5px", marginLeft: "10px" }}
        >
          New Powers
        </Typography>
      </Stack>
      {powers.length > 0 && <PowersGrid powers={powers} />}
    </Box>
  );
}

function RandomPowers({ baseUrl }: { baseUrl: string }) {
  const [powers, setPowers] = React.useState<Power[]>([]);

  const fetchData = React.useCallback(async () => {
    const url =
      `${baseUrl}/api/v1/powers/random?` + new URLSearchParams({ limit: "6" });
    const response = await fetch(url);
    const powers = await response.json();
    setPowers(powers);
  }, [baseUrl]);

  React.useEffect(() => {
    fetchData().catch(console.error);
  }, [fetchData]);

  return (
    <Box padding={1}>
      <Stack direction="row">
        <Typography
          variant="h5"
          component="h2"
          style={{ margin: "5px", marginLeft: "10px" }}
        >
          Random Powers
        </Typography>
      </Stack>
      {powers.length > 0 && <PowersGrid powers={powers} />}
    </Box>
  );
}

function SearchPowers({ baseUrl }: { baseUrl: string }) {
  const [searchParams, setSearchParams] = useSearchParams();

  const searchQuery = searchParams.get("keyword") ?? "";

  const [powers, setPowers] = React.useState<Power[]>([]);
  const [searchBarText, setSearchBarText] = React.useState(searchQuery);

  const handleSearchBarTextChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setSearchBarText(event.target.value);
  };

  const handleSearchBarSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSearchParams({ keyword: searchBarText });
  };

  const handleSearchBarButtonClick = () => {
    setSearchParams({ keyword: searchBarText });
  };

  const fetchData = React.useCallback(async () => {
    if (searchQuery === "") return;

    const url =
      `${baseUrl}/api/v1/powers/search?` +
      new URLSearchParams({ keyword: searchQuery, limit: "40" });
    const response = await fetch(url);
    const powers = await response.json();
    setPowers(powers);
  }, [baseUrl, searchQuery]);

  React.useEffect(() => {
    fetchData().catch(console.error);
  }, [fetchData]);

  return (
    <Box padding={1}>
      <Stack direction="row">
        <Typography
          variant="h5"
          component="h2"
          style={{ margin: "5px", marginLeft: "10px" }}
        >
          Search for Powers
        </Typography>
        <form onSubmit={handleSearchBarSubmit}>
          <TextField
            label="Search Powers"
            placeholder="Search Powers..."
            variant="outlined"
            size="small"
            value={searchBarText}
            onChange={handleSearchBarTextChange}
          />
          <IconButton
            type="submit"
            aria-label="search"
            onClick={handleSearchBarButtonClick}
          >
            <SearchIcon />
          </IconButton>
        </form>
      </Stack>
      {powers.length > 0 && <PowersGrid powers={powers} />}
      {powers.length === 0 && <NoContent searchQuery={searchQuery} />}
    </Box>
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
            <PowerTags tags={power.tags} />
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

//This is a "fake" statblock just to show the listed features
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
          <FeatureGroup {...grp} />
        ))}
      </ContentWrap>
      <div className="bar"></div>
    </div>
  );
}
