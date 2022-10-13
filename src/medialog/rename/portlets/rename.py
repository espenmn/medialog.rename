# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Acquisition import aq_inner
from medialog.rename import _
from plone import schema
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope.component import getMultiAdapter
from zope.interface import implementer

from plone import api
import transaction
import re



class IRenamePortlet(IPortletDataProvider):
    find_str = schema.TextLine(
        title=_(u'Expression (find)'),
        description=_(u'Change (in) image names from'),  # NOQA: E501
        required=True,
        default=u'.jpg'
    )

    replace_str = schema.TextLine(
        title=_(u'Expression (find)'),
        description=_(u'Change to'),  # NOQA: E501
        required=True,
        default=u''
    )


@implementer(IRenamePortlet)
class Assignment(base.Assignment):
    schema = IRenamePortlet

    def __init__(self, find_str='', replace_str=''):
        self.find_str = find_str
        self.replace_str = replace_str

    @property
    def title(self):
        return _(u'Replace Portlet')


class AddForm(base.AddForm):
    schema = IRenamePortlet
    form_fields = field.Fields(IRenamePortlet)
    label = _(u'Add Replace patternt')
    description = _(u'This portlet is for replacing image names in folder.')

    def create(self, data):
        return Assignment(
            find_str=data.get('find_str', ''),
            replace_str=data.get('replace_str', ''),
        )


class EditForm(base.EditForm):
    schema = IRenamePortlet
    form_fields = field.Fields(IRenamePortlet)
    label = _(u'Edit Replace Portlet')
    description = _(u'This portlet is used for replacing image names.')


class Renderer(base.Renderer):
    schema = IRenamePortlet
    _template = ViewPageTemplateFile('rename.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = aq_inner(self.context)
        self.folder_path = context.getPhysicalPath
        portal_state = getMultiAdapter(
            (context, self.request),
            name=u'plone_portal_state'
        )
        self.anonymous = portal_state.anonymous()

    def render(self):
        return self._template()

    #@property
    #def replace(self):
    #    """Show the portlet only if there are one or more elements and
    #    not an anonymous user."""
    #    return not self.anonymous and self.data()


    #def find_str(self):
    #    """Show the find string"""
    #    return self.data.find_str


    def rename(self):
        import pdb; pdb.set_trace()
        find = self.data.find_str
        replace = self.data.replace_str

        folder_path = self.folder_path()

        all_items = self.context.portal_catalog(portal_type='Image', path={'query': folder_path,})

        for my_image in all_items:
            title = my_image.Title
            #print(title)
            new_title = title.replace(find, replace)
            new_title = new_title.replace('.', ' ')
            new_title = new_title.replace('-', ' ')
            new_title = new_title.replace('*', '')


            title_len = len(new_title.split(" "))
            if (title_len > 1):
                first_word = new_title.split(" ")[0];
                if first_word[0].isdigit():
                    new_title = new_title.split(" ")[1] + " " + first_word 

            #new_title.replace(a, b)
            #print(new_title)

            item = my_image.getObject()

            item.setTitle(new_title)
            transaction.get().commit()

        return 'You need to rebuild catalog now.'
