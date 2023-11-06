import argparse
import abc
import random
import numpy as np

from dataclasses import dataclass

import unittest

from typing import List, Tuple

from time import sleep


class Distribution(abc.ABC):
    def __init__(self, parameters):
        self.parameters = parameters

    @abc.abstractmethod
    def sample(self) -> float:
        pass


class GaussianDistribution(Distribution):
    def sample(self) -> float:
        mean, std_dev = self.parameters
        return np.random.normal(mean, std_dev)


class ExponentialDistribution(Distribution):
    def sample(self) -> float:
        rate = self.parameters[0]
        return np.random.exponential(1 / rate)


class UniformDistribution(Distribution):
    def sample(self) -> float:
        low, high = self.parameters
        return np.random.uniform(low, high)


class ConstantDistribution(Distribution):
    def sample(self) -> float:
        return self.parameters[0]


def get_distribution(name: str, parameters: List[float]) -> Distribution:
    if name == "gaussian":
        if len(parameters) != 2:
            raise ValueError(
                "Gaussian distribution requires 2 parameters: mean and standard deviation"
            )
        return GaussianDistribution(parameters)
    elif name == "exponential":
        if len(parameters) != 1:
            raise ValueError("Exponential distribution requires 1 parameter: rate")
        return ExponentialDistribution(parameters)
    elif name == "uniform":
        if len(parameters) != 2:
            raise ValueError("Uniform distribution requires 2 parameters: low and high")
        return UniformDistribution(parameters)
    elif name == "constant":
        if len(parameters) != 1:
            raise ValueError("Constant distribution requires 1 parameter: value")
        return ConstantDistribution(parameters)
    else:
        raise ValueError(f"Unsupported distribution type: {name}")


@dataclass
class SimulationResult:
    num_records: int = -1
    num_dropped_by_watermark: int = -1

    def percentage_dropped(self) -> float:
        return self.num_dropped_by_watermark / self.num_records

    def __str__(self):
        return f"(percentage_dropped_by_wm: {self.percentage_dropped()})"


def generate_data(
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
        # print(f"Got record {records[i]}")

    sorted_records = sorted(records, key=lambda x: x[1])

    # Streaming engine metrics
    global_watermark = 0.0
    max_event_time_seen = 0.0
    num_dropped_by_watermark = 0

    for i, record in enumerate(sorted_records):
        event_time, arrival_time = record
        # print(f"Got record ({event_time}, {arrival_time}), watermark: {global_watermark}")

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


def main():
    parser = argparse.ArgumentParser(description="Data Generation Script")
    parser.add_argument(
        "--distribution",
        choices=["gaussian", "exponential", "uniform", "constant"],
        help="Type of distribution (gaussian, exponential, uniform, or constant)",
    )
    parser.add_argument(
        "--parameters",
        type=float,
        nargs="+",
        help="Parameters for the selected distribution",
    )
    parser.add_argument(
        "--watermark_delay",
        type=float,
        required=True,
        help="Watermark delay in seconds (a positive scalar integer)",
    )
    parser.add_argument(
        "--watermark_speed",
        type=int,
        required=True,
        help="The watermark will update every watermark_speed number of records",
    )
    parser.add_argument(
        "--input_rate",
        type=int,
        required=True,
        help="Input rate in records per second (a positive scalar integer)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        required=False,
        default=10,
        help="The number of seconds to run the waterpark simulation for",
    )

    args = parser.parse_args()

    print("Distribution:", args.distribution)
    print("Parameters:", args.parameters)
    print("Watermark Delay:", args.watermark_delay)
    print("Input Rate:", args.input_rate)

    distribution = get_distribution(args.distribution, args.parameters)
    result = generate_data(
        distribution,
        args.watermark_delay,
        args.watermark_speed,
        args.input_rate,
        args.duration,
    )
    print(result)


if __name__ == "__main__":
    main()
