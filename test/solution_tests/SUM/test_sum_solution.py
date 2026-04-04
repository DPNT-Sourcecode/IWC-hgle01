from solutions.SUM.sum_solution import SumSolution
import pytest


class TestSum():
    def test_sum(self):
        assert SumSolution().compute(1, 2) == 3

    @pytest.mark.parametrize("x, y", [(-1, 2), (101, 2), (1, -1), (1, 101)])
    def test_sum_out_of_range(self, x, y):
        with pytest.raises(ValueError):
            SumSolution().compute(x, y)


    @pytest.mark.parametrize("x, y", [(0, 0), (100, 0), (0, 100), (100, 100), (50, 50)])
    def test_sum_in_range(self, x, y):
        assert SumSolution().compute(x, y) == x + y


