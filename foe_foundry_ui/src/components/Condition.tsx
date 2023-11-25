import React from 'react';
import InfoIcon from '@mui/icons-material/Info';
import WhatshotIcon from '@mui/icons-material/Whatshot';
import ElectricBoltIcon from '@mui/icons-material/ElectricBolt';
import AcUnitIcon from '@mui/icons-material/AcUnit';
import BloodtypeOutlinedIcon from '@mui/icons-material/BloodtypeOutlined';
import PsychologyAltOutlinedIcon from '@mui/icons-material/PsychologyAltOutlined';
import BedtimeOffOutlinedIcon from '@mui/icons-material/BedtimeOffOutlined';
import HeartBrokenOutlinedIcon from '@mui/icons-material/HeartBrokenOutlined';
import DinnerDiningIcon from '@mui/icons-material/DinnerDining';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import { Tooltip } from "@mui/material";

export interface ConditionProps {
    name: string;
    description: JSX.Element;
    icon?: JSX.Element;
}

export const Condition: React.FC<ConditionProps> = (props) => {

    const icon = props.icon ?? <InfoIcon fontSize='small'/>;

    return (
        <Tooltip title={props.description}>
            <span>
                <strong>{props.name}</strong>
                {icon}
            </span>
        </Tooltip>
    );
};


const BurningProps: ConditionProps = {
    name:"Burning",
    description:<span>A <strong>Burning</strong> creature suffers ongoing damage at the start of each of its turns. A creature may use an action to end the condition.</span>,
    icon: <WhatshotIcon fontSize='small'/>
}
export const Burning = () => <Condition {...BurningProps} />;

const BleedingProps: ConditionProps = {
    name: "Bleeding",
    description: <span>A <b>Bleeding</b> creature suffers ongoing damage at the end of each of its turns.
        A creature may use an action to attempt a Medicine check to end the condition.
        The condition also ends if the creature receives healing.</span>,
    icon: <BloodtypeOutlinedIcon fontSize='small'/>
}
export const Bleeding = () => <Condition {...BleedingProps} />;

const FrozenProps: ConditionProps = {
    name: "Frozen",
    description: <span>A <b>Frozen</b> creature is partially encased in ice. It has a movement speed of zero, attacks made against it are at advantage, and it is vulnerable to bludgeoning and thunder damage.
        <br />
        <br />
        A creature may use an action to perform a Strength (Athletics) check to break the ice and end the condition.
        The condition also ends whenever the creature takes any bludgeoning, thunder, or fire damage.</span>,
    icon: <AcUnitIcon fontSize='small'/>
}
export const Frozen = () => <Condition {...FrozenProps} />;

const DazedProps: ConditionProps = {
    name: "Dazed",
    description: <span>A <b>Dazed</b> creature can move or take an action on its turn, but not both. It cannot take bonus actions or free object interactions.</span>,
    icon: <PsychologyAltOutlinedIcon fontSize='small'/>
}
export const Dazed = () => <Condition {...DazedProps} />;

const ShockedProps: ConditionProps = {
    name: "Shocked",
    description: <span>A <b>Shocked</b> creature is <Dazed /> and drops whatever it is carrying.</span>,
    icon: <ElectricBoltIcon fontSize='small'/>
}
export const Shocked = () => <Condition {...ShockedProps}/>;


const FatigueProps: ConditionProps = {
    name: "Fatigue",
    description: <span>A creature suffering from <b>Fatigue</b> subtracts its fatigue level from the d20 roll whenever making a d20 test.
        It also subtracts its fatigue level from the Spell save DC of any spell it casts.
        <br />
        <br />
        Fatigue levels are cumulative, and any creature that gains more than 10 levels of fatigue dies.
        Finishing a Long Rest removes 1 level of fatigue.</span>,
    icon: <BedtimeOffOutlinedIcon fontSize='small'/>
}
export const Fatigue = () => <Condition {...FatigueProps}/>;


const WeakenedProps: ConditionProps = {
    name: "Weakened",
    description: <span>A <b>Weakened</b> creature deals half damage with its spells and attacks and has disadvantage on Strength ability checks and saving throws.</span>,
    icon: <HeartBrokenOutlinedIcon fontSize='small'/>
}
export const Weakened = () => <Condition {...WeakenedProps}/>;


const SwallowedProps: ConditionProps = {
    name: "Swallowed",
    description: <span>A <b>Swallowed</b> creature is <b>Blinded</b>, <b>Restrained</b>, and has total cover against attacks and effects from the outside. It takes ongoing damage at the start of each of its turns.
        <br />
        <br />
        If the swallowing creature takes sufficient damage on a single turn from a creature inside it, it must make a Constitution saving throw at the end of that turn or regurgitate all swallowed creatures which fall <b>Prone</b> in a space within 10 feet of it.
        If the swallowing creature dies, the swallowed creature is no longer restrained by it and can escape by using 15 feet of movement, exiting prone.</span>,
    icon: <DinnerDiningIcon fontSize='small'/>
}
export const Swallowed = () => <Condition {...SwallowedProps}/>;

const SusceptibleProps: ConditionProps = {
    name: "Susceptible",
    description: <span>A creature <b>Susceptible</b> to a certain damage type ignores any immunity or resistance to that damage type that it may have had. If it had no such immunity, it is instead vulnerable to that damage type.</span>,
    icon: <ReportProblemIcon />
}
export const Susceptible = () => <Condition {...SusceptibleProps}/>;


export const AllConditionProps = [
    BurningProps,
    BleedingProps,
    FrozenProps,
    DazedProps,
    ShockedProps,
    FatigueProps,
    WeakenedProps,
    SwallowedProps,
    SusceptibleProps,
];
