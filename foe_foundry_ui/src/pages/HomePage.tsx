import React from 'react';
import CreatureTypeGallery from '../components/CreatureTypeGallery.tsx';
import ProductHeroText from '../components/ProductHeroText.tsx';
import { DefaultPageLayout, DefaultPageProps } from '../components/PageLayout.tsx';

function AboutPage(props: React.PropsWithChildren<DefaultPageProps>) {

    const productValues = {
        title: <span>Welcome to the <b>Foe Foundry</b></span>,
        text1: {
            title: "Powerful & Interesting",
            description: "These monsters hit hard. Powers add interesting flavor, unique mechanics, and tactical effects to make combat exciting."
        },
        text2: {
            title: "Action Economy",
            description: "Monsters shouldn't have to sacrifice damage to do cool things. Your monsters won't lose just because of action economy."
        },
        text3: {
            title: "Easy to Run",
            description: "Foe Foundry monsters have clearly identified roles that inform mechanics, tactics, and flavor."
        }
    }
    const howItWorks = {
        title: "How Foe Foundry Works",
        text1: {
            title: "Templates",
            description: "Statblocks adjust based on creature type, CR, and monster role."
        },
        text2: {
            title: "Powers",
            description: "Over 200 unique powers that add interesting flavor, unique mechanics, and tactical effects to make combat exciting."
        },
        text3: {
            title: "Smart Selection",
            description: "Monsters are created intelligently by combining powers that make sense together."
        }
    }

    return (
        <DefaultPageLayout {...props}>
            <ProductHeroText {...productValues} />
            <CreatureTypeGallery />
            <ProductHeroText {...howItWorks} />
        </DefaultPageLayout>
    )
};

export default AboutPage;
