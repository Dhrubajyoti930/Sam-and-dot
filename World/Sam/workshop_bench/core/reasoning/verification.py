from pydantic import BaseModel
from typing import List

class VerificationPlan(BaseModel):
    hypotheses: List[str]
    test_assertions: List[str]
    rollback_condition: str