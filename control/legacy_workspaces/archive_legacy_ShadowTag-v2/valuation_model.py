# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# valuation_model.py
class AiYouValuation:
    def __init__(self):
        # Unit Economics (Year 5 Estimates)
        self.tower_rev_yr = 35000  # Revenue per tower
        self.car_rev_mo = 10  # Revenue per car/mo
        self.starlink_rev_gb = 0.04

        # Volumes
        self.towers = 100_000
        self.cars = 10_000_000
        self.starlink_traffic_gb = 50_000_000_000  # 50 PB

    def calculate(self):
        # 1. Terrestrial (Towers)
        infra_arr = self.towers * self.tower_rev_yr

        # 2. Mobile (Cars)
        mobile_arr = self.cars * self.car_rev_mo * 12

        # 3. Orbital (Starlink)
        orbital_arr = self.starlink_traffic_gb * self.starlink_rev_gb

        # 4. Digital (Apps/Mall)
        # Assumed ratio based on infra traffic
        digital_arr = (infra_arr + mobile_arr + orbital_arr) * 0.6

        total_arr = infra_arr + mobile_arr + orbital_arr + digital_arr

        # Valuation (20x Multiple for Infra, 15x for Digital)
        valuation = (infra_arr + mobile_arr + orbital_arr) * 20 + (digital_arr * 15)

        return {
            "Total ARR": total_arr,
            "Valuation": valuation,
            "Founder Yield (5% of FCF)": total_arr * 0.4 * 0.05,  # 40% margin
        }


if __name__ == "__main__":
    model = AiYouValuation()
    results = model.calculate()
    print(f"Values in USD: {results}")
