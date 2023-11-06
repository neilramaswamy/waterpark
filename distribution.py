import abc
from typing import List

import numpy as np


class Distribution(abc.ABC):
    def __init__(self, parameters):
        self.parameters = parameters

    @abc.abstractmethod
    def sample(self) -> float:
        pass


class GammaDistribution(Distribution):
    def sample(self) -> float:
        shape = self.parameters[0]
        scale = self.parameters[1]
        return np.random.gamma(shape, scale)


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
    if name == "gamma":
        if len(parameters) != 2:
            raise ValueError("Gamma distribution requires 2 parameter: <shape> <scale>")
        return GammaDistribution(parameters)
    elif name == "exponential":
        if len(parameters) != 1:
            raise ValueError("Exponential distribution requires 1 parameter: <rate>")
        return ExponentialDistribution(parameters)
    elif name == "uniform":
        if len(parameters) != 2:
            raise ValueError("Uniform distribution requires 2 parameters: <low> <high>")
        return UniformDistribution(parameters)
    elif name == "constant":
        if len(parameters) != 1:
            raise ValueError("Constant distribution requires 1 parameter: <value>")
        return ConstantDistribution(parameters)
    else:
        raise ValueError(f"Unsupported distribution type: {name}")
