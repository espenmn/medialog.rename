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

    enable = schema.Bool(
        title=_(u'Enable replacing'),
        required=False,
    )


    search_depth = schema.Int(
        title=_(u'Search depth'),
        description=_(u'Folder levels for search'),  # NOQA: E501
        required=True,
        default=1
    )


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

    period = schema.Bool(
        title=_(u'period to space'),
        required=False,
    )

    hyphen= schema.Bool(
        title=_(u'hyphen to space'),
        required=False,
    )

    star = schema.Bool(
        title=_(u'* to space'),
        required=False,
    )

    yeer = schema.Bool(
        title=_(u'Add year to field year. Dont enable this'),
        required=False,
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

        if self.data.enable:
            find = self.data.find_str
            replace = self.data.replace_str
            search_depth = self.data.search_depth

            folder_path = self.folder_path()
            #folder_path = '/'.join(context.getPhysicalPath())
            folder_path = '/'.join(folder_path)

            all_items = self.context.portal_catalog(portal_type='Image', path={'query': folder_path, 'depth': search_depth})

            for my_image in all_items:
                title = my_image.Title
                #print(title)
                new_title = title.replace(find, replace)

                if self.data.period:
                    new_title = new_title.replace('.', ' ')

                if self.data.hyphen:
                    new_title = new_title.replace('-', ' ')

                if self.data.star:
                    new_title = new_title.replace('*', '')


                title_len = len(new_title.split(" "))
                #import pdb; pdb.set_trace()

                if (title_len > 1):
                    first_word = new_title.split(" ")[0];
                    last_part = new_title.split(" ")[1:]
                    if first_word[0].isdigit():
                        ##obs need to add spaces
                        new_title = ' '.join(last_part) + " " + first_word

                    # take year from title and add it to field 'year'
                    if self.data.yeer:
                        for word in last_part:
                            print(word)
                            if word[0] == "(" and word[-1] == ")":
                                print('will split')
                                word = word[1:-1]
                        print(word)
                        if word.isdigit():
                            if int(word) > 1700 and int(word) < 2040:
                                item.year = int(word)

                #new_title.replace(a, b)
                #print(new_title)

                item = my_image.getObject()

                item.setTitle(new_title)
                transaction.get().commit()

            return 'You need to rebuild catalog now.'

        return 'Portlet is disabled'
