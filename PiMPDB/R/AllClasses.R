#' An S4 class to represent a PiMPDB connection.
#'
#' 
#'
#' @slot dbconnection A DBMS specific DBIConnection e.g. RSQLite or RMySQL
#' @export
setClass("PiMPDB",
    slots = c(
        dbconnection = "DBIConnection"
    )
)
