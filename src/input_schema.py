from dataclasses import dataclass
from typing import Optional

@dataclass
class StartupInput:

    #we define what all we neet , datatype and optional or not.
    funding_rounds: int
    funding_stage: int  
    funding_total_usd: Optional[float] = None
    days_to_funding: Optional[float] = None
    market: Optional[str] = None
    country: Optional[str] = None
    has_institutional_vc: bool = False
    angel: float = 0.0
    debt_financing: float = 0.0
    grant: float = 0.0
    convertible_note: float = 0.0
    undisclosed: float = 0.0

    #checks to ensure no wrong values enter the model 
    def __post_init__(self):
        if not isinstance(self.funding_rounds, int) or self.funding_rounds < 1:
            raise ValueError("funding_rounds must be a whole number, at least 1")
        if self.funding_stage not in (0, 1, 2, 3):
            raise ValueError("funding_stage must be 0, 1, 2 or 3")

        for name in ("funding_total_usd", "days_to_funding"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, (int, float)) or value < 0):
                raise ValueError(f"{name} must be a non-negative number, or left unknown")

        for name in ("market", "country"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{name} must be text, or left unknown")

        types = ("angel", "debt_financing", "grant", "convertible_note", "undisclosed")
        for name in types:
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{name} must be a non-negative number")

        if self.funding_total_usd is not None:
            parts = sum(getattr(self, n) for n in types)
            if parts > self.funding_total_usd:
                raise ValueError("funding by type adds up to more than total funding")
