import * as React from "react";

import { drawerWidth } from "./Drawer.js";

interface StatblockProps {
  rawHtml: string
}

export function Statblock({ rawHtml }: StatblockProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100vh",
        textAlign: "left",
        padding: "20px",
        marginLeft: drawerWidth,
      }}
    >
      <div dangerouslySetInnerHTML={{ __html: rawHtml }} />
    </div>
  );
}
