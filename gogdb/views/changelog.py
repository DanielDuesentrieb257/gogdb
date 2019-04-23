import flask

from gogdb import app, api
from gogdb.views.pagination import calc_pageinfo
import asyncio

ITEMS_PER_PAGE = 100


@app.route("/changelog")
def changelog():
    page = int(flask.request.args.get("page", "1"))
    limit = ITEMS_PER_PAGE

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(api.list_changes(limit, page))
    loop.close()
    page_info = calc_pageinfo(page, int(result['count']), limit)
    '''
    page = int(flask.request.args.get("page", "1"))

    # Get total number of entries
    total_entries = db.session.query(
        ChangeRecord.timestamp # just a placeholder
    ).group_by(
        ChangeRecord.timestamp, ChangeRecord.type_prim, ChangeRecord.prod_id
    ).count()


    changes = db.session.query(
        ChangeRecord.timestamp, ChangeRecord.type_prim, ChangeRecord.prod_id,
        sqlalchemy.sql.functions.max(model.Product.title).label("title")
    ).join(
        model.Product
    ).group_by(
        ChangeRecord.timestamp, ChangeRecord.type_prim, ChangeRecord.prod_id
    ).order_by(
        ChangeRecord.timestamp.desc()
    ).offset(page_info["from"]).limit(ITEMS_PER_PAGE)

    page_info["prev_link"] = flask.url_for(
        "changelog", page=page_info["page"] - 1)
    page_info["next_link"] = flask.url_for(
        "changelog", page=page_info["page"] + 1)
    '''

    return flask.render_template(
        "changelog.html", changes=result['records'], page_info=page_info)
