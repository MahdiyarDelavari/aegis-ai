from pydantic import BaseModel
from datetime import datetime


class OverviewResponse(BaseModel):
    total_flows: int
    normal_flows: int
    attack_flows: int
    attack_percentage: float
    unique_protocols: int


class NetworkFlow(BaseModel):
    source_id: int
    label: int
    attack_cat: str | None
    proto: str | None
    dur: float
    sbytes: int
    dbytes: int


class FlowPage(BaseModel):
    page: int
    size: int
    total: int
    items: list[NetworkFlow]



class PipelineRun(BaseModel):
    run_id: int
    status: str
    processed_flows: int
    rejected_rows: int
    started_at: datetime
    finished_at: datetime | None