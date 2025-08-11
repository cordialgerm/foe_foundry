import re
from dataclasses import dataclass


@dataclass
class TrainingParagraph:
    topic: str
    name: str
    text: str

    @property
    def word_count(self) -> int:
        return len(re.findall(r"\w+", self.text))

    def to_dict(self) -> dict[str, str]:
        return {
            "topic": self.topic,
            "name": self.name,
            "text": self.text,
        }
