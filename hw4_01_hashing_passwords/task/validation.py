from dataclasses import dataclass, field
import re

ERR_LENGTH = "length"
ERR_LETTER = "requires_letter"
ERR_DIGIT = "requires_digit"
ERR_SPECIAL = "requires_special"

@dataclass
class PasswordValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid

def validate_password(password: str) -> PasswordValidationResult:
    result = PasswordValidationResult(is_valid=True)
    
    if len(password) < 12:
        result.is_valid = False
        result.errors.append(ERR_LENGTH)
    
    if not re.search(r'[a-zA-Z]', password):
        result.is_valid = False
        result.errors.append(ERR_LETTER)
    
    if not re.search(r'\d', password):
        result.is_valid = False
        result.errors.append(ERR_DIGIT)
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result.is_valid = False
        result.errors.append(ERR_SPECIAL)
    
    return result