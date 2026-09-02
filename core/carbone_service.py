

import httpx
from fastapi import HTTPException
from core.config import settings


class CarboneService:

    @staticmethod
    def _headers() -> dict:
        if not settings.CARBONE_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="Carbone is not configured (CARBONE_API_KEY missing). "
                       "Report export is unavailable until this is set."
            )
        return {
            "Authorization": f"Bearer {settings.CARBONE_API_KEY}",
            "carbone-version": "4",
            "Content-Type": "application/json",
        }

    @staticmethod
    def generate_report_document(report_matrix: dict, fiscal_year: str, center_name: str,
                                  convert_to: str = "xlsx") -> bytes:
      
        if not settings.CARBONE_REPORT_TEMPLATE_ID:
            raise HTTPException(
                status_code=503,
                detail="CARBONE_REPORT_TEMPLATE_ID is not set. Upload the FY25 template "
                       "to Carbone Studio first, then configure the template ID."
            )

        render_payload = {
            "data": {
                "center_name": center_name,
                "fiscal_year": fiscal_year,
                **report_matrix,  
            },
            "convertTo": convert_to,
        }

        render_url = f"{settings.CARBONE_API_BASE_URL}/render/{settings.CARBONE_REPORT_TEMPLATE_ID}"

        with httpx.Client(timeout=30.0) as client:
            render_response = client.post(render_url, headers=CarboneService._headers(), json=render_payload)

            if render_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Carbone render request failed: {render_response.text}"
                )

            render_id = render_response.json().get("data", {}).get("renderId")
            if not render_id:
                raise HTTPException(status_code=502, detail="Carbone did not return a renderId.")

            download_url = f"{settings.CARBONE_API_BASE_URL}/render/{render_id}"
            download_response = client.get(download_url, headers=CarboneService._headers())

            if download_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Carbone document download failed: {download_response.text}"
                )

            return download_response.content
