"""Smart business generation — uncertainty, self-test, human forecast, assembly."""

from backend.core.business_gen.generator import BusinessGenerator, generate_business
from backend.core.business_gen.services_catalog import BUSINESS_SERVICES, service_demo
from backend.core.business_gen.core_deliverable import build_core_deliverable
from backend.core.business_gen.hook_plan import build_hook_plan
from backend.core.business_gen.rd_reader import convert_to_rd
from backend.core.business_gen.author_personality import build_author_personality
from backend.core.business_gen.assist_agent import ImplementationAssistAgent

__all__ = [
    "BusinessGenerator",
    "generate_business",
    "BUSINESS_SERVICES",
    "service_demo",
    "build_core_deliverable",
    "build_hook_plan",
    "convert_to_rd",
    "build_author_personality",
    "ImplementationAssistAgent",
]
