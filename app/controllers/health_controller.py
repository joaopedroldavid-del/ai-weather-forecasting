from fastapi import APIRouter, Response, status

from app.dtos.health_dto import DependencyStatusDTO, HealthDTO, ReadinessDTO
from app.services.health_service import check_supabase_connection

router = APIRouter()


@router.get("/health", response_model=HealthDTO)
def health_check() -> HealthDTO:
    return HealthDTO(status="ok")


@router.get("/health/ready", response_model=ReadinessDTO)
def readiness_check(response: Response) -> ReadinessDTO:
    supabase_up = check_supabase_connection()
    if not supabase_up:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessDTO(
        status="ok" if supabase_up else "unavailable",
        dependencies=DependencyStatusDTO(supabase="up" if supabase_up else "down"),
    )
