import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import LoopIcon from '@mui/icons-material/Loop';
import { Divider as MuiDivider, Drawer as MuiDrawer, List as MuiList, ListItem as MuiListItem, ListItemButton as MuiListItemButton, ListItemIcon as MuiListItemIcon, ListItemText as MuiListItemText } from '@mui/material';
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

export function PersistentDrawerLeft({ creatureType, setCreatureType,
    role, setRole,
    cr, setCr,
    open, setOpen,
    onGenerate }) {
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

    const onGenerateClicked = event => {
        onGenerate();
    }

    return (
        <MuiDrawer
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
            <MuiDivider />
            <MuiList>
                <MuiListItem key="creatureType">
                    <CreateTypeSelector value={creatureType} onChange={onCreatureTypeChanged} />
                </MuiListItem>
                <MuiListItem key="role">
                    <RoleSelector value={role} onChange={onRoleChanged} />
                </MuiListItem>
                <MuiListItem key="cr">
                    <CrSelector value={cr} onChange={onCrChanged} />
                </MuiListItem>
                <MuiListItem key="generate">
                    <MuiListItemButton onClick={onGenerateClicked} style={{ width: "200px" }}>
                        <MuiListItemIcon>
                            <LoopIcon />
                        </MuiListItemIcon>
                        <MuiListItemText primary="Generate" />
                    </MuiListItemButton>
                </MuiListItem>
            </MuiList>
        </MuiDrawer>
    )
}
