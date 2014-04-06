# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

##### This tells web2py to use GAE logins.
if request.env.web2py_runtime_gae:
    from gluon.contrib.login_methods.gae_google_account import GaeGoogleAccount
    auth.settings.login_form = GaeGoogleAccount()
    auth.settings.actions_disabled.append('request_reset_password')
    auth.settings.actions_disabled.append('reset_password')
    auth.settings.actions_disabled.append('retrieve_password')
    auth.settings.actions_disabled.append('email_reset_password')
    auth.settings.actions_disabled.append('change_password')
    auth.settings.actions_disabled.append('retrieve_username')
    auth.settings.actions_disabled.append('verify_email')
    auth.settings.actions_disabled.append('register')
    # auth.settings.actions_disabled.append('profile')
    db.auth_user.email.writable = False

#### How to get an email address.
def get_user_email():
    """Note that this function always returns a lowercase email address."""
    if request.env.web2py_runtime_gae:
        from google.appengine.api import users as googleusers
        u = googleusers.get_current_user()
        if u is None:
            return None
        else:
            return u.email().lower()
    else:
        if auth.user is None:
            return None
        else:
            return auth.user.email.lower()

#### How to get a user ID.
def get_user_id():
    if request.env.web2py_runtime_gae:
        from google.appengine.api import users as googleusers
        u = googleusers.get_current_user()
        if u is None:
            return None
        else:
            return u.user_id()
    else:
        if auth.user is None:
            return None
        else:
            return auth.user.id

#### How to get a user name.
def get_user_name():
    if request.env.web2py_runtime_gae:
        from google.appengine.api import users as googleusers
        u = googleusers.get_current_user()
        if u is None:
            return None
        else:
            return u.nickname()
    else:
        if auth.user is None:
            return None
        else:
            return auth.user.first_name

######################
# Logging
import logging, logging.handlers

class GAEHandler(logging.Handler):
    """
    Logging handler for GAE DataStore
    """
    def emit(self, record):

        from google.appengine.ext import db

        class Log(db.Model):
            name = db.StringProperty()
            level = db.StringProperty()
            module = db.StringProperty()
            func_name = db.StringProperty()
            line_no = db.IntegerProperty()
            thread = db.IntegerProperty()
            thread_name = db.StringProperty()
            process = db.IntegerProperty()
            message = db.StringProperty(multiline=True)
            args = db.StringProperty(multiline=True)
            date = db.DateTimeProperty(auto_now_add=True)

        log = Log()
        log.name = record.name
        log.level = record.levelname
        log.module = record.module
        log.func_name = record.funcName
        log.line_no = record.lineno
        log.thread = record.thread
        log.thread_name = record.threadName
        log.process = record.process
        log.message = record.msg
        log.args = str(record.args)
        log.put()

def get_configured_logger(name):
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # This logger has no handlers, so we can assume it hasn't yet been configured
        # (Configure logger)

        # Create default handler
        if request.env.web2py_runtime_gae:
            # Create GAEHandler
            handler = GAEHandler()
            handler.setLevel(logging.WARNING)
            logger.addHandler(handler)
            logger.setLevel(logging.WARNING)
        else:
            # Create RotatingFileHandler
            import os
            formatter="%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
            handler = logging.handlers.RotatingFileHandler(os.path.join(request.folder,'private/app.log'),maxBytes=1024,backupCount=2)
            handler.setFormatter(logging.Formatter(formatter))
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

        # Test entry:
        # logger.debug(name + ' logger created')
    else:
        pass
        # Test entry:
        # logger.debug(name + ' already exists')

    return logger

# Assign application logger to a global var
logger = get_configured_logger(request.application)

# Assign application logger to a global var
if request.env.web2py_runtime_gae:
    logger = logging
else:
    logger = get_configured_logger(request.application)

# Makes the db and logger available also to modules.
from gluon import current
current.db = db
current.logger = logger

# Let's log the user.
logger.info("User: %r" % get_user_email())
logger.info("ID: %r" % get_user_id())


##################################
### Tag Functions
##################################

def get_relation_strength(name, tag_assoc):
    if (name == tag_assoc.to_):
        other = db(db.tags.name == tag_assoc.from_).select().first()
    elif (name == tag_assoc.from_):
        other = db(db.tags.name == tag_assoc.to_).select().first()
    else: return 0
    return tag_assoc.num / other.num

class TagData:
    def __init__(self, name, rel_str):
        self.name = name
        self.rel_str = rel_str

def get_related_tags(name):
    entries = db((db.tag_assoc.to_ == name) | (db.tag_assoc.from_ == name)).select()
    result = []
    for e in entries:
        if (name == tag_assoc.to_):
            other = tag_assoc.from_
        elif (name == tag_assoc.from_):
            other = tag_assoc.to_
        imin = 0
        imax = len(result)
        while imin < imax:
            imid = round((imin + imax) / 2)
            if (strength < result[imid].rel_str):
                imin = imid + 1
            else:
                imax = imid
        result.insert(imin, TagData(name, strength))
    return result

class ConflictData:
    def __init__(self, event, rel_str):
        self.event = event
        self.rel_str = rel_str

# 'start' and 'end' are UNIX timestamps
def get_tag_conflicts(tag, rel_str, start, end):
    search1 = ((db.events.start > start) & (db.events.start < end))
    search2 = ((start > db.events.start) & (start < db.events.end))
    entries = db(search1 | search2).select()
    result = []
    for e in entries:
        result.append(ConflictData(e, rel_str))
    return result

# 'start' and 'end' are UNIX timestamps
def get_timing_conflicts(tags, start, end):
    rel_tag_data = []
    for tag in tags:
        rel_tag_data = rel_tag_data + get_related_tags(tag)
    i = 0
    for tag_data in rel_tag_data:
        d = False
        for tag in tags:
            if (tag_data.name == tag):
                d = True
                break
        if (d or tag_data.rel_str < 40): rel_tag_data.pop(i)
        i = i + 1
    conflicts = []
    for tag in tags:
        conflicts = conflicts + get_tag_conflicts(tag, 100, start, end)
    for tag_data in rel_tag_data:
        conflicts = conflicts + get_tag_conflicts(tag_data.name, tag_data.rel_str, start, end)
    return conflicts
