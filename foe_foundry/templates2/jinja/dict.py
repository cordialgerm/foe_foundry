class AccessTrackingDict(dict):
    """Keep track of which keys have been accessed so we know if statblocks have been used"""

    def __init__(self, **kwargs):
        new_kwargs = {k.replace("_", "-"): v for k, v in kwargs.items()}

        super().__init__(**new_kwargs)
        self.accessed_keys = set()

    def __getitem__(self, key):
        key = key.lower().replace("_", "-")
        self.accessed_keys.add(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        key = key.lower().replace("_", "-")
        super().__setitem__(key, value)

    def get_unused_keys(self):
        return set(self.keys()) - self.accessed_keys

    def get_unused(self) -> dict:
        unused = {}
        for unused_key in self.get_unused_keys():
            unused[unused_key] = super().__getitem__(unused_key)
        return unused
