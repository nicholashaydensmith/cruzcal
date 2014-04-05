# coding: utf8

from datetime import datetime

# __CRUZ CAL TABLES__

# tags
db.define_table ('tags',
                 Field('name','string')
                 )

db.tags.name.unique = True

# event
db.define_table ('events',
                 Field('name','string'),
                 Field ('owner_id',default=get_user_id()),
                 Field ('tags','list:string'),
                 Field ('details','json'),
                 Field ('image','upload')
                 )

db.events.owner_id.readable = False
db.events.tags.widget = SQLFORM.widgets.autocomplete(
     request, db.tags.name, limitby=(0,10), min_length=2)

# user
db.define_table ('profile',
                 Field ('name', 'string'),
                 Field ('owner_id',default=get_user_id()),
                 Field ('tags','list:string')
                 )
db.profile.owner_id.readable = False
