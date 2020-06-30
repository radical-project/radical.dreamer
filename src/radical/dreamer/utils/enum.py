
class EnumTypes:

    def __init__(self, *args):
        """
        Initialization.

        :param args: Pairs of ('Name', 'value').
        :type args: tuple
        """
        self.values = [x[1] for x in args]
        self.choices = list(zip(self.values, [x[0] for x in args]))

        self._attrs = dict(args)
        self._items = dict(zip(range(len(args)), self.values))

    def __getattr__(self, a):
        """
        Get value of the corresponding Enum name.

        :param a: Enum name.
        :type a: str
        :return: Enum value.
        :rtype: any
        """
        return self._attrs[a]

    def __getitem__(self, i):
        """
        Get value of the corresponding element by the index.

        :param i: Enum index.
        :type i: str
        :return: Enum value.
        :rtype: any
        """
        return self._items[i]

    def __len__(self):
        """
        Get number of elements.

        :return: Number of elements.
        :rtype: int
        """
        return len(self._attrs)

    def __iter__(self):
        return iter(self.choices)
