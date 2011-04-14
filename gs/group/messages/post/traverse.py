# coding=utf-8
from traceback import format_exc
from zope.component import getMultiAdapter
from zope.location.interfaces import LocationError
from zope.publisher.interfaces import NotFound
from gs.group.base.page import GroupPage
from error import NoIDError, Hidden

SUBSYSTEM = 'gs.group.messages.post'
import logging
log = logging.getLogger(SUBSYSTEM) #@UndefinedVariable

class GSPostTraversal(GroupPage):
    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)
        
    def publishTraverse(self, request, name):
        if not request.has_key('postId'):
            self.request['postId'] = name
        return self
    
    def __call__(self):
        # TODO: Handle the 410 (Gone) post here. Hidden posts will 
        # sometimes raise a 410
        # <https://projects.iopen.net/groupserver/ticket/316>
        try:
            retval = getMultiAdapter((self.context, self.request), name="gspost")()
        except NotFound, n:
            self.request.form['q'] = self.request.URL
            self.request.form['r'] = self.request.get('HTTP_REFERER','')
            retval = getMultiAdapter((self.context, self.request),
                        name="new_not_found.html")()
        except NoIDError, n:
            uri = '%s/messages/topics.html' % self.groupInfo.url
            m = 'No post ID in <%s>. Going to <%s>' % \
                (self.request.URL, uri)
            log.info(m)
            retval = self.request.RESPONSE.redirect(uri)
        except Exception, e:
            self.request.form['q'] = self.request.URL
            self.request.form['m'] = format_exc()
            log.error(format_exc())
            retval = getMultiAdapter((self.context, self.request),
                        name="new_unexpected_error.html")()
        return retval

