from dataclasses import dataclass


@dataclass
class Token:
    name: str
    dc: int
    charges: int

    @property
    def caption(self) -> str:
        return f"<span class='token'>{self.name} Token (AC/DC {self.dc}, {self.charges} Charges)</span>"
