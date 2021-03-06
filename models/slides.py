import requests
from PIL import Image

import base64
import datetime
import io
import json
import re

from werkzeug import urls

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools import image
from odoo.tools.translate import html_translate
from odoo.exceptions import Warning
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for

class Channel(models.Model):
    _inherit = "slide.channel"
    
    @api.multi
    def _compute_website_url(self):
        super(Channel, self)._compute_website_url()
        for channel in self:
            if channel.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                base_url = channel.get_base_url()
                channel.website_url = '%s/resources/%s' % (base_url, slug(channel))

class Slide(models.Model):
    _inherit = "slide.slide"
    
    @api.multi
    def _compute_website_url(self):
        super(Slide, self)._compute_website_url()
        for slide in self:
            if slide.id:  # avoid to perform a slug on a not yet saved record in case of an onchange.
                base_url = slide.channel_id.get_base_url()
                # link_tracker is not in dependencies, so use it to shorten url only if installed.
                if self.env.registry.get('link.tracker'):
                    url = self.env['link.tracker'].sudo().create({
                        'url': '%s/resources/resource/%s' % (base_url, slug(slide)),
                        'title': slide.name,
                    }).short_url
                else:
                    url = '%s/resources/resource/%s' % (base_url, slug(slide))
                slide.website_url = url

    def _get_embed_code(self):
        base_url = request and request.httprequest.url_root or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url[-1] == '/':
            base_url = base_url[:-1]
        for record in self:
            if record.datas and (not record.document_id or record.slide_type in ['document', 'presentation']):
                slide_url = base_url + url_for('/resources/embed/%s?page=1' % record.id)
                record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (slide_url, 315, 420)
            elif record.slide_type == 'video' and record.document_id:
                if not record.mime_type:
                    # embed youtube video
                    query = urls.url_parse(record.url).query
                    query = query + '&theme=light' if query else 'theme=light'
                    record.embed_code = '<iframe src="//www.youtube.com/embed/%s?%s" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id, query)
                else:
                    # embed google doc video
                    record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
            else:
                record.embed_code = False
