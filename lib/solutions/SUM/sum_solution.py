
class SumSolution:
    
    def compute(self, x: int, y: int) -> int:
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("X and Y must be of type int")

        if not (0 <= x <= 100) or not (0 <= y <= 100):
            raise ValueError("X and Y must be between 0 and 100")
        return x + y




