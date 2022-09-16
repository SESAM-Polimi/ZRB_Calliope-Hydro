import warnings


class ModelError(Exception):
    """
    ModelErrors should stop execution of the model, e.g. due to a problem
    with the model formulation or input data.

    """

    pass


class ModelWarning(Warning):
    """
    ModelWarnings should be raised for possible model errors, but
    where execution can still continue.

    """

    pass


class BackendWarning(Warning):
    pass


def warn(message, _class=ModelWarning):
    warnings.warn(message, _class)
