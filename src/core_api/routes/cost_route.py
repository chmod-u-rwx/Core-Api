from fastapi import APIRouter

router = APIRouter(prefix="/cost", tags=["Resource Cost"])

CPU_CORE_COST_PER_SECOND = 0.03
RAM_GB_COST_PER_SECOND = 0.05

@router.get("/", summary="Get current cost per ")
def get_resource_cost():
    return {
        "cpu_core_cost_per_second": CPU_CORE_COST_PER_SECOND,
        "ram_gb_cost_per_second": RAM_GB_COST_PER_SECOND,
    }