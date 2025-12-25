from dataclasses import dataclass, field


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
    errors = []
    
    if len(password) < 12:
        errors.append(ERR_LENGTH)
    
    if not any(c.isalpha() for c in password):
        errors.append(ERR_LETTER)
    
    if not any(c.isdigit() for c in password):
        errors.append(ERR_DIGIT)
    
    if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
        errors.append(ERR_SPECIAL)
    
    return PasswordValidationResult(
         is_valid=not errors, 
        errors=errors
    )
