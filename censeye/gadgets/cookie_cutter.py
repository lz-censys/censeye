from typing import Optional

from censeye.gadget import QueryGeneratorGadget


class CookieCutterGadget(QueryGeneratorGadget):
    """When the service_name is HTTP and has a Set-Cookie header, this gadget generates queries that focus on the cookie values.

    Example:

    HTTP/1.1 200 OK
    Set-Cookie: SESSIONID=1234567890; path=/; HttpOnly

    Queries:
    - services.http.response.headers: (key: "Set-Cookie" and value: "SESSIONID=*")

    "I'm a cookie monster!" - Aristotle
    """

    def __init__(self):
        super().__init__("cookie-cutter", aliases=["cookie", "cookiecutter"])

    def generate_query(self, host: dict) -> Optional[set[tuple[str, str]]]:
        queries: set[tuple[str, str]] = set()
        services: list[dict] = host.get("services", [])
        for service in services:
            if service.get("service_name") == "HTTP":
                headers: dict[str, list[str]] = (
                    service.get("http", {}).get("response", {}).get("headers", [])
                )
                for header_key, headers_value in headers.items():
                    if not headers_value:
                        continue
                    if header_key.lower() in ("set-cookie", "set_cookie"):
                        header_value = headers_value.pop().strip()
                        cookie_parts = header_value.split("=", 1)
                        if len(cookie_parts) == 0:
                            continue
                        cookie_name = cookie_parts[0].strip()
                        queries.add(
                            (
                                self.name,
                                f"services.http.response.headers: (key: 'Set-Cookie' and value.headers: '{cookie_name}=*')",
                            )
                        )
        return queries


__gadget__ = CookieCutterGadget()
