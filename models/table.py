# coding: utf8

from datetime import datetime

# __CRUZ CAL TABLES__

# tags
db.define_table ('tags',
                 Field('name','string')
                 )

db.tags.name.requires.unique = True

# event
db.define_table ('events',
                 Feild ('name','string'),
                 Feild ('owner_id',default=get_user_id()),
                 Feild ('tags','list:string'),
                 Feild ('details','json'),
                 Feild ('image','upload')
                 )

db.events.owner_id.readable = false
db.events.tags.widget = SQLFORM.widgets.autocomplete(
     request, db.tags.name, limitby=(0,10), min_length=2)

# user
db.define_table ('profile',
                 Feild ('name', 'string'),
                 Feild ('owner_id',default=get_user_id()),
                 Feild ('tags','list:string')
                 )
