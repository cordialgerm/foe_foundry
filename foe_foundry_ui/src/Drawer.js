import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import LoopIcon from '@mui/icons-material/Loop';
import { Divider, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import { styled, useTheme } from '@mui/material/styles';
import * as React from 'react';
import { CrSelector, CreateTypeSelector, RoleSelector } from './Selectors.js';

export const drawerWidth = 240

const DrawerHeader = styled('div')(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: 'flex-end',
}));

export function PersistentDrawerLeft({ creatureType, setCreatureType, role, setRole, cr, setCr, refreshCount, setRefreshCount, open, setOpen }) {
    const theme = useTheme();

    const handleDrawerClose = () => {
        setOpen(false);
    }

    const onCreatureTypeChanged = event => {
        setCreatureType(event.target.value);
    }

    const onRoleChanged = event => {
        setRole(event.target.value)
    }

    const onCrChanged = event => {
        setCr(event.target.value)
    }

    const onRefreshClicked = event => {
        setRefreshCount(refreshCount + 1)
    }

    return (
        <Drawer
            variant="persistent"
            anchor="left"
            width={drawerWidth}
            elevation={3}
            open={open}>
            <DrawerHeader>
                <IconButton onClick={handleDrawerClose}>
                    {theme.direction === 'ltr' ? <ChevronLeftIcon /> : <ChevronRightIcon />}
                </IconButton>
            </DrawerHeader>
            <Divider />
            <List>
                <ListItem key="creatureTyp">
                    <CreateTypeSelector value={creatureType} onChange={onCreatureTypeChanged} />
                </ListItem>
                <ListItem key="role">
                    <RoleSelector value={role} onChange={onRoleChanged} />
                </ListItem>
                <ListItem key="cr">
                    <CrSelector value={cr} onChange={onCrChanged} />
                </ListItem>
                <ListItem key="refresh">
                    <ListItemButton onClick={onRefreshClicked} style={{ width: "200px" }} color="primary">
                        <ListItemIcon>
                            <LoopIcon />
                        </ListItemIcon>
                        <ListItemText primary="Refresh" />
                    </ListItemButton>
                </ListItem>
            </List>
        </Drawer>
    )
}
