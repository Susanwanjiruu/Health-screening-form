from typing import Dict, Any, Tuple


class ReferralEngineService:
  

    HIGH_PRIORITY_SYSTEMS = [
        "sys_circulatory", "sys_respiratory", "sys_nervous", "sys_endocrine",
    ]

    @staticmethod
    def evaluate(
        malnutrition_status: str,
        temperature_celsius,
        physical_exam_flags: Dict[str, bool],
        lab_test_flags: Dict[str, bool],
    ) -> Tuple[bool, str, str, bool]:
       
        reasons = []
        is_safeguarding = False
        urgency = "Routine"

        if malnutrition_status in ["Severe", "Moderate"]:
            reasons.append(f"Malnutrition status: {malnutrition_status}")

        if temperature_celsius is not None and (temperature_celsius >= 39.5 or temperature_celsius <= 35.0):
            reasons.append(f"Abnormal temperature: {temperature_celsius}°C")
            urgency = "Urgent"

        if physical_exam_flags.get("appearance_signs_of_abuse_neglect"):
            reasons.append("Signs of abuse/neglect noted on physical exam")
            is_safeguarding = True
            urgency = "Urgent"

        if physical_exam_flags.get("appearance_lethargic"):
            reasons.append("Lethargy noted on exam")

        if physical_exam_flags.get("appearance_edema_swelling"):
            reasons.append("Edema/swelling noted on exam")

        for system_field in ReferralEngineService.HIGH_PRIORITY_SYSTEMS:
            if physical_exam_flags.get(system_field):
                reasons.append(f"Abnormal finding: {system_field.replace('sys_', '').replace('_', ' ')}")
                urgency = "Urgent"

        if lab_test_flags.get("test_hiv_positive"):
            reasons.append("Positive HIV test result")
            urgency = "Urgent"

        requires_referral = len(reasons) > 0
        reason_text = "; ".join(reasons) if reasons else ""

        return requires_referral, reason_text, urgency, is_safeguarding
