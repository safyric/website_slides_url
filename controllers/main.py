# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import Slides

class WebsiteSlidesInherit(Slides):
  @http.route()
