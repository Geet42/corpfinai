from models.valuation import SensitivityCell
from typing import List


class SensitivityAnalyzer:
    def generate_matrix(
        self,
        base_fcf: float,
        shares: float,
        wacc_range: list,
        growth_range: list,
        projection_years: int = 5,
    ) -> List[SensitivityCell]:
        """Generate WACC vs Terminal Growth sensitivity matrix."""
        cells = []
        for wacc in wacc_range:
            for growth in growth_range:
                if wacc <= growth:
                    cells.append(
                        SensitivityCell(
                            wacc=round(wacc, 4),
                            terminal_growth=round(growth, 4),
                            implied_price=0,
                        )
                    )
                    continue

                # PV of terminal value only (simplified for sensitivity)
                terminal_value = (base_fcf * (1 + growth)) / (wacc - growth)
                pv_terminal = terminal_value / ((1 + wacc) ** projection_years)
                implied_price = pv_terminal / shares if shares else 0

                cells.append(
                    SensitivityCell(
                        wacc=round(wacc, 4),
                        terminal_growth=round(growth, 4),
                        implied_price=round(implied_price, 2),
                    )
                )
        return cells
