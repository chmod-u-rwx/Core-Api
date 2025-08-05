from fastapi import APIRouter
from ..services.sample import SampleServie

router = APIRouter(prefix="/sample")

@router.get("/")
def sample_route():
    sample_model = SampleServie.get_sample_model()
    return sample_model.model_dump()