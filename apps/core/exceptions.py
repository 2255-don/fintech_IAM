class BusinessRuleError(Exception):
    """Base exception for domain/business rule violations."""


class AgentNotFoundError(BusinessRuleError):
    pass


class ClientNotFoundError(BusinessRuleError):
    pass


class InvalidMiseError(BusinessRuleError):
    pass


class CycleClosedError(BusinessRuleError):
    pass


class InvalidNbMisesError(BusinessRuleError):
    pass


class CollecteLimitExceededError(BusinessRuleError):
    pass


class InsufficientRetirableAmountError(BusinessRuleError):
    pass


class ActiveCycleAlreadyExistsError(BusinessRuleError):
    pass


class EmergencyWithdrawalNotAllowedError(BusinessRuleError):
    pass


class EmergencyWithdrawalAmountExceededError(BusinessRuleError):
    pass
