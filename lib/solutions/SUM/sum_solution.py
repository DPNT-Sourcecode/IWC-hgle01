
class SumSolution:
    
    def compute(self, x, y):
        if not (0 <= x <= 100) and not (0 <= y <= 100):
            raise ValueError("X and Y must be between 0 and 100")
        return x + y


