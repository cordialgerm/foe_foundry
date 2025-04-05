import React from "react";
import { Button } from "@mui/material";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  CardActions,
  CardMedia,
} from "@mui/material";
import { PageLayout, PageProps } from "../components/PageLayout.tsx";
import {
  Dazed,
  Burning,
  Shocked,
  Frozen,
  Fatigue,
} from "../components/Condition.tsx";
import { OglCopyrightNotice } from "./OglPage.tsx";
import { Link } from "react-router-dom";
import { IconCredits } from "../components/MonsterIcons.tsx";

interface CreditProps {
  title: string;
  description: JSX.Element;
  url?: string;
  imageUrl?: string;
  actionText?: string;
  notice?: string;
  fontSize?: string;
}

interface CreditGridProps {
  credits: CreditProps[];
  fontSize?: string;
}

const inspirationCredits = [
  {
    title: "Forge of Foes",
    url: "https://slyflourish.com/build_a_quick_monster_with_forge_of_foes.html",
    imageUrl: "https://slyflourish.com/images/fof_cover_300w.jpg",
    description: (
      <span>
        <a href="https://slyflourish.com/build_a_quick_monster_with_forge_of_foes.html">
          <i>Forge of Foes</i>
        </a>{" "}
        by Teos Abadia, Scott Fitzgerald Gray, and Michael Shea is a wonderful
        book to help GMs create quick and easy monsters and run challenging and
        fun encounters. It serves as inspiration for many of the powers and
        ideas in <b>Foe Foundry</b>. I highly encourage you to check it out!
      </span>
    ),
    notice:
      "This project is not affiliated with Sly Flourish or the authors of Forge of Foes. Book titles and image copyrights belong to their respective holders.",
    actionText: "Buy Forge of Foes",
  },
  {
    title: "Level Up: Advanced 5th Edition",
    url: "https://www.levelup5e.com/",
    imageUrl:
      "https://images.squarespace-cdn.com/content/v1/5f30140933f50e61c794e1a3/1629827625546-DZJZ3FYLE9JQDVMWT1TQ/mediamodifier_image-7.png?format=1500w",
    description: (
      <span>
        <a href="https://www.levelup5e.com/">
          <b>A5e</b>
        </a>{" "}
        has a wonderful <i>Monstrous Menagerie</i> that re-imagines many of the
        monsters in the 5E SRD. <b>Foe Foundry</b> takes inspiration from many
        of the monster designs and monster-building guidelines.
      </span>
    ),
    notice:
      "This project is not affiliated with EN Publishing or the authors of Level Up: Advanced 5th Edition. Book titles and image copyrights belong to their respective holders.",
    actionText: "Buy Level Up: Advanced 5th Edition",
  },
  {
    title: "DungeonDudes",
    url: "https://www.patreon.com/dungeon_dudes/posts",
    imageUrl:
      "https://c10.patreonusercontent.com/4/patreon-media/p/campaign/1023986/6df849009bfc4ff6806d3dbb866b5432/eyJ3IjoxMjAwLCJ3ZSI6MX0%3D/4.png?token-time=1701648000&token-hash=WGOLlYurn1T_aYUf_j5Iqp6wnrGiT56R87goQz-Sc1s%3D",
    description: (
      <span>
        <b>Foe Foundry</b> utilizes some new conditions, including <Dazed />,{" "}
        <Burning />, <Shocked />, <Frozen />, and <Fatigue />. Inspiration for
        these powers comes from the{" "}
        <a href="https://www.patreon.com/dungeon_dudes/posts">DungeonDudes</a>.
        In particular, this YouTube video{" "}
        <a href="https://youtu.be/Bq2Dz-EETJs?si=x94Allggu79ECGy3">
          Homebrewing New Conditions for D&D 5e
        </a>
      </span>
    ),
    notice:
      "This project is not affiliated with The DungeonDudes. Image copyrights belong to their respective holders.",
    actionText: "Support the DungeonDudes on Patreon",
  },
  {
    title: "Disease Powers from CrunchyDM",
    url: "https://www.patreon.com/crunchydm/posts",
    description: (
      <span>
        Several of the disease powers are inspired by very vicious disease-laden
        spiders that{" "}
        <a href="https://www.patreon.com/crunchydm/posts">CrunchyDM</a> threw
        against me and my fellow PCs in one of our games. They put the fear of
        the God of Decay into our hearts and I thought other players would enjoy
        that experience as well.
      </span>
    ),
    actionText: "Support CrunchyDM on Patreon",
  },
  {
    title: "Creative Anti-Magic Monster Design",
    url: "https://www.reddit.com/r/onednd/comments/17gw8he/monster_design_a_way_to_balance_castersmartials/",
    description: (
      <span>
        Several of the anti-magic monster powers are inspirted by a reddit post
        by <b>u/Juls7243</b> to r/onednd about{" "}
        <a href="https://www.reddit.com/r/onednd/comments/17gw8he/monster_design_a_way_to_balance_castersmartials/">
          creative anti-magic monster design
        </a>
      </span>
    ),
    actionText: "Read the Reddit Post",
  },
];

