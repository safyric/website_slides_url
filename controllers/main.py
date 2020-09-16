# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides

class WebsiteSlidesInherit(WebsiteSlides):
    @http.route('/resources')
    def slides_index(self, *args, **post):
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
    
    def sitemap_slide(env, rule, qs):
        Channel = env['slide.channel']
        dom = sitemap_qs2dom(qs=qs, route='/resources/', field=Channel._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for channel in Channel.search(dom):
            loc = '/resources/%s' % slug(channel)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}
    
    @http.route([
        '''/resources/<model("slide.channel"):channel>''',
        '''/resources/<model("slide.channel"):channel>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/<string:slide_type>''',
        '''/resources/<model("slide.channel"):channel>/<string:slide_type>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>''',
        '''/resources/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>/page/<int:page>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>/<string:slide_type>''',
        '''/resources/<model("slide.channel"):channel>/category/<model("slide.category"):category>/<string:slide_type>/page/<int:page>'''])
    def channel(self, channel, category=None, tag=None, page=1, slide_type=None, sorting='creation', search=None, **kw):
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
    
    @http.route('''/resources/resource/<model("slide.slide", "[('channel_id.can_see', '=', True), ('website_id', 'in', (False, current_website_id))]"):slide>''')
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/pdf_content''')
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/download''')
    def slide_download(self, slide, **kw):
        slide = slide.sudo()
        if slide.download_security == 'public' or (slide.download_security == 'user' and request.env.user and request.env.user != request.website.user_id):
            filecontent = base64.b64decode(slide.datas)
            disposition = 'attachment; filename=%s.pdf' % werkzeug.urls.url_quote(slide.name)
            return request.make_response(
                filecontent,
                [('Content-Type', 'application/pdf'),
                 ('Content-Length', len(filecontent)),
                 ('Content-Disposition', disposition)])
        elif not request.session.uid and slide.download_security == 'user':
            return request.redirect('/web/login?redirect=/resources/resource/%s' % (slide.id))
        return request.render("website.403")
    
    @http.route('''/resources/resource/<model("slide.slide"):slide>/promote''')
    def slide_set_promoted(self, slide, **kwargs):
        slide.channel_id.promoted_slide_id = slide.id
        return request.redirect("/resources/%s" % slide.channel_id.id)
    
    @http.route('/resourcees/resource/like')
    
    @http.route('/resources/resource/dislike')
    
    @http.route(['/resources/resource/send_share_email'])
    
    @http.route('/resources/resource/overlay')
    
    @http.route(['/resources/dialog_preview'])
    def dialog_preview(self, **data):
        Slide = request.env['slide.slide']
        document_type, document_id = Slide._find_document_data_from_url(data['url'])
        preview = {}
        if not document_id:
            preview['error'] = _('Please enter valid youtube or google doc url')
            return preview
        existing_slide = Slide.search([('channel_id', '=', int(data['channel_id'])), ('document_id', '=', document_id)], limit=1)
        if existing_slide:
            preview['error'] = _('This video already exists in this channel <a target="_blank" href="/resources/resource/%s">click here to view it </a>') % existing_slide.id
            return preview
        values = Slide._parse_document_url(data['url'], only_preview_fields=True)
        if values.get('error'):
            preview['error'] = _('Could not fetch data from url. Document or access right not available.\nHere is the received response: %s') % values['error']
            return preview
        return values
    
    @http.route(['/resources/add_slide'])
    def create_slide(self, *args, **post):
        # check the size only when we upload a file.
        if post.get('datas'):
            file_size = len(post['datas']) * 3 / 4 # base64
            if (file_size / 1024.0 / 1024.0) > 25:
                return {'error': _('File is too big. File size cannot exceed 25MB')}

        values = dict((fname, post[fname]) for fname in [
            'name', 'url', 'tag_ids', 'slide_type', 'channel_id',
            'mime_type', 'datas', 'description', 'image', 'index_content', 'website_published'] if post.get(fname))
        if post.get('category_id'):
            if post['category_id'][0] == 0:
                values['category_id'] = request.env['slide.category'].create({
                    'name': post['category_id'][1]['name'],
                    'channel_id': values.get('channel_id')}).id
            else:
                values['category_id'] = post['category_id'][0]

        # handle exception during creation of slide and sent error notification to the client
        # otherwise client slide create dialog box continue processing even server fail to create a slide.
        try:
            slide_id = request.env['slide.slide'].create(values)
        except (UserError, AccessError) as e:
            _logger.error(e)
            return {'error': e.name}
        except Exception as e:
            _logger.error(e)
            return {'error': _('Internal server error, please try again later or contact administrator.\nHere is the error message: %s') % e}
        return {'url': "/resources/resource/%s" % (slide_id.id)}
    
    @http.route('/resources/embed/<int:slide_id>')
    
