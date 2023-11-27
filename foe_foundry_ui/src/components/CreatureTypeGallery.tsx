import * as React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import ButtonBase from '@mui/material/ButtonBase';
import Container from '@mui/material/Container';
import { Typography } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';

const ImageBackdrop = styled('div')(({ theme }) => ({
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    background: '#000',
    opacity: 0.5,
    transition: theme.transitions.create('opacity'),
}));

const ImageIconButton = styled(ButtonBase)(({ theme }) => ({
    position: 'relative',
    display: 'block',
    padding: 0,
    borderRadius: 0,
    height: '40vh',
    [theme.breakpoints.down('md')]: {
        width: '100% !important',
        height: 100,
    },
    '&:hover': {
        zIndex: 1,
    },
    '&:hover .imageBackdrop': {
        opacity: 0.15,
    },
    '&:hover .imageMarked': {
        opacity: 0,
    },
    '&:hover .imageTitle': {
        border: '4px solid currentColor',
    },
    '& .imageTitle': {
        position: 'relative',
        padding: `${theme.spacing(2)} ${theme.spacing(4)} 14px`,
    },
    '& .imageMarked': {
        height: 3,
        width: 18,
        background: theme.palette.common.white,
        position: 'absolute',
        bottom: -2,
        left: 'calc(50% - 9px)',
        transition: theme.transitions.create('opacity'),
    },
}));

const images = [
    {
        url: "/img/monster/aberration-eye-monster.png",
        title: "Aberrations",
        link: "aberration",
        width: "40%"
    },
    {
        url: "/img/monster/beast-wolves.png",
        title: "Beasts",
        link: "beast",
        width: "40%"
    },
    {
        url: "/img/monster/celestial-fractal.png",
        title: "Celestials",
        link: "celestial",
        width: "20%"
    },
    {
        url: "/img/monster/construct-iron-golem.png",
        title: "Constructs",
        link: "construct",
        width: "38%"
    },
    {
        url: "/img/monster/dragon-2.png",
        title: "Dragons",
        link: "dragon",
        width: "38%"
    },
    {
        url: "/img/monster/elemental-fire.png",
        title: "Elementals",
        link: "elemental",
        width: "24%"
    },
    {
        url: "/img/monster/fey-hag.png",
        title: "Fey",
        link: "fey",
        width: "36%",
    },
    {
        url: "/img/monster/fiend-demon.png",
        title: "Fiends",
        link: "fiend",
        width: "44%"
    },
    {
        url: "/img/monster/giant-frost-fire.png",
        title: "Giants",
        link: "giant",
        width: "20%"
    },
    {
        url: "/img/monster/humanoid-elf-rogue.png",
        title: "Humanoids",
        link: "humanoid",
        width: "44%"
    },
    {
        url: "/img/monster/monstrosity-owlbear.png",
        title: "Monstrosities",
        link: "monstrosity",
        width: "32%"
    },
    {
        url: "/img/monster/ooze-slime-monster.png",
        title: "Oozes",
        link: "ooze",
        width: "24%"
    },
    {
        url: "/img/monster/plant-death-flower.png",
        title: "Plants",
        link: "plant",
        width: "40%"
    },
    {
        url: "/img/monster/undead-lich1.png",
        title: "Undead",
        link: "undead",
        width: "60%"
    }
]

interface CreatureTypeProps {
    url: string;
    title: string;
    link: string;
    width: string;
}

function CreatureTypeImage(image: CreatureTypeProps) {

    const navigate = useNavigate();

    const onClick = () => {
        navigate(`/statblocks/${image.link}`)
    };

    return(
    <ImageIconButton
        key={image.title}
        style={{
            width: image.width,
        }}
        onClick={onClick}
    >
        <Box
            sx={{
                position: 'absolute',
                left: 0,
                right: 0,
                top: 0,
                bottom: 0,
                backgroundSize: 'cover',
                backgroundPosition: 'center 40%',
                backgroundImage: `url(${image.url})`,
            }}
        />
        <ImageBackdrop className="imageBackdrop" />
        <Box
            sx={{
                position: 'absolute',
                left: 0,
                right: 0,
                top: 0,
                bottom: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'common.white',
            }}
        >
            <Typography
                component="h3"
                variant="h6"
                color="inherit"
                className="imageTitle"
            >
                <Link to={`/statblocks/${image.link}`} style={{ textDecoration: 'none', color: 'inherit' }}>{image.title}</Link>
                <div className="imageMarked" />
            </Typography>
        </Box>
    </ImageIconButton>
    )
}

export default function CreatureTypeGallery() {
    return (
        <Container component="section" sx={{ mt: 8, mb: 4 }}>
            <Typography variant="h4" align="center" component="h2">
                Try Out the Foe Foundry!
            </Typography>
            <Box sx={{ mt: 8, display: 'flex', flexWrap: 'wrap' }}>
                {images.map((image, index) => (
                    <CreatureTypeImage key={index} {...image} />
                ))}
            </Box>
        </Container>
    );
}
