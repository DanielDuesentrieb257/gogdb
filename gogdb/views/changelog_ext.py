import itertools

import flask

import asyncio

from gogdb import app, api
from gogdb.views.pagination import calc_pageinfo

ITEMS_PER_PAGE = 100


def changelog_ext_page(view):
    page = int(flask.request.args.get("page", "1"))
    limit = int(flask.request.args.get("limit", "100"))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(api.list_changes(limit, page))
    loop.close()

    page_info = calc_pageinfo(page, int(result['pages']), limit)

    changes = result['records']

    page_info["prev_link"] = flask.url_for(
        view, page=page_info["page"] - 1)
    page_info["next_link"] = flask.url_for(
        view, page=page_info["page"] + 1)


    recordgroups = []
    for groupkey, items in itertools.groupby(
            changes, key=lambda record: (record['dateTime'].split(' ')[0], record['game'])):
        recordgroups.append(list(items))

    if view == "changelog_atom":
        response = flask.make_response(flask.render_template(
            "changelog_ext.xml",
            changes=recordgroups,
            page_info=page_info
        ))
        response.mimetype = "application/atom+xml"
        return response

    else:
        return flask.render_template(
            "changelog_ext.html",
            changes=recordgroups,
            page_info=page_info
        )

@app.route("/changelog.xml")
def changelog_atom():
    return changelog_ext_page("changelog_atom")

@app.route("/changelog-ext")
def changelog_ext():
    return changelog_ext_page("changelog_ext")
