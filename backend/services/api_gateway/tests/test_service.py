from news_core import Locale, ServiceSettings

from services.api_gateway.app.service import GatewayService


def test_get_slates_returns_data():
    service = GatewayService(ServiceSettings(service_name="api-gateway-test"))
    slates = service.get_slates(Locale.EN_US, ["world"])
    assert slates
    assert slates[0].events
