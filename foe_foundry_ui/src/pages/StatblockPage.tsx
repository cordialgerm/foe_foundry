import * as React from "react";

import { useState, useEffect, useCallback } from "react";
import { Statblock } from "../components/Statblock.tsx";
import { RandomBackgroundImage } from "../components/Background.js";

import { PageLayout, PageProps } from "../components/PageLayout.tsx";

const StatblockPage: React.FC<PageProps> = (props) => {
  const [state, setState] = useState({
    rawHtml: "Loading...",
    counter: 0,
    displayCreature: props.sidebar.creatureType,
  });
  const selection = props.sidebar;

  const fetchData = useCallback(
    async (increment: boolean) => {
      const url = `${props.baseUrl}/statblocks/random/${selection.creatureType}/${selection.role}/${selection.cr}?render=partial`;
      const response = await fetch(url);
      const rawHtml = await response.text();

      if (increment) {
        setState((currentState) => {
          return {
            ...currentState,
            rawHtml: rawHtml,
            displayCreature: selection.creatureType,
            counter: currentState.counter + 1,
          };
        });
      } else {
        setState((currentState) => {
          return {
            ...currentState,
            rawHtml: rawHtml,
            displayCreature: selection.creatureType,
          };
        });
      }
    },
    [selection, props.baseUrl]
  );

  //override the default onGenerate behavior to specifically render data for this page
  const pageProps = {
    ...props,
    onGenerate: async () => {
      //on mobile devices, close the drawer after generating a new statblock so user can see it better
      if (props.isMobile) {
        props.setSidebar({ ...props.sidebar, drawerOpen: false });
      }
      await fetchData(true);
    },
  };

  //fetch data on page load
  useEffect(() => {
    fetchData(false).catch(console.error);
  }, []);

  return (
    <PageLayout {...pageProps}>
      <RandomBackgroundImage
        creatureType={state.displayCreature}
        counter={state.counter}
      >
        <Statblock rawHtml={state.rawHtml} />
      </RandomBackgroundImage>
    </PageLayout>
  );
};

export default StatblockPage;
