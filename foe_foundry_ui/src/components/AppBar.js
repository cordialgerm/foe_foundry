import { styled } from '@mui/material/styles';
import * as React from 'react';

import ConstructionIcon from '@mui/icons-material/Construction';
import MenuIcon from '@mui/icons-material/Menu';
import { AppBar, Container, Toolbar, Typography } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import { drawerWidth } from './Drawer';

const MuiAppBar = styled(AppBar, {
    shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
    transition: theme.transitions.create(['margin', 'width'], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    ...(open && {
        width: `calc(100% - ${drawerWidth}px + 8px)`,
        marginLeft: `${drawerWidth - 8}px`,
        transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen,
        }),
    }),
}));

export function FoeFoundryAppBar({ drawerOpen, setDrawerOpen }) {

    const handleDrawerOpen = () => {
        setDrawerOpen(true);
    }

    return (
        <MuiAppBar position="static" open={drawerOpen}>
            <Container>
                <Toolbar disableGutters>
                    {!drawerOpen &&
                        (<IconButton onClick={handleDrawerOpen}>
                            <MenuIcon />
                        </IconButton>)
                    }
                    <ConstructionIcon style={{ marginRight: "10px" }} />
                    <Typography
                        variant="h6"
                        noWrap
                        component="a"
                        sx={{
                            mr: 2,
                            display: { xs: 'none', md: 'flex' },
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            letterSpacing: '.2rem',
                            color: 'inherit',
                            textDecoration: 'none',
                        }}>
                        Foe Foundry
                    </Typography>
                </Toolbar>
            </Container>
        </MuiAppBar>
    );
}
