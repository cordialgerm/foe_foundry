
import React from 'react';
import { Button } from '@mui/material';
import { Grid, Card, CardContent, Typography} from '@mui/material';
import  { DefaultPageLayout, DefaultPageProps } from '../components/PageLayout.tsx';
import {AllConditionProps, ConditionProps, Condition} from '../components/Condition.tsx';
import {Link} from 'react-router-dom';


function ConditionCard(condition: ConditionProps) {

  return (
    <Card elevation={2} style={{margin: "10px", display: "flex", flexDirection: "column", minHeight: "210px"}}>
        <CardContent style={{flexGrow: 1}}>
          <Typography id={condition.name} variant="h6" component="div">
            <Condition {...condition} />
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {condition.description}
          </Typography>
        </CardContent>
  </Card>
  )
}

function Header(props: React.PropsWithChildren) {
  return (
    <Typography variant="h5" component="h2" style={{margin: "5px", marginLeft: "10px"}}>
      {props.children}
    </Typography>
  )
}

function ConditionGrid(){
  return (
    <Grid container spacing={2}>
        {AllConditionProps.map((condition, index) => (
          <Grid item xs={12} sm={6} md={6} lg={4} key={index}>
            <ConditionCard {...condition} />
          </Grid>
        ))}
      </Grid>
  )
}

function ConditionPage(props: React.PropsWithChildren<DefaultPageProps>) {

  return (
    <DefaultPageLayout {...props}>
      <Header>Conditions</Header>
      <Typography variant="body1" marginLeft="10px">
        <p>
          <b>Foe Foundry</b> uses a variety of custom conditions. See <Link to="/credits">Credits</Link> for more information on inspirations.
        </p>
        <p>
          These conditions are designed to be more interactive than standard 5E conditions such as <b>Stunned</b> and <b>Paralyzed</b>.
        </p>
        <p>
          Don't worry - <b>Foe Foundry</b> monsters can afford to be more lenient in conditions that they apply to players because their action economy
          is designed such that applying these conditions is a side effect of doing damage to PCs.
          In other words, <b>Foe Foundry</b> monsters don't rely on paralyzing a PC to be threatening.
        </p>
      </Typography>
      <ConditionGrid />
    </DefaultPageLayout>
  );
};

export default ConditionPage;
