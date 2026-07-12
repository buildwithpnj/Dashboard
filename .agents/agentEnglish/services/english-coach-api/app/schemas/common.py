from pydantic import BaseModel, Field

class HealthCheck(BaseModel):
    status: str = Field(..., description="System status flag.")
    version: str = Field(..., description="System version.")
    app_name: str = Field(..., description="Application name.")
    app_env: str = Field(..., description="Application execution environment.")
