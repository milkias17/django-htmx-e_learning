from django.http import HttpResponse
from django.shortcuts import redirect
from render_block import render_block_to_string


def htmx_redirect(request, url=None):
    if url is None:
        url = request.META.get("HTTP_REFERER")

    if not request.htmx:
        return redirect(url)


def render_html_block(template_name: str, block_name: str, context: dict, request):
    content_html = render_block_to_string(template_name, block_name, context=context, request=request)
    return HttpResponse(content_html, content_type="text/html")
