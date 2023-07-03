from dataclasses import dataclass
from typing import Optional, List

from pydantic import BaseModel


@dataclass
class Concept:
    description: str
    regex: Optional[str] = None


class CardData(BaseModel):
    """Card information element"""

    card_id: int
    name: str
    energy: int
    power: int
    pool: str
    ability_type: List[str]
    # gender: str
    # species: str
    # featured_in: List["str"]


class CardDataColors(BaseModel):
    """Colors for card elements compared"""

    energy_color: str
    power_color: str
    pool_color: str
    ability_type_color: str
    # gender_color: str
    # species_color: str
    # featured_in_color: str


class GuessAnswer(BaseModel):
    """Answer to the user's submitted guess"""

    card_data: CardData
    card_data_colors: CardDataColors

