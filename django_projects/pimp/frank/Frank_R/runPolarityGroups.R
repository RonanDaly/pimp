runPolarityGroups <- function (ms1_df, frag_pol_df, pol){


  cat('Running a polarity group', pol)

  source(paste(getwd(), '/frank/Frank_R/frankPeakSet3.R', sep=""))
  ms1     <- subset(ms1_df,polarity==pol)
  frag_f_pol <- subset(frag_pol_df,polarity==pol)
  frags <- data.frame(x= character(0), y = character(0))

  #If the polarity is found in the frag_pol_df
  if (nrow(frag_f_pol)!=0) {

    #Get the name of the fragment file
    frag_file <- toString(frag_f_pol$filename)
    polarity <- frag_f_pol$polarity

    # Run method 3 to get the fragments
    frags <- run_create_peak_method_3(ms1, frag_file)
    }

  print ("returning frags from polarity group via method 3")
  print(frags)
  return(frags)
}