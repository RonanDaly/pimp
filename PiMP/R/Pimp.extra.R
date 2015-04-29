.welcome <- function(interval, seconds) {
	flashes <- as.integer(seconds / interval + 1)
	for(i in 1:flashes) {
		if(i%%2) {
			cat("\r", sprintf("%60s", paste("Welcome! Pimping your metabolome in", floor(interval*(flashes-i)), "seconds")))	
		}
		else {
			cat("\r", sprintf("%60s", ""))
		}
		flush.console() 
		Sys.sleep(interval)
	}
	cat("\r", sprintf("%60s", ""), "\n")
}

.goodbye <- function(interval, seconds) {
	flashes <- as.integer(seconds / interval + 1)
	for(i in 1:flashes) {
		if(i%%2) {
			cat("\r", sprintf("%60s", paste(" You've been Pimped. Goodbye! ")))	
		}
		else {
			cat("\r", sprintf("%60s", ""))
		}
		flush.console() 
		Sys.sleep(interval)
	}
	cat("\r", sprintf("%60s", ""), "\n")
}

getJavaHeapSize <- function(default=2048) {
	java.params <- getOption("java.parameters")

	if(!is.null(java.params)) {
		java.params <- as.character(unlist(strsplit(java.params, " ")))
		
		heapsize.idx <- grep("-Xmx", as.character(unlist(strsplit(java.params, " "))))
		if(length(heapsize.idx) > 0) {
			heapsize <- gsub("\\D", "", java.params[heapsize.idx])
			return(heapsize)
		}
		else {
			return(default)
		}
	}
	else {
		return(default)
	}	
}