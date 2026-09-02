from typing import Optional, Dict
from datetime import date


class ClinicalMathService:

    @staticmethod
    def calculate_bmi(weight_kg: Optional[float], height_cm: Optional[float]) -> Optional[float]:
        if not weight_kg or not height_cm or height_cm <= 0:
            return None
        height_m = height_cm / 100.0
        return round(weight_kg / (height_m ** 2), 2)

    @staticmethod
    def calculate_age_years(birthdate: Optional[date], as_of: Optional[date] = None) -> Optional[float]:
        if not birthdate:
            return None
        as_of = as_of or date.today()
        return round((as_of - birthdate).days / 365.25, 2)

    @staticmethod
    def bmi_cross_check_malnutrition_status(bmi: Optional[float], age_years: Optional[float]) -> Optional[str]:
      
        if bmi is None or age_years is None:
            return None

        if 5 <= age_years < 20:
            if bmi < 14.0:
                return "Severe"
            elif bmi < 15.5:
                return "Moderate"
            elif bmi < 17.0:
                return "Mild"
            return "None"

        elif age_years >= 20:
            if bmi < 16.0:
                return "Severe"
            elif bmi < 17.0:
                return "Moderate"
            elif bmi < 18.5:
                return "Mild"
            return "None"

        return None  
