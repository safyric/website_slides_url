# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides

class WebsiteSlidesInherit(WebsiteSlides):
    @http.route('/resources')
    def slides_index(self):
        return super(WebsiteSlidesInherit,self).slides_index(self)
