Pimp.statistics.pca <- function(data=matrix(), groups=list(), file=NULL) {
	if(!is.null(file)) {
		svg(filename = file, width=8, height=7)
	}

	##order groups/data.frame alphabetically
	groups <- groups[mixedsort(names(groups))]
	data <- data[,as.character(unlist(groups))]

	colors <- .groupColors(data, groups)
	pca <- prcomp(t(na.omit(data)))#, center=TRUE) ##scale=?
	#variance <- pca$sdev^2

	variance <- pca$sdev^2/sum(pca$sdev^2)
    xlab = paste("PC1: ", round(variance[1] * 100, 2), "%", sep = "")
    ylab = paste("PC2: ", round(variance[2] * 100, 2), "%", sep = "")

	#xlab = paste("PC1")#: Variance ", round(variance[1],2), sep="")
	#ylab = paste("PC2")#: Variance ", round(variance[2],2), sep="")
	par(mar=c(5.1, 4.1, 4.1, 8.1), xpd=TRUE)
	plot (pca$x[,1], pca$x[,2], pch=19, col=colors$colors, xlab=xlab, ylab=ylab)#, cex=cexSpan) 
	#text (pca$x[,1], pca$x[,2], colnames( data ), pos= 3 )
			
	#points (pca$x[,1], pca$x[,2], col=colors$colors, bg=colors$colors, pch=21)#, cex=cexSpan)
	legend ("topright",fill=colors$key.colors,colors$key.text, box.lwd = 0, cex=0.6, inset=c(-0.2,0))

	if(!is.null(file)) {
		dev.off()
	}

	return(file)
	#title()
	#xyplot(PC2 ~ PC1, data=as.data.frame(pca$x), pch=19, cex=1, col=colors$colors, )


			## title (paste("neonate vs sixteen week", title, sep = " ")) 
			#title (paste("Genotype 1, 2 and Healthy Control,", "scaled =", CC, sep = " "))
			#text(PCA$x[,1], PCA$x[,2],labels = sampleLabels, pos=3,cex=0.60, font=2)
			
			#dev.off ()
}

.groupColors = function(data, groups) {
	#sample.group <- sapply(colnames(data), function(x, g){grep(paste("\\b",x,"\\b",sep=""),g, fixed=TRUE)}, g=groups)
	sample.group <- sapply(colnames(data), function(x, g){grep(paste("\\b",x,"\\b",sep=""),g)}, g=groups)
	#group.names <- mixedsort(names(groups)[unique(sample.group)])
	group.names <- names(groups)

	if(length(group.names) < 10) {
		colors <- brewer.pal(9, "Set1")
	}
	else {
		colors <- rainbow(length(group.names))
	}
	
	group.colors <- colors[seq_len(length(group.names))]

	
	sample.colors <- colors[sample.group]

	return(list(colors=sample.colors, key.colors=group.colors, key.text=group.names))
}