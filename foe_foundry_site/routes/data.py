from pydantic import BaseModel


class MonsterMeta(BaseModel):
    monster_key: str
    template_key: str
