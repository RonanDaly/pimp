Pimp.statistics.pca <- function(data=matrix(), sample.metadata, factorNames, file=NULL) {
    if(!is.null(file)) {
        svg(filename = file, width=8, height=7)
    }

  smd = as.data.table(sample.metadata, keep.rownames=TRUE)
  count = smd[, list(Rows=list(.I)), by = eval(factorNames)]
  data <- data[,row.names(sample.metadata)]
  
    ##order groups/data.frame alphabetically
    colors <- .groupColors(data, count, factorNames)
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

.groupColors = function(data, count, factors) {
  
  group.names = apply(count[,factors,with=FALSE], 1, function(x) paste(x, collapse=','))
  rows = count$Rows
  names(rows) = seq_len(length(rows))
  sample.group = as.numeric(reverseSplit(rows))
  
    if(length(group.names) < 10) {
        colors <- brewer.pal(9, "Set1")
    } else {
        colors <- rainbow(length(group.names))
    }

    group.colors <- colors[seq_len(length(group.names))]


    sample.colors <- colors[sample.group]

    return(list(colors=sample.colors, key.colors=group.colors, key.text=group.names))
}
