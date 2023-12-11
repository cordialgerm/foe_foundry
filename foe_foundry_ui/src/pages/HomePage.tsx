import React from "react";
import CreatureTypeGallery from "../components/CreatureTypeGallery.tsx";
import ProductHeroText from "../components/ProductHeroText.tsx";
import { PageLayout, PageProps } from "../components/PageLayout.tsx";
import { Link } from "react-router-dom";

function AboutPage(props: React.PropsWithChildren<PageProps>) {
  const productValues = {
    title: (
      <>
        Welcome to the <b>Foe Foundry</b>
      </>
    ),
    subtitle: (
      <>
        A 5E monster builder that makes it easy to create powerful and
        interesting monsters. <Link to="/statblocks">Get Started!</Link>
      </>
    ),
    text1: {
      title: "Powerful & Interesting",
      description: (
        <span>
          These monsters hit hard.{" "}
          <Link to="/powers">
            <b>Powers</b>
          </Link>{" "}
          add interesting flavor, unique mechanics, and tactical effects to make
          combat exciting.
        </span>
      ),
    },
    text2: {
      title: "Action Economy",
      description:
        "Monsters shouldn't have to sacrifice damage to do cool things. Your monsters won't lose just because of action economy.",
    },
    text3: {
      title: "Easy to Run",
      description:
        "Foe Foundry monsters have clearly identified roles that inform mechanics, tactics, and flavor.",
    },
  };
  const howItWorks = {
    title: "How Foe Foundry Works",
    subtitle: (
      <>
        <i>
          No Generative AI is used to create statblocks - all powers & rules are
          hand-crafted.
        </i>
      </>
    ),
    text1: {
      title: "Templates",
      description:
        "Statblocks adjust based on creature type, CR, and monster role.",
    },
    text2: {
      title: "Powers",
      description: (
        <>
          Over 200 unique{" "}
          <Link to="/powers">
            <b>Powers</b>
          </Link>{" "}
          that add interesting flavor, unique mechanics, and tactical effects to
          make combat exciting.
        </>
      ),
    },
    text3: {
      title: "Smart Selection",
      description: (
        <>
          Monsters are created intelligently by combining powers that make sense
          together using a series of rules and random tables.
        </>
      ),
    },
  };

  return (
    <PageLayout {...props}>
      <ProductHeroText {...productValues} />
      <CreatureTypeGallery {...props} />
      <ProductHeroText {...howItWorks} />
    </PageLayout>
  );
}

export default AboutPage;
