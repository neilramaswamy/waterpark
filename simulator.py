from dataclasses import dataclass
from typing import List, Tuple

from distribution import Distribution


@dataclass
class SimulationResult:
    num_records: int = -1
    num_dropped_by_watermark: int = -1

    def percentage_dropped(self) -> float:
        return self.num_dropped_by_watermark / self.num_records

    def __str__(self):
        return f"(percentage_aggregated: {1 - self.percentage_dropped()})"


def run_simulation(
    distribution: Distribution,
    watermark_delay: int,
    watermark_speed: int,
    input_rate: int,
    duration: int,
):
    # For duration seconds, generate input_rate records per second
    num_records = duration * input_rate

    records: List[Tuple[float, float]] = [(0.0, 0.0) for i in range(num_records)]

    # First, generate all the records
    for i in range(num_records):
        event_time = i / input_rate
        delay = distribution.sample()
        arrival_time = event_time + delay

        records[i] = (event_time, arrival_time)

    # Sort based on when we _receive_ the records, i.e. arrival time
    sorted_records = sorted(records, key=lambda x: x[1])

    # Streaming engine metrics
    global_watermark = 0.0
    max_event_time_seen = 0.0
    num_dropped_by_watermark = 0

    for i, record in enumerate(sorted_records):
        event_time, arrival_time = record

        # Drop late records
        if event_time < global_watermark:
            num_dropped_by_watermark += 1
            continue

        # Compute the maximum so-far
        max_event_time_seen = max(max_event_time_seen, event_time)

        # Only set the new watermark at the "batch boundary", i.e. every watermark_speed
        if i % watermark_speed == 0:
            global_watermark = max(max_event_time_seen - watermark_delay, 0)

    return SimulationResult(num_records, num_dropped_by_watermark)
