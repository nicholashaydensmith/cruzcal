# coding: utf8

from datetime import datetime

# __CRUZ CAL TABLES__

# tags
db.define_table ('tags',
                 Field ('name','string'),
                 Field ('num', 'integer')
                 )

#db.tags.name.requires = IS_NOT_IN_DB(db,'tags.name')

# tag association
db.define_table('tag_assoc',
                Field('to_','string'),
                Field('from_','string'),
                Field('num','integer')
                )

# event
db.define_table('events',
                 Field ('title','string', requires=IS_NOT_EMPTY()),
                 Field ('is_gfeed', 'boolean'),
                 Field ('google_feed', 'string'),
                 Field ('owner_id',default=get_user_id()),
                 Field ('start_time', 'datetime', requires=IS_NOT_EMPTY()),
                 Field ('end_time', 'datetime', requires=IS_NOT_EMPTY()),
                 Field ('all_day', 'boolean'),
                 Field ('tags','list:string', requires=IS_NOT_EMPTY()),
                 Field ('image','upload'),
                 Field ('details', 'text'),
                 Field ('address', 'string'),
                 Field ('city', 'string', requires=IS_NOT_EMPTY()),
                 Field ('zip', 'string'),
                 )

db.events.owner_id.readable = False

# user
db.define_table('profile',
                 Field ('name', 'string', default=get_user_name()),
                 Field ('owner_id',default=get_user_id()),
                 Field ('tags','list:string'),
                 Field ('events','list:integer')
                 )
db.profile.owner_id.readable = False
