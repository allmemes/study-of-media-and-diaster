from typing import List


class TemplateClass(object):
    """A class template

    Parameters
    ==========
    example_arg: int
    Some example arg
    """
    def __init__(self, int: int):
        self._int = int

    def get_data(self, num: int) -> List[int]:
        """Get a list of int

        Parameters
        ==========
        num: int
            The count of the int

        Returns
        =======
        List[int]
            A list of int

        Examples
        ========
        >>> template = TemplateClass(5)
        >>> template.get_data(3)
        """

        return [self._int] * num
