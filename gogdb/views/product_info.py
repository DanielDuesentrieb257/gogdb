import copy

import flask
import asyncio
from arrow.arrow import Arrow
from datetime import datetime

from gogdb import app,api


@app.route("/product/<int:prod_id>")
@app.route("/product/<int:prod_id>/")
def product_info(prod_id):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    product, prices, discount, countries = loop.run_until_complete(
            asyncio.gather(
                api.product_detail(prod_id),
                api.product_price(prod_id),
                api.product_discount(prod_id),
                api.get_countries()))

    if len(product) == 0:
        flask.abort(404)

    if len(prices) == 0:
        baseprice = []
    else:
        baseprice = prices['baseprice']

    if len(discount) == 0:
        discount = {"labels":[],"values":[]}
    else:
        discount = discount['discount']
        dis_fmt = {"labels":[], "values":[]}
        for dis in discount:
            if dis['discount']:
                dis_fmt["labels"].append(dis['dateTime'])
                dis_fmt["values"].append(dis['discount'])
        discount = dis_fmt
        if len(discount['values']) > 0:
            discount['labels'].append(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            discount['values'].append(discount['values'][len(discount['values'])-1])

    loop.close()

    return flask.render_template(
        "product_info.html",
        product=product,
        baseprice=baseprice,
        discount=discount,
        countries=countries
    )

