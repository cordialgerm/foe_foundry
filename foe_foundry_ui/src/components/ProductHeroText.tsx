import * as React from "react";
import { Theme } from "@mui/material/styles";
import { SxProps } from "@mui/system";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Container from "@mui/material/Container";
import { Typography } from "@mui/material";

interface HeroTextProps {
  title: string | JSX.Element;
  description: string | JSX.Element;
}

interface ProductHeroTextProps {
  title: string | JSX.Element;
  subtitle?: string | JSX.Element;
  text1: HeroTextProps;
  text2: HeroTextProps;
  text3: HeroTextProps;
}

const item: SxProps<Theme> = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  px: 5,
};

const title = {
  fontSize: 24,
  fontFamily: "default",
  fontWeight: "bold",
  textDecoration: "underline",
  textAlign: "center",
};

const description = {
  fontSize: 18,
  fontFamily: "default",
  textAlign: "center",
};

const HeroText: React.FC<HeroTextProps> = (data) => {
  return (
    <Grid item xs={12} md={4}>
      <Box sx={item}>
        <Box sx={title}>{data.title}</Box>
        <Typography variant="h5" align="center" sx={description}>
          {data.description}
        </Typography>
      </Box>
    </Grid>
  );
};

const ProductHeroText: React.FC<ProductHeroTextProps> = (heroText) => {
  return (
    <Box
      component="section"
      sx={{ display: "flex", bgcolor: "primary.light", overflow: "hidden" }}
    >
      <Container
        sx={{
          mt: 10,
          mb: 15,
          position: "relative",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Box
          component="img"
          src="/img/logo/foe_foundry_logo_200.png"
          alt="curvy lines"
          sx={{
            pointerEvents: "none",
            // position: 'absolute',
            // top: -180,
            opacity: 1.0,
          }}
        />
        <Typography
          variant="h4"
          component="h2"
          sx={{ mb: 4, textAlign: "center" }}
        >
          {heroText.title}
        </Typography>
        {heroText.subtitle && (
          <Typography
            variant="h5"
            component="h3"
            sx={{ mb: 4, textAlign: "center", fontStyle: "italic" }}
          >
            {heroText.subtitle}
          </Typography>
        )}
        <div>
          <Grid container spacing={5}>
            <HeroText {...heroText.text1} />
            <HeroText {...heroText.text2} />
            <HeroText {...heroText.text3} />
          </Grid>
        </div>
      </Container>
    </Box>
  );
};

export default ProductHeroText;
