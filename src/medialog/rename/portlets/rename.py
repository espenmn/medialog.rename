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
        description=_(u'Change (in) image names from. Regex can be written:"([0-9][0-9]) (.*)"'),  # NOQA: E501
        required=True,
        default=u'.jpg'
    )

    replace_str = schema.ASCII(
        title=_(u'Expression (find)'),
        description=_(u'Change to, Regex can be written:"\\2 \\1"'),  # NOQA: E501
        required=True,
    )



    regex = schema.Bool(
        title=_(u'Regular Expression'),
        description=_(u'Tick this if you use regular expressions'),
        required=False,
    )

    move_digit = schema.Bool(
        title=_(u'Move digit'),
        description=_(u'Change 10a Something to Something 10a'),
        required=False,
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

    keep_enabled = schema.Bool(
        title=_(u'Keep enabled'),
        description=_(u'Enable this if you want the portlet functions to stay active after renaming items'),
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

    #@property
    #def turnoff(self):
    #    self.data.enable = False
    #    return 'Portlet is disabled'


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

    def turnoff(self):
        self.data.enable = False
        return 'Portlet is disabled'

    def rename(self):

        if self.data.enable:
            #Turn off search, we need to be sure we dont replac too much
            #self.data.enable = False
            find = self.data.find_str
            replace = self.data.replace_str
            search_depth = self.data.search_depth

            folder_path = self.folder_path()
            #folder_path = '/'.join(context.getPhysicalPath())
            folder_path = '/'.join(folder_path)

            all_items = self.context.portal_catalog(portal_type='Image', path={'query': folder_path, 'depth': search_depth})

            for my_image in all_items:
                title = my_image.Title
                new_title = title


                if self.data.regex:

                    #re.sub(r"([0-9][0-9])\ (.*)", r"\2 \1", "10 Imagename")
                    #from_regex = r"" + re.escape(find)
                    #to_regex   = re.escape(replace)
                    #import pdb; pdb.set_trace()
                    new_title = re.sub(find, replace, title)
                else:
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
                    if self.data.move_digit:
                        first_word = new_title.split(" ")[0];
                        last_part = new_title.split(" ")[1:]
                        if first_word[0].isdigit():
                            ##obs need to add spaces
                            new_title = ' '.join(last_part) + " " + first_word

                    # take year from title and add it to field 'year'
                    try:
                        if self.data.yeer:

                            for word in last_part:
                                print(word)
                                if len(word) > 4:
                                    if word[0] == "(" and word[-1] == ")":
                                        print('will split')
                                        word = word[1:-1]
                            print(word)
                            if word.isdigit():
                                if int(word) > 1700 and int(word) < 2040:
                                    item.year = int(word)
                    finally:
                        print('nothing')

                #new_title.replace(a, b)
                #print(new_title)

                # seem to not reindex properly
                # Do I need to getObject?
                item = my_image.getObject()

                item.setTitle(new_title)
                #No idea why this should be needed
                transaction.get().commit()

                item.reindexObject(idxs=['Title'])

            if not self.data.keep_enabled:
                self.data.enable = False
                self.turnoff()

                return 'Changes done. Portlet is disabled'

        if not self.data.enable:
            return 'Portlet is disabled'
        else:
            return 'Portlet funcions are ACTIVE'
