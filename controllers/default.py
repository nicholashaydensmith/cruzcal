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
		redirect(URL('default','wall'))


    events = """
	$(document).ready(function() {
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
def edit_tags() :

	form2 = SQLFORM.factory (Field('tags'),submit_button = 'Update Tags')
	form2.vars.tags = 'List a current tag to delete it.'

	list = []
	tags = []
	record = db(db.profile.owner_id == get_user_id()).select()
	if (record != None and record.first() != None and record.first().tags != None):
		tags = record.first().tags

	if (form2.process().accepted):
		list = form2.vars.tags.split(',') or None
		for tag in list:
			tag = tag.lower().replace(" ", "")
			if (tags and tag in tags):
				tags.remove(tag)
			else:
				tags.append(tag)
	else:
		session.flash = T('Check for errors in form.')

	if (not tags):
		tags = "No tags yet! Add some above."
	elif(record.first() != None):
		record.first().update_record(tags=tags)

	return dict(form2 = form2,tags=tags)

@auth.requires_login()
def wall():
    search = FORM(INPUT(_name='search', _value='Search Events', _onblur="if(this.value == ''){this.value = 'Search Events'}", _onFocus="if(this.value=='Search Events'){this.value=''}", requires=IS_NOT_EMPTY()), INPUT(_type='submit', _action=URL('search')))

    user_id = get_user_id()
    user_tags = db(db.profile.owner_id == user_id).select().first().tags
    results = get_tag_events(user_tags)
    cal_results_html = wrap_cal(cal_format(results))

    if request.post_vars.search != None:
        redirect(URL('default','search', args=[request.post_vars.search]))

    return dict(search=search, events=SCRIPT(cal_results_html, _type='text/javascript'), get_all_cal=get_all_cal(), get_your_cal=get_your_cal())

def edit_event():
	e = request.args(0) or None
	if (e == None):
		redirect(URL('default','wall'))
	form = SQLFORM(db.events, record = e, fields=['title','start_time','end_time','all_day','image','details'],
				   submit_button = 'Update Event', showid = False)

	form2 = SQLFORM.factory (Field('tags'),submit_button = 'Update Tags')
	form2.vars.tags = 'Enter Comma Separated List'
	list = []
	tags = []
	record = db.events[e]
	if (record != None and record.tags != None):
		tags = record.tags

	if (form2.process().accepted):
		list = form2.vars.tags.split(',') or None
		for tag in list:
			if (tags and (tag not in tags)):
				tag.replace(" ", "")
				tags.append(tag.lower())
	else:
		session.flash = T('Check for errors in form.')

	if (not tags):
		tags = "No tags yet! Add some above."
	else:
		record.update_record(tags=tags)

	return dict(form = form, form2 = form2,tags=tags)

def new_event():

    form = SQLFORM(db.events,
                    fields=['title',
                            'start_time',
                            'end_time',
                            'all_day',
                            'tags',
                            'image',
                            'details'])
    gcal = SQLFORM(db.events, fields = ['google_feed', 'tags'])
    gcal.vars.is_gfeed = True

    search = FORM(INPUT(_name='search', _value='Search Events', _onblur="if(this.value == ''){this.value = 'Search Events'}", _onFocus="if(this.value=='Search Events'){this.value=''}", requires=IS_NOT_EMPTY()), INPUT(_type='submit', _action=URL('search')))
    if (form.process().accepted):
        session.flash = T('Success!')
        redirect(URL('default','edit_event',args=[form.vars.id]))
    else:
        session.flash = T('Check for errors in form.')
    return dict(form=form, gcal=gcal)

def list_format(results):
    # If no results return early
    if len(results) == 0:
        return H3("No Results")
    # Test for another search
    if request.post_vars.search != None:
        redirect(URL('default','search', args=[request.post_vars.search]))

    # Format the Text into HTML
    results_html = []
    for result in results:
        title = A(result.title, _href=URL('default', 'view_event', args=[result.id]))
        tag_str = CAT('', '')
        for tag in result.tags:
            tag_str = CAT(tag_str, A(tag, _href=URL('default', 'search', args=[str(tag)])))
            if (tag != result.tags[len(result.tags) - 1]):
                tag_str = CAT(tag_str, ', ')

        inner_html = CAT(H2(title), H4('Start Date: ', str(result.start_time)), H4('End Date: ', str(result.end_time)), CAT(H4('Tags: ', tag_str)))

        div = DIV(inner_html, _id="event-listing")
        results_html.append(div)
        logger.info(div)
    return results_html

def get_all_cal():
    user_tags_db = db(db.tags.id != -1).select()
    user_tags = []
    for tag in user_tags_db:
        user_tags.append(tag)
    results = get_tag_events(user_tags)
    print "All results", results
    return cal_format(results)

def get_your_cal():
    user_id = get_user_id()
    user_tags = db(db.profile.owner_id == user_id).select().first().tags
    results = get_tag_events(user_tags)
    return cal_format(results)

def wrap_cal(cal_html):
    return "$(document).ready(function() {" + cal_html + "});"


def cal_format(results):
    results_html = """
		$('#calendar').fullCalendar({
                        height: 500,
			editable: false,
			events: ["""

    for result in results:
        if result.is_gfeed:
            results_html += result.google_feed
        else:
            results_html += "{"
            results_html += "title:'" + result.title + "',"
            results_html += "start:'" + str(result.start_time) + "',"
            results_html += "end:'" + str(result.end_time) + "'"
            results_html += "},"

    results_html += "]});"
    return results_html

def search():
	# Validate URL
	r_temp = request.args(0) or None
	results = None
	list_results_html = None
	cal_results_html = None

	# Search form
	search = FORM(INPUT(_name='search', _value='Search Events', _onblur="if(this.value == ''){this.value = 'Search Events'}", _onFocus="if(this.value=='Search Events'){this.value=''}", requires=IS_NOT_EMPTY()), INPUT(_type='submit', _action=URL('search')))

	if (r_temp == None):
		redirect(URL('default','wall'))
	else:
		# Query the database
		results = get_tag_events(r_temp)
		list_results_html = list_format(results)
		cal_results_html = wrap_cal(cal_format(results))
		return dict(search=search, list_results=P(list_results_html), cal_results=SCRIPT(cal_results_html, _type='text/javascript'))

	# Redirect with search form value
	if (request.post_vars.search != None):
		redirect(URL('default','search', args=[request.post_vars.search]))

	return dict(search=None, list_results=None,
					cal_results=None)

def search_date():
    if request.vars == []:
        return dict()
    tags = request.vars.tags
    conflicts = get_timing_conflicts(tags, request.vars.start_time, request.vars.end_time);
    cal_results_html = wrap_cal(cal_format(conflicts))
    #URL('static','js/fullcalendar.min.js')
    return SCRIPT(cal_results_html, _type='text/javascript')

def view_event():
    if request.args == []:
        return dict()

    results = db(db.events.id == request.args[0]).select()
    results_html = H1("")
    for result in results:
        results_html += (IMG(_src=URL('default', 'download', args=result.image), _alt="poster"))
        results_html += (H1(result.title))

        #start_date = datetime.strptime(result.start_time, "%Y-%m-%d")
        #end_date = datetime.strptime(result.end_time)

        #time_str = CAT(H3(str(start_date)), H3('-'), H3(str(end_date)))
        #div_center = DIV(time_str, _id="event-list")
        #results_html.append(div_center)
        #results_html += (H3(result.start_time))
        #results_html += (H3(result.end_time))

        tag_str = CAT('', '')
        for tag in result.tags:
            tag_str = CAT(tag_str, A(tag, _href=URL('default', 'search', args=[str(tag)])))
            if (tag != result.tags[len(result.tags) - 1]):
                tag_str = CAT(tag_str, ', ')

    inner_html = CAT(H4('Description'), P(result.details), CAT(P('Tags: ', tag_str)))
    div = DIV(inner_html, _id="event-view")
    results_html.append(div)

    return dict(view_event=results_html)

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
