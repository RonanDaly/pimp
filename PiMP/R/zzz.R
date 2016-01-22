.onLoad <- function(libname = find.package("mzmatch.R"), pkgname = "mzmatch.R") {
	heapsize <- getJavaHeapSize()
	mzmatch.init(memorysize=heapsize, version.1=FALSE)
	logging::basicConfig()
}