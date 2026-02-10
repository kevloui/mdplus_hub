class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class AuthorizationError(DomainError):
    pass


class StorageError(DomainError):
    pass


class GlimpsError(DomainError):
    pass


class ModelNotTrainedError(GlimpsError):
    pass


class TrainingError(GlimpsError):
    pass


class InferenceError(GlimpsError):
    pass
