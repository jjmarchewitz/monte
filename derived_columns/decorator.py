from dataclasses import dataclass
from functools import wraps


# Using eq=True and frozen=True makes the dataclass automatically hashable
@dataclass(eq=True, frozen=True)
class DFIdentifier():
    """DOC:"""
    symbol: str
    timestamp: str


def derived_column(func):
    """DOC:"""
    func.cache_ = {}

    # TODO: Hide the DFIdentifier functionality. Create an identifier instance here (inside the decorator)
    # based on the dataframe that was passed in. That way, the first argument just has to be the dataframe.

    @wraps(func)
    def inner(identifier: DFIdentifier, *args, **kwargs):

        # Make sure the first argument is an instance of DFIdentifier
        if not isinstance(identifier, DFIdentifier):
            raise TypeError("The first parameter of a function decorated by derived_column must be an "
                            "instance of DFIdentifier.")

        # TODO: purge cache if incoming identifier's timestamp is different. Possible store latest
        # timestamp as another function attribute (like cache_)

        if identifier not in func.cache_:
            func.cache_[identifier] = func(identifier, *args, **kwargs)

        return func.cache_[identifier]

    return inner
