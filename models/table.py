# coding: utf8

from datetime import datetime

# __CRUZ CAL TABLES__

# tags
db.define_table ('tags',
                 Field ('name','string'),
                 Field ('num', 'integer')
                 )

db.tags.name.unique = True

# tag association
db.define_table('tag_assoc',
                Field('to_','reference tags'),
                Field('from_','reference tags'),
                Field('num','integer')
                )

# event
db.define_table('events',
                 Field('title','string'),
                 Field ('owner_id',default=get_user_id()),
                 Field ('start_time', 'datetime'),
                 Field ('end_time', 'datetime'),
                 Field ('all_day', 'boolean'),
                 Field ('tags','list:string'),
                 Field ('image','upload'),
                 Field ('details', 'text')
                 )

db.events.owner_id.readable = False
db.events.tags.widget = SQLFORM.widgets.autocomplete(
     request, db.tags.name, limitby=(0,10), min_length=2)

# user
db.define_table('profile',
                 Field ('name', 'string', default=get_user_name()),
                 Field ('owner_id',default=get_user_id()),
                 Field ('tags','list:string')
                 )
db.profile.owner_id.readable = False
