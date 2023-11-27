import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import LoopIcon from "@mui/icons-material/Loop";
import {
  Divider as MuiDivider,
  Drawer as MuiDrawer,
  List as MuiList,
  ListItem as MuiListItem,
  ListItemButton as MuiListItemButton,
  ListItemIcon as MuiListItemIcon,
  ListItemText as MuiListItemText,
} from "@mui/material";
import IconButton from "@mui/material/IconButton";
import { styled, useTheme } from "@mui/material/styles";
import * as React from "react";
import { CrSelector, CreateTypeSelector, RoleSelector } from "./Selectors.js";
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

export function PersistentDrawerLeft({ ...props }: DrawerProps) {
  const theme = useTheme();
  const navigate = useNavigate();

  const handleDrawerClose = () => {
    props.setOpen(false);
  };

  const onCreatureTypeChanged = (event) => {
    props.setCreatureType(event.target.value);
  };

  const onRoleChanged = (event) => {
    props.setRole(event.target.value);
  };

  const onCrChanged = (event) => {
    props.setCr(event.target.value);
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

    return (
      <MuiListItemButton onClick={onClick}>{link.children}</MuiListItemButton>
    );
  }

  return (
    <MuiDrawer
      variant="persistent"
      anchor="left"
      width={drawerWidth}
      elevation={3}
      open={props.open}
    >
      <DrawerHeader>
        <IconButton onClick={handleDrawerClose}>
          {theme.direction === "ltr" ? (
            <ChevronLeftIcon />
          ) : (
            <ChevronRightIcon />
          )}
        </IconButton>
      </DrawerHeader>
      <MuiDivider />
      {props.isMobile && (
        <>
          <MuiList>
            <MuiListItem>
              <Link to="/statblocks">Statblocks</Link>
            </MuiListItem>
            <MuiListItem>
              <Link to="/conditions">Conditions</Link>
            </MuiListItem>
            <MuiListItem>
              <Link to="/credits">Credits</Link>
            </MuiListItem>
          </MuiList>
          <MuiDivider />
        </>
      )}
      <MuiList>
        <MuiListItem key="creatureType">
          <CreateTypeSelector
            value={props.creatureType}
            onChange={onCreatureTypeChanged}
          />
        </MuiListItem>
        <MuiListItem key="role">
          <RoleSelector value={props.role} onChange={onRoleChanged} />
        </MuiListItem>
        <MuiListItem key="cr">
          <CrSelector value={props.cr} onChange={onCrChanged} />
        </MuiListItem>
        <MuiListItem key="generate">
          <MuiListItemButton
            onClick={onGenerateClicked}
            style={{ width: "200px" }}
          >
            <MuiListItemIcon>
              <LoopIcon />
            </MuiListItemIcon>
            <MuiListItemText primary="Generate" />
          </MuiListItemButton>
        </MuiListItem>
      </MuiList>
    </MuiDrawer>
  );
}