const artCredits = [
  {
    title: "Icons from Game-Icons.net",
    description: <IconCredits />,
  },
  {
    title: "Watercolor Monster Pack",
    description: "Watercolor Monster Pack by metalsnail",
    url: "https://metalsnail.itch.io/watercolour-monster-pack",
  },
  {
    title: "Monsters by GalefireRPG",
    description: (
      <>
        <ul>
          <a href="https://galefirerpg.itch.io/fantasy-beasts-monster-pack">
            Fantasy Beasts Monster Pack
          </a>
          <a href="https://galefirerpg.itch.io/metal-monsters-monster-pack">
            Metal Monsters Monster Pack
          </a>
          <a href="https://galefirerpg.itch.io/cursed-kingdoms-monster-pack2">
            Cursed Kingdoms Monster Pack 2
          </a>
          <a href="https://galefirerpg.itch.io/cursed-kingdoms-boss-pack">
            Cursed Kingdoms Boss Pack
          </a>
          <a href="https://galefirerpg.itch.io/blood-suckers-monster-pack">
            Blood Suckers Monster Pack
          </a>
        </ul>
      </>
    ),
  },
  {
    title: "Chromatic Dragon Hatchlings Stock Art",
    description: "Chromatic Dragon Hatchlings Stock Art by Ymia",
    url: "https://ymia.itch.io/chromatic-dragon-hatchlings-stock-art",
  },
  {
    title: "Fantasy Creatures V1 by ErkmenArtworks",
    description: "Fantasy Creatures V1 by ErkmenArtworks",
    url: "https://erkmenartworks.itch.io/fantasy-creatures-v1",
  },
  {
    title: "Dragons Stock Art Pack",
    description: (
      <>
        Dragons Stock Art Pack by Felipe da Silva Faria. <br />
        <i>
          Some artwork copyright Felipe da Silva Faria, used with permission
        </i>
      </>
    ),
    url: "https://felipemuky.itch.io/dragon-stock-art-pack",
  },
  {
    title: "Publisher's Choice Quality Stock Art",
    description: (
      <>
        Publisher's Choice Quality Stock Art by © Rick Hershey. <br />
      </>
    ),
    url: "http://fatgoblingames.com"
  },
  {
    title: "Art by Daniel Comerci",
    description: (
      <>
        Art by Daniel Comerci used with permission. www.danielcomerci.com
      </>
    ),
    url: "www.danielcomerci.com"
  },
  {
    title: "Art by Diane Ramic",
    description: (
      <>
        Art by Diane Ramic used with permission. https://dramic.wixsite.com/home
      </>
    ),
    url: "https://dramic.wixsite.com/home"
  },
  {
    title: "Art by Hounworks",
    description: (
      <>
        Art by Hounworks used with permission. http://www.hounworks.it
      </>
    ),
    url: "http://www.hounworks.it"
  },
  {
    title: "Stock Art by Brett Neufeld",
    description: (
      <>
        Stock Art by Brett Neufeld used with permission.
      </>
    ),
  },
  {
    title: "Stock Art by Matt Morrow",
    description: (
      <>
        Stock Art by Matt Morrow used with permission.
      </>
    ),
  },
  {
    title: "Art by Adrian Arduini",
    description: (
      <>
        Art by Adrian Arduini used with permission.
      </>
    ),
  },
  {
    title: "Stock Art by Rob Necronomicon",
    description: (
      <>
        Art by <a href="https://www.instagram.com/robnecronomicon/?hl=en">Rob Necronomicon</a>
      </>
    )
  },
  {
    title: "Stock Art Collection by Jeff Preston",
    description: (
      <>
        Jeff Preston Art is licensed under: This work is licensed under the Creative Commons Attribution 3.0 Unported License.
        Justin Nichol Art is licensed under: CC BY 4.0,. CC BY 3.0
        Mariana Ruiz Villareal is licensed under: CC0
        Max Brooks is licensed under: CC SA 3.0
        Miko Arc is licensed under: CC BY 4.0 and must include: Colorful Monsters © 2020 by Mikoarc Studio is licensed under CC BY 4.0
        Morgan Strauss is licensed under: CC0
        Remi is licensed under: CC0
        Ruskerdax is licensed under: CC0

        To view a copy of these licenses, visit:
        http://creativecommons.org/licenses/by/3.0/
        https://creativecommons.org/licenses/by/4.0/
        https://creativecommons.org/licenses/by/3.0/
        https://creativecommons.org/share-your-work/public-domain/cc0/
        http://creativecommons.org/licenses/by-sa/3.0/

        or send a letter to:

        Creative Commons
        444 Castro Street
        Suite 900
        Mountain View, California, 94041, USA

      </>
    )
  }
];

