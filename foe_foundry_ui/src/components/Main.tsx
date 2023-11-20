import * as React from 'react';
import { drawerWidth } from './Drawer';
import { styled } from '@mui/material';

interface MainContentProps {
    drawerOpen: boolean;
}

export function MainContent(props: React.PropsWithChildren<MainContentProps>) {

    const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(
        ({ theme }) => ({
            flexGrow: 1,
            transition: theme.transitions.create('margin', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.leavingScreen,
            }),
            marginLeft: `-${drawerWidth}px`,
            ...(props.drawerOpen && {
                transition: theme.transitions.create('margin', {
                    easing: theme.transitions.easing.easeOut,
                    duration: theme.transitions.duration.enteringScreen,
                }),
                marginLeft: 0,
            }),
        }),
    );

    return (
        <Main>
            {props.children}
        </Main>
    )

}
