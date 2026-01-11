class DomainConstraint:
    """Unary constraint X in {values}"""
    def __init__(self, var, values):
        self.var = var
        self.values = set(values)

    def propagate(self, domains):
        if self.var not in domains:
            domains[self.var] = set(self.values)
            return True
        old = domains[self.var]
        new = old & self.values
        if not new:
            return False
        if new != old:
            domains[self.var] = new
            return True
        return True  # consistent, no change needed


class NotEqualConstraint:
    """Binary constraint X != Y"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def propagate(self, domains):
        if self.x not in domains or self.y not in domains:
            return True  # not all variables bound yet, no propagation possible
        dx = domains[self.x].copy()
        dy = domains[self.y].copy()

        # If one variable is bound to a single value, remove that value from the other
        if len(dx) == 1:
            dy -= dx
        if len(dy) == 1:
            dx -= dy

        # Check consistency: both domains must be non-empty
        if not dx or not dy:
            return False

        domains[self.x] = dx
        domains[self.y] = dy

        # Return True if consistent (changes or not)
        return True