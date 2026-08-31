from pydantic import BaseModel


class HealthDTO(BaseModel):
    status: str


class DependencyStatusDTO(BaseModel):
    supabase: str


class ReadinessDTO(BaseModel):
    status: str
    dependencies: DependencyStatusDTO
