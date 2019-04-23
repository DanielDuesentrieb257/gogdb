from flask import Flask
app = Flask("gogdb")

from gogdb.gogdbapi import API
api = API('https://api.gog-db.info')

import gogdb.config
import gogdb.assets
import gogdb.filters
import gogdb.views

