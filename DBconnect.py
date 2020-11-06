###########################################################################
# IMPORTS
import mysql.connector as SQL
from mysql.connector import errorcode


###########################################################################
# VARIABLES 
DB_HOST = 'localhost'
DB_PORT = '8889'
DB_DATA = 'srcpubshortenerdb'
DB_USER = 'root'
DB_PSWD = 'root'
DB_LOGERROR = True
DB_SOCK = '/Applications/MAMP/tmp/mysql/mysql.sock'

search_table = 'short_urls'
search_column = 'short_code'
search_for = 'jgllc'
replace_with = 'jg123'

###########################################################################
# DATABASE CONFIG
db_opt = dict(
	unix_socket			= DB_SOCK,
	host				= DB_HOST,
	port				= DB_PORT,
	database			= DB_DATA,
	user				= DB_USER,
	password			= DB_PSWD,
	raise_on_warnings	= DB_LOGERROR
)



###########################################################################
# MYSQL STATEMENTS

# SAMPLE QUERY: UPDATE 'MySQL_Table' SET 'MySQL_Table_Column' = REPLACE('MySQL_Table_Column', 'oldString', 'newString') WHERE 'MySQL_Table_Column' LIKE 'oldString%'
SearchAndReplace = "UPDATE `%s` SET %s = REPLACE(%s, '%s', '%s') WHERE `%s` LIKE `%s`" % (
	search_table, search_column,
	search_column, search_for, replace_with,
	search_column, search_for
)

SearchAndReplace_2 = "UPDATE `%s` SET %s = REPLACE(%s, '%s', '%s') WHERE `%s` LIKE '%s%s';" % (
	search_table, search_column, search_column,
	search_for, replace_with,
	search_column, search_for, '%'
)

# QUERY ALL ROWS IN TABLE
stmt = "SELECT * FROM `%s`" % search_table

query = (stmt)
print(SearchAndReplace)
print(SearchAndReplace_2)
#print(query_all_rows)

# first connect to DB
try:
 	db = SQL.connect(**db_opt)
 	cursor = db.cursor()
 	cursor.execute( SearchAndReplace_2 )

# catch errors connecting to DB
except SQL.Error as error:
	if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Incorrect username or password")
	elif error.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exist")
	else:
		print(error)
else:
	db.close()


'''
cursor = db.cursor()
wp_post_rows = cursor.execute("select * from wp_posts");
print(wp_post_rows)
db.close()
'''