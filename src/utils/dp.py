import math
import secrets
from typing import Iterable

def laplace_noise(scale: float) -> float:
    # Inverse CDF sampling for Laplace(0, b=scale)
    # U in (-0.5, 0.5)
    u = secrets.randbits(64) / 2**64 - 0.5
    return -scale * math.copysign(1.0, u) * math.log(1 - 2 * abs(u))

def dp_count(items: Iterable, epsilon: float) -> float:
    sensitivity = 1.0  # for count queries
    scale = sensitivity / max(epsilon, 1e-6)
    true_count = float(len(list(items)))
    return true_count + laplace_noise(scale)

def dp_sum(values: Iterable[float], epsilon: float, sensitivity: float = 1.0) -> float:
    scale = sensitivity / max(epsilon, 1e-6)
    true_sum = float(sum(values))
    return true_sum + laplace_noise(scale)
