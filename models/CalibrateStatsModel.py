from dataclasses import dataclass

@dataclass
class CallibrateStatsModel:
  avg_total_time_ms: float
  avg_phase1_time_ms: float
  avg_phase2_time_ms: float
  avg_phase3_time_ms: float
  successful_requests: int
  blocked_requests: int
  blocking_probability: float
