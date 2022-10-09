from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class DFIdentifier():
    """DOC:"""
    symbol: str
    timestamp: str


def derived_column(func):
    """DOC:"""
    func.cache_ = {}

    def inner(identifier: DFIdentifier, *args, **kwargs):

        # Make sure the first argument is an instance of DFIdentifier
        if not isinstance(identifier, DFIdentifier):
            raise TypeError("The first parameter of a function decorated by derived_column must be an "
                            "instance of DFIdentifier.")

        # TODO: purge cache if incoming identifier's timestamp is different

        if identifier not in func.cache_:
            func.cache_[identifier] = func(identifier, *args, **kwargs)

        return func.cache_[identifier]

    return inner
