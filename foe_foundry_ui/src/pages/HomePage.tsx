import React from "react";
import CreatureTypeGallery from "../components/CreatureTypeGallery.tsx";
import ProductHeroText from "../components/ProductHeroText.tsx";
import { PageLayout, PageProps } from "../components/PageLayout.tsx";
import { Link } from "react-router-dom";

function AboutPage(props: React.PropsWithChildren<PageProps>) {
  const productValues = {
    title: (
      <span>
        Welcome to the <b>Foe Foundry</b>
      </span>
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
    text1: {
      title: "Templates",
      description:
        "Statblocks adjust based on creature type, CR, and monster role.",
    },
    text2: {
      title: "Powers",
      description: (
        <span>
          Over 200 unique{" "}
          <Link to="/powers">
            <b>Powers</b>
          </Link>{" "}
          that add interesting flavor, unique mechanics, and tactical effects to
          make combat exciting.
        </span>
      ),
    },
    text3: {
      title: "Smart Selection",
      description:
        "Monsters are created intelligently by combining powers that make sense together.",
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
