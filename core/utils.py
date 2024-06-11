from collections.abc import Callable
import functools
from django.contrib.messages import get_messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from render_block import render_block_to_string


def htmx_redirect(request, url=None):
    if url is None:
        url = request.META.get("HTTP_REFERER")

    if not request.htmx:
        return redirect(url)


def render_html_block(template_name: str, block_name: str, context: dict, request):
    content_html = render_block_to_string(
        template_name, block_name, context=context, request=request
    )
    return HttpResponse(content_html, content_type="text/html")


def inject_messages(view: Callable) -> Callable:
    @functools.wraps(view)
    def _wrapper(request: HttpRequest, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if not request.htmx:
            return response

        if set(request.headers) & frozenset(
            {
                "HX-Location",
                "HX-Redirect",
                "HX-Refresh",
            }
        ):
            return response

        if messages := get_messages(request):
            content = render_to_string(
                "partials/alert-message.html",
                context={"hx_oob": True, "messages": messages},
            )
            response.write(content)

        return response

    return _wrapper