const legalNotices = [
  {
    title: "SRD 5.1 Notice",
    description: (
      <span>
        This work includes material taken from the System Reference Document 5.1
        (“SRD 5.1”) by Wizards of the Coast LLC and available at{" "}
        <a href="https://dnd.wizards.com/resources/systems-reference-document">
          https://dnd.wizards.com/resources/systems-reference-document
        </a>
        . The SRD 5.1 is licensed under the Creative Commons Attribution 4.0
        International License available at{" "}
        <a href="https://creativecommons.org/licenses/by/4.0/legalcode">
          https://creativecommons.org/licenses/by/4.0/legalcode
        </a>
        .
      </span>
    ),
  },
  {
    title: "A5E SRD Notice",
    description: (
      <span>
        This work includes material taken from the A5E System Reference Document
        (A5ESRD) by EN Publishing and available at A5ESRD.com, based on Level
        Up: Advanced 5th Edition, available at{" "}
        <a href="www.levelup5e.com">www.levelup5e.com</a>. The A5ESRD is
        licensed under the Creative Commons Attribution 4.0 International
        License available at{" "}
        <a href="https://creativecommons.org/licenses/by/4.0/legalcode">
          https://creativecommons.org/licenses/by/4.0/legalcode
        </a>
        .
      </span>
    ),
  },
  {
    title: "Lazy GM's 5e Monster Builder Resource Document Notice",
    description: (
      <span>
        This work includes material taken from the{" "}
        <a href="https://slyflourish.com/lazy_5e_monster_building_resource_document.html">
          Lazy GM's 5e Monster Builder Resource Document
        </a>{" "}
        written by Teos Abadía of{" "}
        <a href="https://alphastream.org">Alphastream.org</a>, Scott Fitzgerald
        Gray of <a href="https://insaneangel.com">Insaneangel.com</a>, and
        Michael E. Shea of <a href="https://slyflourish.com">SlyFlourish.com</a>
        , available under a{" "}
        <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
          Creative Commons Attribution 4.0 International License
        </a>
        .
      </span>
    ),
  },
  {
    title: "Lazy GM's Resource Document Notice",
    description: (
      <span>
        This work includes material taken from the{" "}
        <a href="https://slyflourish.com/lazy_gm_resource_document.html">
          Lazy GM's Resource Document
        </a>{" "}
        by Michael E. Shea of{" "}
        <a href="https://slyflourish.com">SlyFlourish.com</a>, available under a{" "}
        <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
          Creative Commons Attribution 4.0 International License
        </a>
        .
      </span>
    ),
  },
  {
    title: "OGL1.0a Legal Notice",
    description: (
      <span>
        This work includes material licensed under the OGL1.0a. See{" "}
        <Link to="/ogl">OGL Page</Link> for details. <br />
        <OglCopyrightNotice />
      </span>
    ),
    url: "/ogl",
    actionText: "View OGL1.0a Legal Notice",
  },
];

function Credit(credit: React.PropsWithChildren<CreditProps>) {
  return (
    <Card
      key={credit.title}
      elevation={2}
      style={{
        margin: "10px",
        display: "flex",
        flexDirection: "column",
        minHeight: "210px",
      }}
    >
      {credit.imageUrl && (
        <CardMedia
          component="img"
          alt={credit.title}
          height={240}
          image={credit.imageUrl}
        />
      )}
      <CardContent style={{ flexGrow: 1 }}>
        <Typography variant="h6" component="div">
          {credit.title}
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          fontSize={credit.fontSize}
        >
          {credit.description}
        </Typography>
        {credit.notice && (
          <Typography
            variant="subtitle2"
            color="text.secondary"
            fontSize={credit.fontSize}
          >
            <p>
              <i>{credit.notice}</i>
            </p>
          </Typography>
        )}
      </CardContent>
      {credit.url && (
        <CardActions>
          <Button href={credit.url} target="_new" size="small">
            {credit.actionText ?? "Learn More"}
          </Button>
        </CardActions>
      )}
    </Card>
  );
}

function Header(props: React.PropsWithChildren) {
  return (
    <Typography
      variant="h5"
      component="h2"
      style={{ margin: "5px", marginLeft: "10px" }}
    >
      {props.children}
    </Typography>
  );
}

function CreditGrid(props: CreditGridProps) {
  return (
    <Grid container spacing={2}>
      {props.credits.map((credit, index) => (
        <Grid item xs={12} sm={6} md={6} lg={4} key={index}>
          <Credit {...credit} fontSize={props.fontSize} />
        </Grid>
      ))}
    </Grid>
  );
}

function CreditPage(props: React.PropsWithChildren<PageProps>) {
  return (
    <PageLayout {...props}>
      <Header>Acknowledgements</Header>
      <CreditGrid credits={inspirationCredits} />
      <Header>Art Credits</Header>
      <CreditGrid credits={artCredits} />
      <Header>Legal Notices</Header>
      <CreditGrid credits={legalNotices} fontSize="12px" />
    </PageLayout>
  );
}

export default CreditPage;
