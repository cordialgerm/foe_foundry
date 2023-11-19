import React from 'react';

import { ThemeProvider } from '@mui/material/styles';

import { CssBaseline } from '@mui/material';
import theme from '../components/Theme.js';
import CreatureTypeGallery from '../components/CreatureTypeGallery.tsx';
import ProductHeroText from '../components/ProductHeroText.tsx';

// Create the AboutPage component
const AboutPage = () => {

    const productValues = {
        title: "Welcome to Foe Foundry",
        text1: {
            title: "Powerful & Interesting",
            description: "Foe Foundry monsters hit hard. Their abilities add interesting flavor, unique mechanics, and tactical effects to make combat exciting."
        },
        text2: {
            title: "Action Economy",
            description: "Foe Foundry monsters don't have to sacrifice damage to do cool things. Your monsters won't lose just because of action economy."
        },
        text3: {
            title: "Easy to Run",
            description: "Foe Foundry monsters have clearly identified roles that dictate their mechanics, tactics, and flavor."
        }
    }
    const howItWorks = {
        title: "How Foe Foundry Works",
        text1: {
            title: "Templates",
            description: "Statblock Templates that adjust based on creature type, CR, and monster role."
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
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <ProductHeroText {...productValues} />
            <CreatureTypeGallery />
            <ProductHeroText {...howItWorks} />
        </ThemeProvider>
    );
};

export default AboutPage;
