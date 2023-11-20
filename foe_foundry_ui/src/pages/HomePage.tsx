import React from 'react';
import CreatureTypeGallery from '../components/CreatureTypeGallery.tsx';
import ProductHeroText from '../components/ProductHeroText.tsx';
import { PageLayout, DefaultSidebarData } from '../components/PageLayout.tsx';
import { useNavigate } from 'react-router-dom';

interface AboutPageProps {
    baseUrl: string;
}

function AboutPage(props: React.PropsWithChildren<AboutPageProps>) {

    const productValues = {
        title: "Welcome to Foe Foundry",
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

    const navigate = useNavigate();
    const [sidebar, setSidebar] = React.useState(DefaultSidebarData);
    const pageProps = {
        baseUrl: props.baseUrl,
        sidebar: sidebar,
        setSidebar: setSidebar,
        onGenerate: () => {
            navigate("/statblocks/" + sidebar.creatureType + "/" + sidebar.role + "/" + sidebar.cr);
        }
    }

    return (
        <PageLayout {...pageProps}>
            <ProductHeroText {...productValues} />
            <CreatureTypeGallery />
            <ProductHeroText {...howItWorks} />
        </PageLayout>
    )
};

export default AboutPage;
