from fastapi import APIRouter
from app.models.requirements import RequirementParseRequest, RequirementParseResponse

router = APIRouter()

@router.post("/parse-requirements", response_model=RequirementParseResponse)
def parse_requirements(request: RequirementParseRequest):
    # Placeholder: echo back a dummy parameters dict
    return RequirementParseResponse(
        parameters={"parsed": True, "requirement": request.requirement},
        original=request.requirement
    ) 