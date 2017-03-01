from spresso.controller.grant.settings import Setting
from spresso.model.settings import Container, Endpoint


class ApiInformationSettings(Setting):
    resource_path = "resources/api/"
    api_template = "api.html"

    endpoints = Container(
        Endpoint("api_info", "/spresso", ["GET"]),
    )
