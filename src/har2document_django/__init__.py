import re
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

from django.urls import Resolver404, ResolverMatch, resolve
from har2document import HTTPMethod, MarkdownComponent


class DjangoViewDoesNotExist(Exception):
    pass


def resolve_url(url: str) -> ResolverMatch:
    try:
        return resolve(urlparse(url).path)
    except Resolver404:
        raise


def _is_view_class(match: ResolverMatch) -> bool:
    return hasattr(match.func, "cls")


def _get_view_class_path_from_path(match: ResolverMatch) -> str:
    return match._func_path


def _get_view_class_name_from_match(match: ResolverMatch) -> str:
    return match.func.cls.__name__


def _get_view_function_path_from_match(match: ResolverMatch) -> str:
    return f"{match._func_path}()"


def _get_view_function_name_from_match(match: ResolverMatch) -> str:
    return f"{match.func.__name__}()"


def get_django_view_name_from_path(url: str, include_module: bool = False) -> str:
    path: str = urlparse(url).path

    try:
        match: ResolverMatch = resolve(path)
    except Resolver404:
        raise DjangoViewDoesNotExist

    func_mapper: dict[tuple[bool, bool], Callable[[ResolverMatch], str]] = {
        (True, True): _get_view_class_path_from_path,
        (True, False): _get_view_class_name_from_match,
        (False, True): _get_view_function_path_from_match,
        (False, False): _get_view_function_name_from_match,
    }
    return func_mapper[_is_view_class(match), include_module](match)


def _get_path_parameter_from_match(match: ResolverMatch) -> dict[str, str]:
    return match.kwargs


def get_path_parameter_from_url(url: str) -> dict[str, Any]:
    path: str = urlparse(url).path

    try:
        match: ResolverMatch = resolve(path)
    except Resolver404:
        raise DjangoViewDoesNotExist

    return _get_path_parameter_from_match(match)


def replace_request_path_with_variable(url: str) -> str:
    path: str = urlparse(url).path
    query_string: str = urlparse(url).query

    try:
        match: ResolverMatch = resolve(path)
    except Resolver404:
        raise DjangoViewDoesNotExist

    return f"/{match.route}?{query_string}"


def replace_route(route: str) -> str:
    """
    Example:
        - "/api/loans/<str:aidb64>/<str:token>/" -> "/api/loans/{aidb64}/{token}/"
        - "/api/users/<int:pk>" -> "/api/users/{pk}"
    """
    return re.sub(r"<\w+:(\w+)>", r"{\1}", route)


class DjangoEndpoint(MarkdownComponent):
    def render(self) -> str:
        """
        Example:
            ### UserView GET `/api/users/?page={page}&size={size}`

        Example:
            ### views.list_users() POST `/api/users/?type=personal`
        """
        request_path_replaced: str = replace_route(
            replace_request_path_with_variable(self.document["request_url"])
        )
        if self.document["request_method"] == HTTPMethod.GET:
            for key, value in self.document["request_query_string"].items():
                request_path_replaced = request_path_replaced.replace(
                    f"{key}={value}", f"{key}={{{key}}}"
                )

        return (
            f"### {get_django_view_name_from_path(self.document['request_url'])}"
            f" {self.document['request_method']} `{request_path_replaced}`"
        )


class PathParameter(MarkdownComponent):
    def render(self) -> str:
        """
        Example:
            Path Parameter

            - `user_id`: `1`
        """
        return "Path Parameter\n\n" + "\n".join(
            f"- `{key}`: `{value}`"
            for key, value in get_path_parameter_from_url(
                self.document["request_url"]
            ).items()
        )

    @property
    def condition(self) -> bool:
        return bool(get_path_parameter_from_url(self.document["request_url"]))
