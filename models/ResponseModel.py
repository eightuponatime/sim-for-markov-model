from dataclasses import dataclass

@dataclass
class ResponseModel:
  buffer_size: int
  client_id: str
  status: bool
  phase1_time_ms: float = 0
  phase2_time_ms: float = 0
  phase3_time_ms: float = 0
  total_time_ms: float = 0
