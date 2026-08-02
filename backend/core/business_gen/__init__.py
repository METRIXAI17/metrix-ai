"""Smart business generation — uncertainty, self-test, human forecast, assembly."""

from backend.core.business_gen.generator import BusinessGenerator, generate_business
from backend.core.business_gen.services_catalog import BUSINESS_SERVICES, service_demo

__all__ = [
    "BusinessGenerator",
    "generate_business",
    "BUSINESS_SERVICES",
    "service_demo",
]
