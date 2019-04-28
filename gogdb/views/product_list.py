import string
import datetime
import asyncio

import flask

from gogdb import app, api
from gogdb.views.pagination import calc_pageinfo


PRODUCTS_PER_PAGE = 20

ALLOWED_CHARS = set(string.ascii_lowercase + string.digits + ' ' + "'" + ":")



def normalize_search(title):
    return "".join(filter(lambda c: c in ALLOWED_CHARS, title.lower()))


@app.route("/products")
@app.route("/products/")
def product_list():
    page = int(flask.request.args.get("page", "1"))
    limit = int(flask.request.args.get('limit', PRODUCTS_PER_PAGE))
    search = flask.request.args.get("search", "").strip()
    search_norm = normalize_search(search)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(api.query_products(search_norm, limit, page))
    loop.close()

    page_info = calc_pageinfo(page, result['pages'], limit)

    if search != "":
        page_info["prev_link"] = flask.url_for(
            "product_list", page=page_info["page"] - 1, search=search, limit=limit)
        page_info["next_link"] = flask.url_for(
            "product_list", page=page_info["page"] + 1, search=search, limit=limit)
    else:
        page_info["prev_link"] = flask.url_for(
            "product_list", page=page_info["page"] - 1, limit=limit)
        page_info["next_link"] = flask.url_for(
            "product_list", page=page_info["page"] + 1, limit=limit)

    return flask.render_template(
        "product_list.html",
        products=result['products'],
        page_info=page_info,
        search=search
    )
