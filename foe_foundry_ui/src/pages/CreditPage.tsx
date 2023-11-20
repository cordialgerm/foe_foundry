
import React from 'react';
import { Button, styled } from '@mui/material';
import { Grid, Card, CardContent, Typography, CardActions } from '@mui/material';
import  { DefaultPageLayout } from '../components/PageLayout.tsx';
import {Dazed, Burning, Shocked, Frozen, Fatigue} from '../components/Condition.tsx';

interface CreditPageProps {
    baseUrl: string;
}

interface CreditProps {
  title: string;
  description: JSX.Element;
  url?: string;
  imageUrl?: string;
  actionText?: string;
}

interface CreditGridProps {
  credits: CreditProps[];
}

const inspirationCredits = [
  {
    title: "Forge of Foes",
    url: "https://slyflourish.com/build_a_quick_monster_with_forge_of_foes.html",
    imageUrl: "https://slyflourish.com/images/fof_cover_300w.jpg",
    description:
      <span>
        <a href="https://slyflourish.com/build_a_quick_monster_with_forge_of_foes.html"><i>Forge of Foes</i></a> by Teos Abadia, Scott Fitzgerald Gray, and Michael Shea is a wonderful book to help GMs create quick and easy monsters and run challenging and fun encounters. It serves as inspiration for many of the powers and ideas in <b>Foe Foundry</b>. I highly encourage you to check it out!
      </span>,
    actionText: "Buy Forge of Foes"
  },
  {
    title: "Level Up: Advanced 5th Edition",
    url: "https://www.levelup5e.com/",
    description:
    <span>
      <a href="https://www.levelup5e.com/"><b>A5e</b></a> has a wonderful <i>Monstrous Menagerie</i> that re-imagines many of the monsters in the 5E SRD. <b>Foe Foundry</b> takes inspiration from many of the monster designs and monster-building guidelines.
    </span>,
    actionText: "Buy Level Up: Advanced 5th Edition"
  },
  {
    title: 'DungeonDudes',
    url: "https://www.patreon.com/dungeon_dudes/posts",
    description: <span>
      <b>Foe Foundry</b> utilizes some new conditions, including <Dazed />, <Burning />, <Shocked />, <Frozen />, and <Fatigue />.
      Inspiration for these powers comes from the <a href="https://www.patreon.com/dungeon_dudes/posts">DungeonDudes</a>.
      In particular, this YouTube video <a href="https://youtu.be/Bq2Dz-EETJs?si=x94Allggu79ECGy3">Homebrewing New Conditions for D&D 5e</a>
    </span>,
    actionText: "Support the DungeonDudes on Patreon"
  },
  {
    title: "Disease Powers from CrunchyDM",
    url: "https://www.patreon.com/crunchydm/posts",
    description: <span>
      Several of the disease powers are inspired by very vicious disease-laden spiders that <a href="https://www.patreon.com/crunchydm/posts">CrunchyDM</a> threw against me and my fellow PCs in one of our games. They put the fear of Nurgle in our hearts and I thought other players would enjoy that experience as well.
    </span>,
    actionText: "Support CrunchyDM on Patreon"
  },
  {
    title: "Creative Anti-Magic Monster Design",
    url: "https://www.reddit.com/r/onednd/comments/17gw8he/monster_design_a_way_to_balance_castersmartials/",
    description: <span>
      Several of the anti-magic monster powers are inspirted by a reddit post by <b>u/Juls7243</b> to r/onednd about <a href="https://www.reddit.com/r/onednd/comments/17gw8he/monster_design_a_way_to_balance_castersmartials/">creative anti-magic monster design</a>
    </span>,
    actionText: "Read the Reddit Post"
  }
];

const artCredits = [
  {
    title: "Midjourney AI",
    description: <span>The background images used in this site were generated using <a href="https://www.midjourney.com/">Midjourney</a></span>
  },
  {
    title: "Watercolor Mask",
    description: <span><a href="https://www.freepik.com/free-vector/abstract-grunge-banners-with-your-test-vector-illustration_25979458.htm?query=watercolor mask border">Image by Rochak Shukla</a> on Freepik</span>
  }
]

const legalNotices = [
  {
    title: "SRD 5.1 Notice",
    description: <span>This work includes material taken from the System Reference Document 5.1 (“SRD 5.1”) by Wizards of the Coast LLC and available at <a href="https://dnd.wizards.com/resources/systems-reference-document">https://dnd.wizards.com/resources/systems-reference-document</a>. The SRD 5.1 is licensed under the Creative Commons Attribution 4.0 International License available at <a href="https://creativecommons.org/licenses/by/4.0/legalcode">https://creativecommons.org/licenses/by/4.0/legalcode</a>.</span>
  },
  {
    title: "A5E SRD Notice",
    description: <span>This work includes material taken from the A5E System Reference Document (A5ESRD) by EN Publishing and available at A5ESRD.com, based on Level Up: Advanced 5th Edition, available at <a href="www.levelup5e.com">www.levelup5e.com</a>. The A5ESRD is licensed under the Creative Commons Attribution 4.0 International License available at <a href="https://creativecommons.org/licenses/by/4.0/legalcode">https://creativecommons.org/licenses/by/4.0/legalcode</a>.</span>
  },
  {
    title: "Lazy GM's 5e Monster Builder Resource Document Notice",
    description: <span>This work includes material taken from the <a href="https://slyflourish.com/lazy_5e_monster_building_resource_document.html">Lazy GM's 5e Monster Builder Resource Document</a> written by Teos Abadía of <a href="https://alphastream.org">Alphastream.org</a>, Scott Fitzgerald Gray of <a href="https://insaneangel.com">Insaneangel.com</a>, and Michael E. Shea of <a href="https://slyflourish.com">SlyFlourish.com</a>, available under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.</span>
  },
  {
    title: "Lazy GM's Resource Document Notice",
    description: <span>This work includes material taken from the <a href="https://slyflourish.com/lazy_gm_resource_document.html">Lazy GM's Resource Document</a> by Michael E. Shea of <a href="https://slyflourish.com">SlyFlourish.com</a>, available under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.</span>
  }
]

function Credit(credit: React.PropsWithChildren<CreditProps>) {

  return (
    <Card elevation={2} style={{margin: "10px", display: "flex", flexDirection: "column", minHeight: "210px"}}>
      <CardContent style={{flexGrow: 1}}>
        <Typography variant="h6" component="div">
          {credit.title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {credit.description}
        </Typography>
      </CardContent>
      { credit.url &&
      <CardActions>
        <Button href={credit.url} target="_new" size="small">{credit.actionText ?? "Learn More"}</Button>
      </CardActions>
      }
  </Card>
  )
}

function Header(props: React.PropsWithChildren) {
  return (
    <Typography variant="h5" component="h2" style={{margin: "5px", marginLeft: "10px"}}>
      {props.children}
    </Typography>
  )
}

function CreditGrid(props: CreditGridProps){
  return (
    <Grid container spacing={2}>
        {props.credits.map((credit, index) => (
          <Grid item xs={12} sm={6} md={6} lg={4} key={index}>
            <Credit {...credit} />
          </Grid>
        ))}
      </Grid>
  )
}

function CreditPage(props: React.PropsWithChildren<CreditPageProps>) {

  return (
    <DefaultPageLayout {...props}>
      <Header>Acknowledgements</Header>
      <CreditGrid credits={inspirationCredits} />
      <Header>Art Credits</Header>
      <CreditGrid credits={artCredits} />
      <Header>Legal Notices</Header>
      <CreditGrid credits={legalNotices} />
    </DefaultPageLayout>
  );
};

export default CreditPage;
