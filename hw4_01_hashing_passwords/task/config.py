from dataclasses import dataclass

@dataclass
class SecurityConfig:
    delay_base: float = 1.5
    delay_constant: float = 1.0
    max_failed_attempts: int = 10
    bcrypt_rounds: int = 12
    log_failed_attempts: bool = True
    log_successful_logins: bool = False
    reset_counter_after: int = 3600

config = SecurityConfig()