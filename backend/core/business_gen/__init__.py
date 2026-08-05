"""Smart business generation — uncertainty, self-test, human forecast, assembly."""

from backend.core.business_gen.generator import BusinessGenerator, generate_business
from backend.core.business_gen.services_catalog import BUSINESS_SERVICES, service_demo
from backend.core.business_gen.core_deliverable import build_core_deliverable
from backend.core.business_gen.hook_plan import build_hook_plan

__all__ = [
    "BusinessGenerator",
    "generate_business",
    "BUSINESS_SERVICES",
    "service_demo",
    "build_core_deliverable",
    "build_hook_plan",
]
