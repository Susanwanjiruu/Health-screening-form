from datetime import date


def get_effective_cohort(beneficiary) -> str:
   
    if beneficiary.cohort_type == "Survival Mother":
        return "Survival Mother"

    if beneficiary.cohort_type == "Survival Baby":
        if not beneficiary.birthdate:
            return "Survival Baby"
        age_years = (date.today() - beneficiary.birthdate).days / 365.25
        if age_years >= 3:
            return "Sponsorship Participant"
        return "Survival Baby"

    return beneficiary.cohort_type
