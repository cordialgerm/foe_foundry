import React from 'react';

import InfoIcon from '@mui/icons-material/Info';
import { Tooltip } from "@mui/material";

interface ConditionProps {
    name: string;
    description: string;
}

export const Condition: React.FC<ConditionProps> = ({ name, description }) => {
    return (
        <Tooltip title={description}>
            <span>
                <strong>{name}</strong>
                <InfoIcon />
            </span>
        </Tooltip>
    );
};

export const Burning = () => <Condition name="Burning" description="You are on fire!" />;
export const Bleeding = () => <Condition name="Bleeding" description="You are bleeding!" />;
export const Frozen = () => <Condition name="Frozen" description="You are frozen!" />;
export const Dazed = () => <Condition name="Dazed" description='You are dazed!' />;
export const Shocked = () => <Condition name="Shocked" description='You are shocked!' />;
export const Swallowed = () => <Condition name="Swallowed" description='You are swallowed!' />;
export const Fatigue = () => <Condition name="Fatigue" description='You are fatigued!' />;
export const Weakened = () => <Condition name="Weakened" description='You are weakened!' />;

export const CustomConditions = [
    Burning,
    Bleeding,
    Frozen,
    Dazed,
    Shocked,
    Swallowed,
    Fatigue,
    Weakened
]
