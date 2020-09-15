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
        res_super=super(WebsiteSlidesInherit,self).channel(channel, category=None, tag=None, page=1, slide_type=None, sorting='creation', search=None, **kw)
        if not channel.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        user = request.env.user
        Slide = request.env['slide.slide']
        domain = [('channel_id', '=', channel.id)]
        pager_url = "/resources/%s" % (channel.id)
        pager_args = {}

        if search:
            domain += [
                '|', '|',
                ('name', 'ilike', search),
                ('description', 'ilike', search),
                ('index_content', 'ilike', search)]
            pager_args['search'] = search
        else:
            if category:
                domain += [('category_id', '=', category.id)]
                pager_url += "/category/%s" % category.id
            elif tag:
                domain += [('tag_ids.id', '=', tag.id)]
                pager_url += "/tag/%s" % tag.id
            if slide_type:
                domain += [('slide_type', '=', slide_type)]
                pager_url += "/%s" % slide_type

        if not sorting or sorting not in self._order_by_criterion:
            sorting = 'date'
        order = self._order_by_criterion[sorting]
        pager_args['sorting'] = sorting

        pager_count = Slide.search_count(domain)
        pager = request.website.pager(url=pager_url, total=pager_count, page=page,
                                      step=self._slides_per_page, scope=self._slides_per_page,
                                      url_args=pager_args)

        slides = Slide.search(domain, limit=self._slides_per_page, offset=pager['offset'], order=order)
        values = {
            'channel': channel,
            'category': category,
            'slides': slides,
            'tag': tag,
            'slide_type': slide_type,
            'sorting': sorting,
            'user': user,
            'pager': pager,
            'is_public_user': user == request.website.user_id,
            'display_channel_settings': not request.httprequest.cookies.get('slides_channel_%s' % (channel.id), False) and channel.can_see_full,
        }
        if search:
            values['search'] = search
            return request.render('website_slides.slides_search', values)

        # Display uncategorized slides
        if not slide_type and not category:
            category_datas = []
            for category in Slide.read_group(domain, ['category_id'], ['category_id']):
                category_id, name = category.get('category_id') or (False, _('Uncategorized'))
                category_datas.append({
                    'id': category_id,
                    'name': name,
                    'total': category['category_id_count'],
                    'slides': Slide.search(category['__domain'], limit=4, offset=0, order=order)
                })
            values.update({
                'category_datas': category_datas,
            })
        return request.render('website_slides.home', values)
        return res_super
        
    
    @http.route('''/resources/resource/<model("slide.slide", "[('channel_id.can_see', '=', True), ('website_id', 'in', (False, current_website_id))]"):slide>''')
    def slide_view(self):
        return super(WebsiteSlidesInherit,self).slide_view()
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/pdf_content''')
    def slide_get_pdf_content(self):
        return super(WebsiteSlidesInherit,self).slide_get_pdf_content()
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/download''')
    def slide_download(self):
        return super(WebsiteSlidesInherit,self).slide_download(self)
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/promote''')
    def slide_set_promoted(self):
        return super(WebsiteSlidesInherit,self).slide_set_promoted()
    
    @http.route('/resourcees/resource/like')
    def slide_like(self):
        return super(WebsiteSlidesInherit,self).slide_like()
    
    @http.route('/resources/resource/dislike')
    def slide_dislike(self):
        return super(WebsiteSlidesInherit,self).slide_dislike()
    
    @http.route(['/resources/resource/send_share_email'])
    def slide_send_share_email(self):
        return super(WebsiteSlidesInherit,self).slide_send_share_email()
    
    @http.route('/resources/resource/overlay')
    def slide_get_next_slides(self):
        return super(WebsiteSlidesInherit,self).slide_get_next_slides()
    
    @http.route(['/resources/dialog_preview'])
    def dialog_preview(self):
        return super(WebsiteSlidesInherit,self).dialog_preview()
    
    @http.route(['/resources/add_slide'])
    def create_slide(self):
        return super(WebsiteSlidesInherit,self).create_slide()
    
    @http.route('/resources/embed/<int:slide_id>')
    def slides_embed(self):
        return super(WebsiteSlidesInherit,self).slide_embed()
    
