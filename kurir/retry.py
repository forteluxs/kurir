from dataclasses import dataclass


@dataclass
class RetryConfig:
    max_attempts: int = 3
    timeout: int = 10
