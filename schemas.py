from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FactCheckRequest(BaseModel):
    """
    Request body for /factcheck endpoint
    """
    text: str = Field(
        ...,
        description="The claim or statement to be fact-checked"
    )


class ModelSignal(BaseModel):
    """
    Output from the ML classifier
    """
    label: Optional[str] = Field(None, example="LABEL_0")
    confidence: float = Field(..., ge=0.0, le=1.0)


class EvidenceItem(BaseModel):
    """
    Single evidence record used in decision-making
    """
    url: str
    title: Optional[str] = ""
    domain: Optional[str] = ""
    snippet: Optional[str] = ""
    sim: Optional[float] = None
    nli_entail: Optional[float] = None
    authority: Optional[float] = None
    e_score: Optional[float] = None


class FactCheckResponse(BaseModel):
    """
    Final response returned by the fact-checking engine
    """
    claim: str
    verdict: str = Field(
        ...,
        description="TRUE / FALSE / INSUFFICIENT"
    )
    model_signal: ModelSignal
    reasons: List[str]
    top_sources: List[str]
    supporting: List[EvidenceItem]
    meta: Dict[str, Any]
