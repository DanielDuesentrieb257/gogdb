import flask

from gogdb import app, api
from gogdb.views.pagination import calc_pageinfo
import asyncio


@app.route("/changelog")
def changelog():
    page = int(flask.request.args.get("page", "1"))
    limit = int(flask.request.args.get("limit", "100"))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(api.list_changes(limit, page))
    loop.close()

    page_info = calc_pageinfo(page, int(result['pages']), limit)

    page_info['prev_link'] = flask.url_for(
            "changelog", page=page_info['page'] - 1)
    page_info['next_link'] = flask.url_for(
            "changelog", page=page_info['page'] + 1)

    return flask.render_template(
        "changelog.html", changes=result['records'], page_info=page_info)
