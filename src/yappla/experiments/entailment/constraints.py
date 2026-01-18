class DomainConstraint:
    """Unary constraint X in {values}"""
    def __init__(self, var, values):
        self.var = var
        self.variable = var  # Alias for backward compatibility
        self.values = set(values)

    def __str__(self):
        # Format the values nicely
        values_list = sorted(list(self.values), key=lambda x: (isinstance(x, str), x))
        return f"{self.var} in {{{', '.join(str(v) for v in values_list)}}}"
    
    def __repr__(self):
        return self.__str__()

    def propagate(self, domains):
        var_name = str(self.var)  # Convert Variable to string if needed
        if var_name not in domains:
            domains[var_name] = set(self.values)
            return True
        old = domains[var_name]
        new = old & self.values if isinstance(old, set) else set(old) & self.values
        if not new:
            return False
        if new != old:
            domains[var_name] = new
            return True
        return True  # consistent, no change needed


class NotEqualConstraint:
    """Binary constraint X != Y"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x} != {self.y}"
    
    def __repr__(self):
        return self.__str__()

    def propagate(self, domains):
        x_name = str(self.x)  # Convert Variable to string if needed
        y_name = str(self.y)  # Convert Variable to string if needed
        
        if x_name not in domains or y_name not in domains:
            return True  # not all variables bound yet, no propagation possible
        
        dx = domains[x_name]
        dy = domains[y_name]
        
        # Convert to sets if they're lists
        if not isinstance(dx, set):
            dx = set(dx)
        if not isinstance(dy, set):
            dy = set(dy)
        
        dx = dx.copy()
        dy = dy.copy()

        # If one variable is bound to a single value, remove that value from the other
        if len(dx) == 1:
            dy -= dx
        if len(dy) == 1:
            dx -= dy

        # Check consistency: both domains must be non-empty
        if not dx or not dy:
            return False

        domains[x_name] = dx
        domains[y_name] = dy

        # Return True if consistent (changes or not)
        return True