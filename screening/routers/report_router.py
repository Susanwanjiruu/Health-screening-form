

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from core.security import require_role
from core.carbone_service import CarboneService
from screening.services.report_engine import ReportEngineService
from screening.repositories.center_repo import CenterRepository

router = APIRouter(prefix="/report", tags=["Reporting (Admin only)"])


@router.get("/{fiscal_year}")
def get_fiscal_report(
    fiscal_year: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    report_matrix = ReportEngineService.generate_fiscal_report_matrix(db, fiscal_year)
    center = CenterRepository.get_profile(db)
    return {
        "center_name": center.name if center else None,
        "region": center.region if center else None,
        "fiscal_year": fiscal_year,
        "report_matrix": report_matrix,
    }


@router.get("/{fiscal_year}/export")
def export_fiscal_report(
    fiscal_year: str,
    format: str = "xlsx",
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
  
    report_matrix = ReportEngineService.generate_fiscal_report_matrix(db, fiscal_year)
    center = CenterRepository.get_profile(db)

    file_bytes = CarboneService.generate_report_document(
        report_matrix=report_matrix,
        fiscal_year=fiscal_year,
        center_name=center.name if center else "Unknown Center",
        convert_to=format,
    )

    media_types = {
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    return Response(
        content=file_bytes,
        media_type=media_types.get(format, "application/octet-stream"),
        headers={"Content-Disposition": f'attachment; filename="FY{fiscal_year}_report.{format}"'},
    )
