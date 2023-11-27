import * as React from "react";

import { useState, useEffect, useCallback } from "react";
import { Statblock } from "../components/Statblock.tsx";
import { RandomBackgroundImage } from "../components/Background.js";

import { PageLayout, PageProps } from "../components/PageLayout.tsx";
import { useParams } from "react-router-dom";

interface StatblockPageProps extends PageProps {
  statblockRawHtml?: string;
}

const StatblockPage: React.FC<StatblockPageProps> = (props) => {
  const { creatureType, creatureRole, cr } = useParams();

  const resolvedCreatureType = creatureType ?? props.sidebar.creatureType;
  const resolvedCreatureRole = creatureRole ?? props.sidebar.role;
  const resolvedCr = cr ?? props.sidebar.cr;

  const url = `${props.baseUrl}/statblocks/random/${resolvedCreatureType}/${resolvedCreatureRole}/${resolvedCr}?render=partial`;

  const [state, setState] = useState({
    rawHtml: "Loading...",
    displayCreatureType: resolvedCreatureType,
    counter: 0,
  });

  const fetchData = useCallback(
    async (increment: boolean) => {
      const response = await fetch(url);
      const rawHtml = await response.text();

      if (increment) {
        setState((currentState) => {
          return {
            ...currentState,
            rawHtml: rawHtml,
            displayCreatureType: resolvedCreatureType,
            counter: currentState.counter + 1,
          };
        });
      } else {
        setState((currentState) => {
          return {
            ...currentState,
            rawHtml: rawHtml,
            displayCreatureType: resolvedCreatureType,
          };
        });
      }
    },
    [url, resolvedCreatureType]
  );

  //override the default onGenerate behavior to specifically render data for this page
  const pageProps = {
    ...props,
    onGenerate: async () => {
      //on mobile devices, close the drawer after generating a new statblock so user can see it better
      if (props.isMobile) {
        const newSidebar = { ...props.sidebar, drawerOpen: false };
        props.setSidebar(newSidebar);
      }

      await fetchData(true);
      window.history.pushState(
        {},
        "",
        `/statblocks/${resolvedCreatureType}/${resolvedCreatureRole}/${resolvedCr}`
      );
    },
  };

  //fetch data on page load
  useEffect(() => {
    fetchData(false).catch(console.error);
  }, []);

  return (
    <PageLayout {...pageProps}>
      <RandomBackgroundImage
        creatureType={state.displayCreatureType}
        counter={state.counter}
      >
        <Statblock rawHtml={state.rawHtml} />
      </RandomBackgroundImage>
    </PageLayout>
  );
};

export default StatblockPage;
