import * as React from 'react';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import ButtonBase from '@mui/material/ButtonBase';
import Container from '@mui/material/Container';
import { Typography } from '@mui/material';

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
        url: "/img/aberration-eye-monster.png",
        title: "Aberrations",
        width: "40%"
    },
    {
        url: "/img/beast-wolves.png",
        title: "Beasts",
        width: "40%"
    },
    {
        url: "/img/celestial-fractal.png",
        title: "Celestials",
        width: "20%"
    },
    {
        url: "/img/construct-iron-golem.png",
        title: "Constructs",
        width: "38%"
    },
    {
        url: "/img/dragon-2.png",
        title: "Dragons",
        width: "38%"
    },
    {
        url: "/img/elemental-fire.png",
        title: "Elementals",
        width: "24%"
    },
    {
        url: "/img/fey-hag.png",
        title: "Fey",
        width: "36%",
    },
    {
        url: "/img/fiend-demon.png",
        title: "Fiends",
        width: "44%"
    },
    {
        url: "/img/giant-frost-fire.png",
        title: "Giants",
        width: "20%"
    },
    {
        url: "/img/humanoid-elf-rogue.png",
        title: "Humanoids",
        width: "44%"
    },
    {
        url: "/img/monstrosity-owlbear.png",
        title: "Monstrosities",
        width: "32%"
    },
    {
        url: "/img/ooze-slime-monster.png",
        title: "Oozes",
        width: "24%"
    },
    {
        url: "/img/plant-death-flower.png",
        title: "Plants",
        width: "40%"
    },
    {
        url: "/img/undead-lich1.png",
        title: "Undead",
        width: "60%"
    }
]

export default function CreatureTypeGallery() {
    return (
        <Container component="section" sx={{ mt: 8, mb: 4 }}>
            <Typography variant="h4" align="center" component="h2">
                Try It Out!
            </Typography>
            <Box sx={{ mt: 8, display: 'flex', flexWrap: 'wrap' }}>
                {images.map((image) => (
                    <ImageIconButton
                        key={image.title}
                        style={{
                            width: image.width,
                        }}
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
                                {image.title}
                                <div className="imageMarked" />
                            </Typography>
                        </Box>
                    </ImageIconButton>
                ))}
            </Box>
        </Container>
    );
}