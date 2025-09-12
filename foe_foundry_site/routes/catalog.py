from __future__ import annotations

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from foe_foundry.creatures import AllTemplates
from foe_foundry_data.base import MonsterInfoModel
from foe_foundry_data.monster_families import MonsterFamilies

router = APIRouter(prefix="/api/v1/catalog")


class CatalogTemplateModel(BaseModel):
    """Model for a template with its monsters in the catalog"""

    key: str
    name: str
    url: str
    monsters: List[MonsterInfoModel]


class CatalogFamilyModel(BaseModel):
    """Model for a family with its monsters in the catalog"""

    key: str
    name: str
    url: str
    monsters: List[MonsterInfoModel]


@router.get("/by_template")
def get_catalog_by_template() -> List[CatalogTemplateModel]:
    """
    Returns all monster templates with their monsters for the catalog view
    """
    catalog_templates = []
    for template in AllTemplates:
        # Only include templates that have lore (are published)
        if template.lore_md is None:
            continue
        # Get all monsters for this template
        template_monsters = []
        for monster in template.monsters:
            template_monsters.append(
                MonsterInfoModel(
                    key=monster.key,
                    name=monster.name,
                    cr=monster.cr,
                    template=template.key,
                )
            )

        # Sort monsters by name
        template_monsters.sort(key=lambda m: m.name)

        catalog_templates.append(
            CatalogTemplateModel(
                key=template.key,
                name=template.name,
                url=f"/monsters/{template.key}/",
                monsters=template_monsters,
            )
        )

    # Sort templates by name
    catalog_templates.sort(key=lambda t: t.name)

    return catalog_templates


@router.get("/by_family")
def get_catalog_by_family() -> List[CatalogFamilyModel]:
    """
    Returns all monster families with their monsters for the catalog view,
    plus templates without families grouped as individual entries
    """
    catalog_families = []

    # Get actual families first
    families = MonsterFamilies.families
    for family in families:
        # Sort monsters by name
        sorted_monsters = sorted(family.monsters, key=lambda m: m.name)

        catalog_families.append(
            CatalogFamilyModel(
                key=family.key,
                name=family.name,
                url=f"/families/{family.key}/",
                monsters=sorted_monsters,
            )
        )

    # Get all templates that are already covered by families
    family_template_keys = set()
    for family in families:
        for monster in family.monsters:
            family_template_keys.add(monster.template)
    # Add templates that don't have families as individual entries
    for template in AllTemplates:
        # Only include templates that have lore (are published)
        if template.lore_md is None:
            continue

        # Skip if this template is already covered by a family
        if template.key in family_template_keys:
            continue

        # Get all monsters for this template
        template_monsters = []
        for monster in template.monsters:
            template_monsters.append(
                MonsterInfoModel(
                    key=monster.key,
                    name=monster.name,
                    cr=monster.cr,
                    template=template.key,
                )
            )

        # Sort monsters by name
        template_monsters.sort(key=lambda m: m.name)

        # Add as a pseudo-family using the template
        catalog_families.append(
            CatalogFamilyModel(
                key=template.key,
                name=template.name,
                url=f"/monsters/{template.key}/",
                monsters=template_monsters,
            )
        )

    # Sort all families/templates by name
    catalog_families.sort(key=lambda f: f.name)

    return catalog_families
