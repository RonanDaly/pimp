#' Constructor method of PiMPDB class
#'
#' Class \code{PiMPDB} defines a PiMPDB database connection object
#'
#' @param dbname database name
#' @param dbuser database user name
#' @param dbpassword database password
#' @param dbhost database hostname
#' @param dbtype database type e.g. sqlite, mysql
#' @return \code{PiMPDB} S4 object
#'
#' @examples 
#'
#' \dontrun{mydb1 <- new("PiMPDB", dbname="pimp.db", dbtype="sqlite")}
#' \dontrun{mydb2 <- new("PiMPDB", dbname="pimpdb", dbuser="pimp", dbpassword="mypassword", dbhost="localhost", dbtype="mysql")}
#' @export

setMethod("initialize", "PiMPDB", function(.Object, dbname="character", dbuser="character", dbpassword="character", dbhost="character", dbport=0, dbtype="character", ...) {
	if(dbtype=="mysql") {
		con <- dbConnect(RMySQL::MySQL(), user=dbuser, password=dbpassword, dbname=dbname, host=dbhost, port=dbport)
	}
	else if(dbtype=="sqlite") {
		con <- dbConnect(RSQLite::SQLite(), dbname=dbname)
	}
	else {
		stop(paste(dbtype, "is not a recognised DBMS."))
	}
	.Object@dbconnection <- con
	callNextMethod(.Object)
})