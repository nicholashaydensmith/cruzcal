# -*- coding: utf-8 -*-

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    message = None
    welcome = "Welcome to CruzCal "
    
    # Is the user logged in?
    # else goto wall
    name_or_blank = get_user_name() or ""
    if (auth.user == None):
        message = T(welcome + name_or_blank)
    else:
        redirect(URL('default','wall'))
    
    events = """
	$(document).ready(function() {

		var date = new Date();
		var d = date.getDate();
		var m = date.getMonth();
		var y = date.getFullYear();

		$('#calendar').fullCalendar({
            height: 500,
			editable: true,
			events: 'http://www.google.com/calendar/feeds/nihasmit%40ucsc.edu/public/basic'		});

	});"""
   
    return dict(events=SCRIPT(events, _type='text/javascript'),m=message)

@auth.requires_login()
def edit_profile():
    # URL validation
    u = request.args(0) or None
    if (u == None):
        session.flash = T('Invalid URL')
        redirect(URL('default','index'))
        # User validation
        if (u != get_user_id()):
            session.flash = T('Invalid URL')
            redirect(URL('default','index'))
    
    g = None
    if (not (auth.has_membership('poster') and auth.has_membership('viewer'))):
        g = request.args(1) or None
        
    if (g == 0):
        auth.add_membership('poster')
    elif (g == 1):
        auth.add_membership('viewer')
        
    form = SQLFORM(db.profile,
                   record=r,
                   fields =['name'],
                   submit_button = 'Submit',
                   deletable= False,
                   showid=False)
    
    if (form.process().accepted):
        session.flash = T('Success!')
        redirect(URL('default','wall',args=[get_user_id()]))
    else:
        session.flash = T('Check for errors in form.')
    return dict(form=form)
    
#@auth.requires_login()
def wall():       
    events = """
	$(document).ready(function() {

		var date = new Date();
		var d = date.getDate();
		var m = date.getMonth();
		var y = date.getFullYear();

		$('#calendar').fullCalendar({
            height: 500,
			editable: true,
			events: 'http://www.google.com/calendar/feeds/nihasmit%40ucsc.edu/public/basic'		});

	});"""
   
    return dict(events=SCRIPT(events, _type='text/javascript'))

@auth.requires_membership('poster')
def edit_event():
    return dict()

#@auth.requires_membership('poster')
def new_event():
    form = SQLFORM(db.events)
    if (form.process().accepted):
        session.flash = T('Success!')
        redirect(URL('default','wall',args=[get_user_id()]))
    else:
        session.flash = T('Check for errors in form.')
    return dict(form=form)

def search(tag):
    results = db(db.events.tags==tag)
    return dict(results=results)

@auth.requires_login
def setup_profile():
    # check if current user has a record yet
    rec = None
    entry = db(db.profile.owner_id == auth.user.id)
    if (entry.count() > 0):
        rec = entry.select().first().id # if user has a record find that table id

    form = None

    # based on if user has a record, display new or display an edit
    if (rec == None) :
        form = SQLFORM(db.profile,
                   fields =['name','tags'],
                   submit_button = 'Create CruzCal Profile',
                   showid=False)
    else:
        form = SQLFORM(db.profile,
                   fields =['name','tags'],
                   record = rec,
                   submit_button = 'Update CruzCal Profile',
                   deletable=False,
                   showid = False)

    if form.process().accepted:
        session.flash = T('Sucess!')

    return dict(form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
