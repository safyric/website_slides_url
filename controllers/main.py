# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides

class WebsiteSlidesInherit(WebsiteSlides):
    @http.route('/resources')
    def slides_index(self, *args, **post):
        res_super=super(WebsiteSlidesInherit,self).slides_index(*args, **post)
        """ Returns a list of available channels: if only one is available,
            redirects directly to its slides
        """
        domain = request.website.website_domain()
        channels = request.env['slide.channel'].search(domain, order='sequence, id')
        if not channels:
            return request.render("website_slides.channel_not_found")
        elif len(channels) == 1:
            return request.redirect("/resources/%s" % channels.id)
        return request.render('website_slides.channels', {
            'channels': channels,
            'user': request.env.user,
            'is_public_user': request.env.user == request.website.user_id
        })
        return res_super
    
    def sitemap_slide(env, rule, qs):
        res_super=super(WebsiteSlidesInherit,self).sitemap_slide(env, rule, qs)
        Channel = env['slide.channel']
        dom = sitemap_qs2dom(qs=qs, route='/resources/', field=Channel._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for channel in Channel.search(dom):
            loc = '/resources/%s' % slug(channel)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}
        return res_super
    
    @http.route([
        '''/resourcees/<model("slide.channel"):channel>''',
        '''/resources/<model("slide.channel"):channel>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/<string:slide_type>''',
        '''/resources/<model("slide.channel"):channel>/<string:slide_type>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>''',
        '''/resources/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>/<string:slide_type>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>/<string:slide_type>/page/<int:page>'''])
    def channel(self):
        record=super(WebsiteSlidesInherit,self).channel()
        record['pager_url'] = "/resources/%s" % (channel.id)
        return record
        
    
    @http.route('''/resources/resource/<model("slide.slide", "[('channel_id.can_see', '=', True), ('website_id', 'in', (False, current_website_id))]"):slide>''')
    def slide_view(self):
        return super(WebsiteSlidesInherit,self).slide_view(self)
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/pdf_content''')
    def slide_get_pdf_content(self):
        return super(WebsiteSlidesInherit,self).slide_get_pdf_content(self)
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/download''')
    def slide_download(self):
        return super(WebsiteSlidesInherit,self).slide_download(self)
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/promote''')
    def slide_set_promoted(self):
        return super(WebsiteSlidesInherit,self).slide_set_promoted(self)
    
    @http.route('/resourcees/resource/like')
    def slide_like(self):
        return super(WebsiteSlidesInherit,self).slide_like(self)
    
    @http.route('/resources/resource/dislike')
    def slide_dislike(self):
        return super(WebsiteSlidesInherit,self).slide_dislike(self)
    
    @http.route(['/resources/resource/send_share_email'])
    def slide_send_share_email(self):
        return super(WebsiteSlidesInherit,self).slide_send_share_email(self)
    
    @http.route('/resources/resource/overlay')
    def slide_get_next_slides(self):
        return super(WebsiteSlidesInherit,self).slide_get_next_slides(self)
    
    @http.route(['/resources/dialog_preview'])
    def dialog_preview(self):
        return super(WebsiteSlidesInherit,self).dialog_preview(self)
    
    @http.route(['/resources/add_slide'])
    def create_slide(self):
        return super(WebsiteSlidesInherit,self).create_slide(self)
    
    @http.route('/resources/embed/<int:slide_id>')
    def slides_embed(self):
        return super(WebsiteSlidesInherit,self).slide_embed(self)
    
