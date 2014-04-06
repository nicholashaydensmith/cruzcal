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
    search = FORM(INPUT(_name='search', _value='Search Events', _onblur="if(this.value == ''){this.value = 'Search Events'}", _onFocus="if(this.value=='Search Events'){this.value=''}", requires=IS_NOT_EMPTY()), INPUT(_type='submit', _action=URL('search')))

    # Is the user logged in?
    # else goto wall
    if (auth.user != None):
        entry = db(db.profile.owner_id == auth.user.id)
        if (entry.count() == 1):
            redirect(URL('default','edit_profile'))
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
    if request.post_vars.search != None:
        redirect(URL('default','search', args=[request.post_vars.search]))

    return dict(search=search, events=SCRIPT(events, _type='text/javascript'),m=message)

def select_user():
    if (auth.has_membership('poster') or auth.has_membership('viewer')):
        redirect(URL('default','wall'))

    return dict()

@auth.requires_login()
def edit_profile():

    g = None
    if (not (auth.has_membership('poster') or auth.has_membership('viewer'))):
        g = request.args(0) or None
    
    if (g == '0'):
        auth.add_membership('viewer')
       
    elif (g == '1'):
        auth.add_membership('poster')
      
        
    entries = db(db.profile.owner_id == get_user_id()).select()
    if (len(entries) > 0):
        r = entries.first().id
        form = SQLFORM(db.profile,
                       record=r,
                       fields =['name'],
                       submit_button = 'Submit',
                       deletable= False,
                       showid=False)
    else:
        form = SQLFORM(db.profile,
                       fields =['name'],
                       submit_button = 'Submit',
                       deletable= False,
                       showid=False)
    
    if (form.process().accepted):
        session.flash = T('Success!')
        redirect(URL('default','wall'))
    else:
        session.flash = T('Check for errors in form.')
    return dict(form=form)

@auth.requires_login()
def wall():
    search = FORM(INPUT(_name='search', _value='Search Events', _onblur="if(this.value == ''){this.value = 'Search Events'}", _onFocus="if(this.value=='Search Events'){this.value=''}", requires=IS_NOT_EMPTY()), INPUT(_type='submit', _action=URL('search')))
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
    if request.post_vars.search != None:
        redirect(URL('default','search', args=[request.post_vars.search]))

    return dict(search=search, events=SCRIPT(events, _type='text/javascript'))

def edit_event():
    return dict()

def new_event():
    form = SQLFORM(db.events)
    if (form.process().accepted):
        session.flash = T('Success!')
        redirect(URL('default','wall',args=[get_user_id()]))
    else:
        session.flash = T('Check for errors in form.')
    return dict(form=form)

def list_format(results):
    # If no results return early
    if len(results) == 0:
        return dict(search=search, results="")
    # Test for another search
    if request.post_vars.search != None:
        redirect(URL('default','search', args=[request.post_vars.search]))

    # Format the Text into HTML
    results_html = []
    for result in results:
        results_html.append(H1(result.title + '\n'))
        results_html.append(H4(str(result.start_time) + ', ' + str(result.end_time)))
        for tag in result.tags:
            results_html.append(H4(str(tag)) + " ")
    return results_html

def cal_format(results):
    results_html = """
	$(document).ready(function() {

		var date = new Date();
		var d = date.getDate();
		var m = date.getMonth();
		var y = date.getFullYear();

		$('#calendar').fullCalendar({
            height: 500,
			editable: false,
			events: ["""
            
    for result in results:
        results_html += "{"
        results_html += "title:'" + result.title + "',"
        results_html += "start:'" + str(result.start_time) + "',"
        results_html += "end:'" + str(result.end_time) + "'"
        results_html += "},"

    results_html += "]});});"
    return results_html

def search():
    search = FORM(INPUT(_name='search', _value='Search Events', _onblur="if(this.value == ''){this.value = 'Search Events'}", _onFocus="if(this.value=='Search Events'){this.value=''}", requires=IS_NOT_EMPTY()), INPUT(_type='submit', _action=URL('search')))
    if request.post_vars.search != None:
        redirect(URL('default','search', args=[request.post_vars.search]))
    # Query the database
    results = get_tag_events(request.args[0])
    list_results_html = list_format(results)
    cal_results_html = cal_format(results)
    return dict(search=search, list_results=P(list_results_html), cal_results=SCRIPT(cal_results_html, _type='text/javascript'))

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
