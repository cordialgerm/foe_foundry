import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import LoopIcon from "@mui/icons-material/Loop";
import {
  Divider,
  Drawer,
  SwipeableDrawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import IconButton from "@mui/material/IconButton";
import { styled, useTheme } from "@mui/material/styles";
import * as React from "react";
import { CrSelector, CreateTypeSelector, RoleSelector } from "./Selectors.tsx";
import { useNavigate } from "react-router-dom";

export const drawerWidth = 240;

const DrawerHeader = styled("div")(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: "flex-end",
}));

export interface DrawerProps {
  creatureType: string;
  setCreatureType: (creatureType: string) => void;
  role: string;
  setRole: (role: string) => void;
  cr: string;
  setCr: (cr: string) => void;
  open: boolean;
  setOpen: (open: boolean) => void;
  onGenerate: () => void;
  isMobile?: boolean;
}

export function FoeFoundryAppDrawer({ ...props }: DrawerProps) {
  const theme = useTheme();
  const navigate = useNavigate();

  const handleDrawerClose = () => {
    props.setOpen(false);
  };

  const onCreatureTypeChanged = (creatureType: string) => {
    props.setCreatureType(creatureType);
  };

  const onRoleChanged = (role: string) => {
    props.setRole(role);
  };

  const onCrChanged = (cr: string) => {
    props.setCr(cr);
  };

  const onGenerateClicked = (event) => {
    props.onGenerate();
  };

  type LinkProps = {
    to: string;
  };
  function Link(link: React.PropsWithChildren<LinkProps>) {
    const onClick = (event) => {
      if (props.isMobile) {
        props.setOpen(false);
      }
      navigate(link.to);
    };

    return <ListItemButton onClick={onClick}>{link.children}</ListItemButton>;
  }

  const DrawerContent = () => {
    return (
      <>
        <DrawerHeader>
          <IconButton onClick={handleDrawerClose}>
            {theme.direction === "ltr" ? (
              <ChevronLeftIcon />
            ) : (
              <ChevronRightIcon />
            )}
          </IconButton>
        </DrawerHeader>
        <Divider />
        {props.isMobile && (
          <>
            <List>
              <ListItem>
                <Link to="/statblocks">Statblocks</Link>
              </ListItem>
              <ListItem>
                <Link to="/powers">Powers</Link>
              </ListItem>
              <ListItem>
                <Link to="/conditions">Conditions</Link>
              </ListItem>
              <ListItem>
                <Link to="/credits">Credits</Link>
              </ListItem>
            </List>
            <Divider />
          </>
        )}
        <List>
          <ListItem key="creatureType">
            <CreateTypeSelector
              value={props.creatureType}
              onCreatureTypeChanged={onCreatureTypeChanged}
            />
          </ListItem>
          <ListItem key="role">
            <RoleSelector value={props.role} onRoleChanged={onRoleChanged} />
          </ListItem>
          <ListItem key="cr">
            <CrSelector value={props.cr} onCrChanged={onCrChanged} />
          </ListItem>
          <ListItem key="generate">
            <ListItemButton
              onClick={onGenerateClicked}
              style={{ width: "200px" }}
            >
              <ListItemIcon>
                <LoopIcon />
              </ListItemIcon>
              <ListItemText primary="Generate" />
            </ListItemButton>
          </ListItem>
        </List>
      </>
    );
  };

  if (props.isMobile) {
    return (
      <SwipeableDrawer
        anchor="left"
        open={props.open}
        onClose={() => props.setOpen(false)}
        onOpen={() => props.setOpen(true)}
      >
        <DrawerContent />
      </SwipeableDrawer>
    );
  } else {
    return (
      <Drawer
        variant="persistent"
        anchor="left"
        width={drawerWidth}
        elevation={3}
        open={props.open}
      >
        <DrawerContent />
      </Drawer>
    );
  }
}
