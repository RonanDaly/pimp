kegg.up.colours <- function() {
	colours <- c("#FFCCCC", "#FF9999", "#FF6565", "#FF3232", "#FF0000")
	#names(colours) <- fold.bins()
	return(colours)
}

kegg.down.colours <- function() {
	colours <- c("#CCCCFF", "#9999FF", "#6565FF", "#3232FF", "#0000FF")
	#names(colours) <- -fold.bins()
	return(colours)
}

fold.bins <- function() {
	return(c(0.5849625, 1, 2, 3, 4))
}

Pimp.colours <- list(
	identified="gold", 
	annotated="grey",
	foldchange.up=c("#FFCCCC", "#FF9999", "#FF6565", "#FF3232", "#FF0000"),
	foldchange.down=c("#CCCCFF", "#9999FF", "#6565FF", "#3232FF", "#0000FF")
)