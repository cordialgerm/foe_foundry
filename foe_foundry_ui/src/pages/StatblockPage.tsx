import * as React from 'react';

import { useState, useEffect } from 'react';
import { Statblock } from '../components/Statblock.tsx'
import { RandomBackgroundImage } from '../components/Background.js';

import { PageLayout, SidebarData, DefaultSidebarData } from '../components/PageLayout.tsx';
import { useParams } from 'react-router-dom';

interface StatblockPageProps {
  baseUrl: string;
}

const StatblockPage: React.FC<StatblockPageProps> = (props) => {

  let {creatureType, creatureRole, cr} = useParams();

  let defaultSidebarData = { ...DefaultSidebarData};
  if (creatureType) {
    defaultSidebarData.creatureType = creatureType;
  }
  if (creatureRole) {
    defaultSidebarData.role = creatureRole;
  }
  if (cr) {
    defaultSidebarData.cr = cr;
  }

  const defaultState = {
    sidebar: defaultSidebarData,
    displayCreatureType: defaultSidebarData.creatureType,
    refreshCounter: 0,
    statblockRawHtml: ""
  }

  const [state, setState] = useState(defaultState);

  const updateStatblock = async (incrementCounter: boolean) => {
    const creatureType = state.sidebar.creatureType;
    const role = state.sidebar.role;
    const cr = state.sidebar.cr;
    const url = `${props.baseUrl}/statblocks/random/${creatureType}/${role}/${cr}?render=partial`;
    const response = await fetch(url);
    const rawHtml = await response.text();

    if (incrementCounter) {
      setState((currentState) => {
        return {...currentState, statblockRawHtml: rawHtml, displayCreatureType: creatureType, refreshCounter: currentState.refreshCounter + 1}
      });
    }
    else {
      setState((currentState) => {
        return {...currentState, statblockRawHtml: rawHtml, displayCreatureType: creatureType}
      });
    }
  };

  const pageProps = {
    baseUrl: props.baseUrl,
    sidebar: state.sidebar,
    setSidebar: (sidebar: SidebarData) => {
      setState( (currentState) => {
        return {...currentState, sidebar: sidebar}
      })
    },
    onGenerate: async () => {
      await updateStatblock(true);
    }
  };



  useEffect(() => {
    updateStatblock(false);  // don't increment counter on initial load
  }, []); // Empty array means this effect runs once after the first render


  return (
    <PageLayout {...pageProps}>
      <RandomBackgroundImage creatureType={state.displayCreatureType} counter={state.refreshCounter}>
        <Statblock rawHtml={state.statblockRawHtml}/>
      </RandomBackgroundImage>
    </PageLayout>
  )
}



export default StatblockPage;
