"""Functions and group homomorphisms."""


class Function():
    def __init__(self, dct: dict):
        """Init function."""
        self.f_dct = dct

    def __call__(self, x):
        """Evaluate self(x)."""
        return self.f_dct[x] if x in self.f_dct else None
    
    def compose(self, other):
        """Return: f = self ∘ other."""
        domain = other.f_dct.keys()
        return Function(
            dict((arg, self(other(arg))) for arg in domain)
        )
