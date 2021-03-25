class Dict(dict):
    """
    Dict class that allows to access the keys like attributes
    """

    def __getattribute__(self, name):
        if name in self:
            return self[name]
