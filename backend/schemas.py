from pydantic import BaseModel


class OverviewResponse(BaseModel):
    total_flows: int
    normal_flows: int
    attack_flows: int
    attack_percentage: float
    unique_protocols: int