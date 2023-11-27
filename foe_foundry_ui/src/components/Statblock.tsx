import * as React from "react";

interface StatblockProps {
  rawHtml: string;
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
      }}
    >
      <div dangerouslySetInnerHTML={{ __html: rawHtml }} />
    </div>
  );
}
