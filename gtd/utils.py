import importlib


def import_class(  # type: ignore[no-untyped-def]
    module_name: str, class_name: str, class_type: str
):
    # Try importing the module.
    module = importlib.import_module(module_name)

    # Try getting the class.
    _class = getattr(module, class_name)

    # Check if the class is a subclass of the base class.
    if class_type and not any(
        base_class.__name__ == class_type for base_class in _class.mro()
    ):
        raise ValueError(
            f"Class '{class_name}' should have `{class_type}` as a base class."
        )

    return _class
