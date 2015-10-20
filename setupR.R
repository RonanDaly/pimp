options('repos'=list(CRAN='http://cran.rstudio.com/', Bioconductor='http://www.bioconductor.org/packages/release/bioc', PuMP='http://puma.ibls.gla.ac.uk/R'))
if (! 'devtools' %in% installed.packages()[,'Package']) {
	install.packages('devtools')
}
library(devtools)
install.packages('mzmatch.R', type="source")
install(pkg='build/PiMP', dependencies=TRUE)
install(pkg='build/PiMPDB', dependencies=TRUE)

#source("http://bioconductor.org/biocLite.R")


