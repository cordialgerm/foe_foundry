import * as React from "react";
import { Box } from "@mui/material";

interface StatblockProps {
  rawHtml: string;
}

export function Statblock({ rawHtml }: StatblockProps) {
  return (
    <Box
      sx={{
        padding: { xs: 0, md: "5px", lg: "20px" },
      }}
      style={{
        display: "flex",
        flexDirection: "column",
        textAlign: "left",
      }}
    >
      <div dangerouslySetInnerHTML={{ __html: rawHtml }} />
    </Box>
  );
}
