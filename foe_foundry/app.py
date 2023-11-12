from __future__ import annotations

import os
import sys

sys.path.append("/home/cordialgerm87/foe_foundry")
from dataclasses import fields
from typing import List, Optional, Set

import numpy as np
import uvicorn
from fastapi import FastAPI, Response
from pydantic.dataclasses import dataclass

from foe_foundry import (
    Attack,
    AttackType,
    Attributes,
    Condition,
    CreatureType,
    DamageType,
    DieFormula,
    Feature,
    MonsterRole,
    Movement,
    ResolvedArmorClass,
    Senses,
    Size,
    Statblock,
    get_common_stats,
    get_creature_template,
    get_role,
)
from foe_foundry.templates import render_html_inline

app = FastAPI()

rng = np.random.default_rng(20210518)


def rng_factory() -> np.random.Generator:
    return rng


@dataclass(kw_only=True)
class StatblockModel:
    name: str
    cr: float
    hp: DieFormula
    speed: Movement
    ac: ResolvedArmorClass
    uses_shield: bool
    attributes: Attributes
    attack: Attack
    additional_attacks: List[Attack]
    features: List[Feature]
    multiattack: int
    size: Size
    creature_type: CreatureType
    creature_subtype: Optional[str]
    creature_class: Optional[str]
    languages: List[str]
    senses: Senses
    role: MonsterRole = MonsterRole.Default
    attack_type: AttackType = AttackType.MeleeWeapon
    damage_resistances: Set[DamageType]
    damage_immunities: Set[DamageType]
    condition_immunities: Set[Condition]
    nonmagical_resistance: bool
    nonmagical_immunity: bool

    @staticmethod
    def from_args(args: dict) -> StatblockModel:
        available = {f.name for f in fields(StatblockModel)}
        kwargs = {k: v for k, v in args.items() if k in available}
        missing = {a for a in available if a not in kwargs}
        for m in missing:
            kwargs[m] = None
        return StatblockModel(**kwargs)


def _random_stats(creature: str, role: str, cr: str | int | float) -> Statblock:
    creature_template = get_creature_template(creature)
    role_template = get_role(role)
    base_stats = get_common_stats(cr)
    stats = creature_template.create(
        base_stats=base_stats,
        role_template=role_template,
        rng_factory=rng_factory,
    )
    return stats


@app.get("/")
def get_root():
    return {"Hello": "World"}


@app.get("/statblocks/random/{creature}/{role}/{cr}")
def view_random_stats(creature: str, role: str, cr: str | int | float) -> Response:
    stats = _random_stats(creature, role, cr)
    html = render_html_inline(stats)
    return Response(content=html, media_type="text/html")


@app.get("/api/v1/statblocks/random/{creature}/{role}/{cr}")
def get_random_stats(creature: str, role: str, cr: str | int | float) -> StatblockModel:
    stats = _random_stats(creature, role, cr)
    return StatblockModel.from_args(stats.__copy_args__())


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.getenv("PORT", 8080)), proxy_headers=True)
