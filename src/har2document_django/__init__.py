import re
from pathlib import Path
from typing import Any, cast, get_type_hints
from urllib.parse import urlparse

from django.urls import Resolver404, ResolverMatch, resolve
from har2document import (
    Document,
    MarkdownComponent,
    QueryParameter,
    RequestBody,
    RequestHeader,
    ResponseBody,
    convert_har_file_to_documents,
    export_dicts_to_csv,
    export_markdown_to_file,
    render_documents_to_markdown,
)

__all__ = [
    "DjangoViewDoesNotExist",
    "resovle_url",
    "get_django_view_name_from_path",
    "get_path_parameter_from_url",
    "replace_request_path_with_variable",
    "replace_route",
    "DjangoEndpoint",
    "PathParameter",
    "DEFAULT_MASKING_MAPPING",
    "DEFAULT_MARKDOWN_COMPONENT_CLASSES",
]

# TODO: Define DjangoDocument inherit from Document


class DjangoViewDoesNotExist(Exception):
    pass


def resolve_url(url: str) -> ResolverMatch:
    try:
        return resolve(urlparse(url).path)
    except Resolver404:
        raise DjangoViewDoesNotExist


def _is_view_class(match: ResolverMatch) -> bool:
    return hasattr(match.func, "cls")


def _get_view_name(match: ResolverMatch) -> str:
    return match._func_path.split(".")[-1]


def _get_view_path(match: ResolverMatch) -> str:
    return match._func_path


def get_django_view_name_from_path(url: str) -> str:
    match: ResolverMatch = resolve_url(url)

    return (
        _get_view_name(match) if _is_view_class(match) else f"{_get_view_path(match)}()"
    )


def _get_path_parameter_from_match(match: ResolverMatch) -> dict[str, str]:
    return match.kwargs


def get_path_parameter_from_url(url: str) -> dict[str, Any]:
    match: ResolverMatch = resolve_url(url)

    return _get_path_parameter_from_match(match)


def replace_request_path_with_variable(url: str) -> str:
    match: ResolverMatch = resolve_url(url)
    query_string: str = urlparse(url).query

    return f"/{match.route}" + (f"?{query_string}" if query_string else "")


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


DEFAULT_MASKING_MAPPING: dict[str, str] = {}

DEFAULT_MARKDOWN_COMPONENT_CLASSES: list[type[MarkdownComponent]] = [
    DjangoEndpoint,
    PathParameter,
    QueryParameter,
    RequestHeader,
    RequestBody,
    ResponseBody,
]


def run(
    har_file_path: str,
    masking_mapping: dict[str, str] | None = None,
    csv: bool = False,
    markdown: bool = False,
    markdown_component_classes: list[type[MarkdownComponent]] | None = None,
) -> list[Document]:
    _har_file_path: Path = Path(har_file_path)
    _masking_mapping: dict[str, str] = masking_mapping or DEFAULT_MASKING_MAPPING
    _markdown_component_classes: list[type[MarkdownComponent]] = (
        markdown_component_classes or DEFAULT_MARKDOWN_COMPONENT_CLASSES
    )

    documents: list[Document] = convert_har_file_to_documents(
        _har_file_path,
        _masking_mapping,
    )
    if csv:
        export_dicts_to_csv(
            cast(list[dict[str, Any]], documents),
            _har_file_path.with_suffix(".csv"),
            fieldnames=list(get_type_hints(Document).keys()),
        )
    if markdown:
        export_markdown_to_file(
            render_documents_to_markdown(documents, _markdown_component_classes),
            _har_file_path.with_suffix(".md"),
        )
    return documents
