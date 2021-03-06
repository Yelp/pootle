#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_noop as _

from pootle.core.models import Revision
from pootle_app.models import Directory
from pootle_app.models.permissions import PermissionSet, get_pootle_permission
from pootle_language.models import Language
from pootle_project.models import Project
from staticpages.models import StaticPage as Announcement


logger = logging.getLogger(__name__)


def initdb(create_projects=True):
    """Populate the database with default initial data.

    This creates the default database to get a working Pootle installation.
    """
    create_revision()
    create_essential_users()
    create_root_directories()
    create_template_languages()
    if create_projects:
        create_terminology_project()
    create_pootle_permissions()
    create_pootle_permission_sets()
    if create_projects:
        create_default_projects()
    create_default_languages()


def _create_object(model_klass, **criteria):
    instance, created = model_klass.objects.get_or_create(**criteria)
    if created:
        logger.debug(
            "Created %s: '%s'"
            % (instance.__class__.__name__, instance))
    else:
        logger.debug(
            "%s already exists - skipping: '%s'"
            % (instance.__class__.__name__, instance))
    return instance, created


def _create_pootle_user(**criteria):
    user, created = _create_object(get_user_model(), **criteria)
    if created:
        user.set_unusable_password()
        user.save()
    return user


def _create_pootle_permission_set(permissions, **criteria):
    permission_set, created = _create_object(PermissionSet, **criteria)
    if created:
        permission_set.positive_permissions = permissions
        permission_set.save()
    return permission_set


def create_revision():
    Revision.initialize()


def create_essential_users():
    """Create the 'default' and 'nobody' User instances.

    These users are required for Pootle's permission system.
    """
    # The nobody user is used to represent an anonymous user in cases where
    # we need to associate model information with such a user. An example is
    # in the permission system: we need a way to store rights for anonymous
    # users; thus we use the nobody user.
    criteria = {
        'username': u"nobody",
        'full_name': u"any anonymous user",
        'is_active': True,
    }
    _create_pootle_user(**criteria)

    # The 'default' user represents any valid, non-anonymous user and is used
    # to associate information any such user. An example is in the permission
    # system: we need a way to store default rights for users. We use the
    # 'default' user for this.
    #
    # In a future version of Pootle we should think about using Django's
    # groups to do better permissions handling.
    criteria = {
        'username': u"default",
        'full_name': u"any authenticated user",
        'is_active': True,
    }
    _create_pootle_user(**criteria)

    # The system user represents a system, and is used to
    # associate updates done by bulk commands as update_stores.
    criteria = {
        'username': u"system",
        'full_name': u"system user",
        'is_active': True,
    }
    _create_pootle_user(**criteria)


def create_pootle_permissions():
    """Create Pootle's directory level permissions."""

    args = {
        'app_label': "pootle_app",
        'model': "directory",
    }

    pootle_content_type, created = _create_object(ContentType, **args)
    pootle_content_type.name = 'pootle'
    pootle_content_type.save()

    # Create the permissions.
    permissions = [
        {
            'name': _("Can access a project"),
            'codename': "view",
        },
        {
            'name': _("Cannot access a project"),
            'codename': "hide",
        },
        {
            'name': _("Can make a suggestion for a translation"),
            'codename': "suggest",
        },
        {
            'name': _("Can submit a translation"),
            'codename': "translate",
        },
        {
            'name': _("Can review suggestions"),
            'codename': "review",
        },
        {
            'name': _("Can administrate a translation project"),
            'codename': "administrate",
        },
    ]

    criteria = {
        'content_type': pootle_content_type,
    }

    for permission in permissions:
        criteria.update(permission)
        _create_object(Permission, **criteria)


def create_pootle_permission_sets():
    """Create the default permission set for the 'nobody' and 'default' users.

    'nobody' is the anonymous (non-logged in) user, and 'default' is the logged
    in user.
    """
    User = get_user_model()

    nobody = User.objects.get(username='nobody')
    default = User.objects.get(username='default')

    view = get_pootle_permission('view')
    suggest = get_pootle_permission('suggest')
    translate = get_pootle_permission('translate')

    # Default permissions for tree root.
    criteria = {
        'user': nobody,
        'directory': Directory.objects.root,
    }
    _create_pootle_permission_set([view, suggest], **criteria)

    criteria['user'] = default
    _create_pootle_permission_set([view, suggest, translate], **criteria)

    # Default permissions for templates language.
    # Override with no permissions for templates language.
    criteria = {
        'user': nobody,
        'directory': Directory.objects.get(pootle_path="/templates/"),
    }
    _create_pootle_permission_set([], **criteria)

    criteria['user'] = default
    _create_pootle_permission_set([], **criteria)


def require_english():
    """Create the English Language item."""
    criteria = {
        'code': "en",
        'fullname': u"English",
        'nplurals': 2,
        'pluralequation': "(n != 1)",
    }
    en, created = _create_object(Language, **criteria)
    return en


def create_root_directories():
    """Create the root Directory items."""
    root, created = _create_object(Directory, **dict(name=""))
    _create_object(Directory, **dict(name="projects", parent=root))


def create_template_languages():
    """Create the 'templates' and English languages.

    The 'templates' language is used to give users access to the untranslated
    template files.
    """
    _create_object(Language, **dict(code="templates", fullname="Templates"))
    require_english()


def create_terminology_project():
    """Create the terminology project.

    The terminology project is used to display terminology suggestions while
    translating.
    """
    criteria = {
        'code': "terminology",
        'fullname': u"Terminology",
        'source_language': require_english(),
        'checkstyle': "terminology",
    }
    _create_object(Project, **criteria)


def create_default_projects():
    """Create the default projects that we host.

    You might want to add your projects here, although you can also add things
    through the web interface later.
    """
    from pootle_project.models import Project

    en = require_english()

    criteria = {
        'code': u"tutorial",
        'source_language': en,
        'fullname': u"Tutorial",
        'checkstyle': "standard",
        'localfiletype': "po",
        'treestyle': "auto",
    }
    tutorial, created = _create_object(Project, **criteria)

    criteria = {
        'active': True,
        'title': "Project instructions",
        'body': ('<div dir="ltr" lang="en">Tutorial project where users can '
                 'play with Pootle and learn more about translation and '
                 'localisation.<br />For more help on localisation, visit the '
                 '<a href="http://docs.translatehouse.org/projects/'
                 'localization-guide/en/latest/guide/start.html">localisation '
                 'guide</a>.</div>'),
        'virtual_path': "announcements/projects/"+tutorial.code,
    }
    _create_object(Announcement, **criteria)


def create_default_languages():
    """Create the default languages."""
    from translate.lang import data, factory

    from pootle_language.models import Language

    # import languages from toolkit
    for code in data.languages.keys():
        try:
            tk_lang = factory.getlanguage(code)
            criteria = {
                'code': code,
                'fullname': tk_lang.fullname,
                'nplurals': tk_lang.nplurals,
                'pluralequation': tk_lang.pluralequation,
            }
            try:
                criteria['specialchars'] = tk_lang.specialchars
            except AttributeError:
                pass
            _create_object(Language, **criteria)
        except:
            pass
