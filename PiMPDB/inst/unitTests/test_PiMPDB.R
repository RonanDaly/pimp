test_PiMPDB <- function() {
	config <- as.list(read.dcf(file=file.path(getwd(), "..", "PiMPDB", "testData", "pimpdb.txt"), all=TRUE))
	
	sqlitedb <- file.path(getwd(), "..", "PiMPDB", "testData", "sqlite3.db")

	#test sqlite connection
	testdb <- new("PiMPDB",
		dbname=sqlitedb,
		dbtype="sqlite" 

	)
	
	##connection test
	checkTrue(nrow(querydb(testdb, "SELECT name FROM sqlite_master")) > 0, "Check tables exist.")
	checkException(nrow(querydb(testdb, "SELECT name FROM my_funky_table")))
	
	##disconnect from sqlite
	checkTrue(dbdisconnect(testdb))
}