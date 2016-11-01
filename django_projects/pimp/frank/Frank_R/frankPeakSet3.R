source(paste(getwd(), '/frank/Frank_R/cachedEic.R', sep=""))
source(paste(getwd(), '/frank/Frank_R/cachedMsms.R', sep=""))

### This is the peak detection workflow based on the RMassBank's script from Emma ###
run_create_peak_method_3 <- function(MS1file, fragmentation_file) {

    print ('In method 3')
    peak_info <- MS1file

    print ('the peak info is')
    print (head(peak_info))
    print ('the fragmentation file is')
    print (fragmentation_file)

    file_details <- c(fragmentation_file, "test")

    test_df <- data.frame(file_details)

    return(test_df)
}