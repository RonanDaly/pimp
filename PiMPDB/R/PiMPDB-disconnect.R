#' @export
setMethod("dbdisconnect", "PiMPDB", function(object) {
	con <- dbconnection(object)
	dbDisconnect(con)
})