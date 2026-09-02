from sqlalchemy.orm import Session
from screening.repositories.report_repo import ReportRepository


DISEASE_PREVALENCE_FIELDS = [
    "sys_auditory_ent", "sys_circulatory", "sys_digestive_git", "sys_endocrine",
    "sys_lymphatic", "sys_musculoskeletal", "sys_nervous", "sys_reproductive",
    "sys_respiratory", "sys_skin", "sys_genito_urinary", "sys_vision_eye",
    "sys_dental", "sys_sti", "sys_malaria",
]

COHORT_MAPPING = {
    "Survival Mother": "Survival Mothers",
    "Survival Baby": "Survival Babies",
    "Sponsorship Participant": "Sponsorship Participants",
}


class ReportEngineService:

    @staticmethod
    def generate_fiscal_report_matrix(db: Session, fiscal_year: str) -> dict:
        matrix = {}

        for db_cohort, report_cohort in COHORT_MAPPING.items():
            disease_prevalence = {
                field.replace("sys_", ""): ReportRepository.count_disease_prevalence(
                    db, db_cohort, fiscal_year, field
                )
                for field in DISEASE_PREVALENCE_FIELDS
            }

            matrix[report_cohort] = {
                "number_of_registered_participants": ReportRepository.count_registered_participants_by_cohort(
                    db, db_cohort
                ),
                "number_of_participants_screened": ReportRepository.count_screened_participants(
                    db, db_cohort, fiscal_year
                ),
                "number_not_yet_screened": ReportRepository.count_not_yet_screened(
                    db, db_cohort, fiscal_year
                ),
                "mild_malnutrition": ReportRepository.count_malnutrition_by_status(
                    db, db_cohort, fiscal_year, "Mild"
                ),
                "moderate_malnutrition": ReportRepository.count_malnutrition_by_status(
                    db, db_cohort, fiscal_year, "Moderate"
                ),
                "severe_malnutrition": ReportRepository.count_malnutrition_by_status(
                    db, db_cohort, fiscal_year, "Severe"
                ),
                "disease_prevalence": disease_prevalence,
                "received_treatment_at_site": ReportRepository.count_summary_flag(
                    db, db_cohort, fiscal_year, "received_treatment_on_site"
                ),
                "prescriptions_given": ReportRepository.count_prescriptions_given(
                    db, db_cohort, fiscal_year
                ),
                "referred_for_further_treatment": ReportRepository.count_referred(
                    db, db_cohort, fiscal_year
                ),
            }

        return matrix
