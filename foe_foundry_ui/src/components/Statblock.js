import * as React from 'react';

import { useEffect, useState } from 'react';

import { drawerWidth } from './Drawer.js';


export function RandomStatblock({ baseUrl, creatureType, role, cr, counter }) {
    const url = `http://${baseUrl}/statblocks/random/${creatureType}/${role}/${cr}?render=partial`
    const id = `${creatureType}-${role}-${cr}-${counter}`

    const [state, setState] = useState({ loaded: false, rawHtml: "loading..." })

    useEffect(() => {
        let ignore = false;

        async function startFetching() {
            const response = await fetch(url)
            const rawHtml = await response.text()
            if (!ignore) {
                setState({ loaded: true, rawHtml: rawHtml })
            }
        }

        startFetching();

        return () => {
            ignore = true;
        };
    }, [creatureType, role, cr, counter, url]);

    return (
        <div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100vh", textAlign: "left", padding: "20px", marginLeft: drawerWidth }}>
            <div key={id} id={id} dangerouslySetInnerHTML={{ __html: state.rawHtml }} style={{ color: "black" }} />
        </div>
    )
}
