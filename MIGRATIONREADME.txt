##### IN GITBASH #####

// this is the code for the migration for the added profile picture column

$ flask db migrate -m 'added profile pic'
// below is the resulting text after the top code has been executed
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'users.profile_pic'
Generating C:\flaskBlog\migrations\versions\dsf43fhui34_added_profile_pic.py ...  done
(virt)


$ flask db upgrade
raise exc.CompileError(
sqlalchemy.exc.CompileError: VARCHAR requires a length on dialect mysql
(virt)
// why


$ flask db migrate -m 'added profile pic v1.3'
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
ERROR [flask_migrate] Error: Target database is not up to date.
// why

// !!!!! TO FIX THE ABOVE ERRORS!!!  profile_pic = db.Column(db.String(), nullable=True)
// !!!!! "db.String()" CANT BE EMPTY! I Changed it to db.String(300)

// Run this code from "https://stackoverflow.com/questions/17768940/target-database-is-not-up-to-date"
// It will fix the last error. Use the code below.

$ flask db stamp head

// then 

$ flask db migrate -m 'added profile pic v1.3'

// and finally

$ flask db upgrade


