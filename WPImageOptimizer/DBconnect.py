###########################################################################
# IMPORTS
import mysql.connector
from mysql.connector import errorcode



###########################################################################
# DATABASE CONFIG
DEFAULT_DB = dict(
	unix_socket			= '/Applications/MAMP/tmp/mysql/mysql.sock',
	host				= 'localhost',
	port				= '8889',
	database			= 'testerdb',
	user				= 'root',
	password			= 'root',
	raise_on_warnings	= True,
)



###########################################################################
# MYSQL FUNCTIONS

# DATABASE CALLBACK ACTION
def defaultDatabaseResponse(data):
	print(data)

# EXECUTE DB QUERY
def queryDataBase(statement, db_options=DEFAULT_DB, callback=defaultDatabaseResponse):
	# establish connection
	try:
		# connect to DB
		SQL = mysql.connector
		db = SQL.connect(**db_options)
		cursor = db.cursor()
		cursor.execute( statement )
		# loop through the data
		for data in cursor:
			# do something with the data
			callback(data)
	# catch errors connecting to DB
	except SQL.Error as error:
		if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Incorrect username or password")
		elif error.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(error)
	else:
		# Make sure data is committed to the database
		db.commit()
		# close out connection
		cursor.close()
		db.close()



###########################################################################
# VARIABLES
DB_OPT = dict(
	unix_socket			= '/Applications/MAMP/tmp/mysql/mysql.sock',
	host				= 'localhost',
	port				= '8889',
	database			= 'testerdb', #'iheartoldtownorange',
	user				= 'root',
	password			= 'root',
	raise_on_warnings	= True,
)
dbs_table = 'Persons'
dbs_column = 'FirstName'
dbs_before = 'Jose'
dbs_after = 'Joey'



###########################################################################
# MYSQL STATEMENTS

# QUERY ALL ROWS IN TABLE
all_col_in_table = "SELECT `%s` FROM `%s`" % (dbs_column, dbs_table)

# SEARCH AND REPLACE QUERY
search_replace = '''
	UPDATE `%s` SET %s = REPLACE(%s, '%s', '%s') WHERE `%s` LIKE `%s`''' % (
	dbs_table, dbs_column, dbs_column, dbs_before, dbs_after, dbs_column, dbs_before
)



###########################################################################
# MYSQL COMMAND

def doSomeAction(data):
	print(data)
	print('DATA RESPONSE: %s' % data)

queryDataBase(
	statement=all_col_in_table,
	db_options=DB_OPT,
	callback=doSomeAction
)




