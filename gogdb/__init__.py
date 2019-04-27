from flask import Flask
app = Flask("gogdb")

import gogdb.config

from gogdb.gogdbapi import API
api = API(gogdb.config.APIHOST)

import gogdb.assets
import gogdb.filters
import gogdb.views

