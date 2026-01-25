
class StateVariable:
    def __init__(self, name, possible_values=None, initial_value=None):
        self.name = name
        self.initial_value = initial_value
        self.possible_values = possible_values

    def __repr__(self):
        return f"VARIABLE {self.name} [{', '.join(str(v) for v in self.possible_values)}] initial = {self.initial_value}"
