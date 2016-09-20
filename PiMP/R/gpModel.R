#library(gptk)
##library(mvoutlier)
#library(outliers)
#library(mzmatch.R)

#source('batchSetup.R')
#source('tpExpandParam.R')
#source('tpExtractParam.R')
#source("tpCreate.R")
#source('tpObjective.R')
#source('tpGradient.R')


# This function is used to robustly scale vectors to zero
# mean and unit variance - if a single value is put in, then
# that value is used
scaleSingle <- function(vec) {
    if ( length(vec) == 1 ) {
        retval = 0
        attr(retval, 'scaled:center') = vec[1]
        attr(retval, 'scaled:scale') = 1
    } else {
        retval = scale(vec)
    }
    retval
}

# This function gives the objective over _all_ batches and peaks that are
# being used to optimise. It is simply the sum over the individual objectives
objectiveSum <- function(objectiveFunction, params, models) {
  logger <- getPiMPLogger('gpModel.objectiveSum')
  objectives = lapply(models, function(model) if (is.null(model)) { 0 } else { objectiveFunction(params, model)})
  retval = sum(unlist(objectives))
  logdebug('Objective at %s: %s', params, retval, logger=logger)
  retval
}

gObjectiveSum = function(params, models) objectiveSum(gpObjective, params, models)
tObjectiveSum = function(params, models) objectiveSum(tpObjective, params, models)

# This function gives the gradient over _all_ batches and peaks that are
# being used to optimise. It is simply the sum over the individual gradients
gradSum <- function(gradFunction, params, models) {
  logger <- getPiMPLogger('gpModel.gradSum')
  #cat('params: ', params, '\n')
  gradients = lapply(models, function(model) if (is.null(model)) { rep(0, length(params)) } else { gradFunction(params, model)})
  #print(t(data.frame(gradients)))
  retval = apply(do.call(cbind, gradients), 1, sum)
  logdebug('Gradient at %s: %s', params, retval, logger=logger)
  retval
}

gGradSum = function(params, models) gradSum(gpGradient, params, models)
tGradSum = function(params, models) gradSum(tpGradient, params, models)

# This function removes the most egregious outliers from a vector y
# It uses an iterated Grubb's test. The return value specifies which
# values to keep.
removeOutliers <- function(y, p.value=0.05) {
    logger <- getPiMPLogger('Pimp.gpModel.removeOutliers')

	retval = rep(TRUE, length(y))
	testY = y
	
	if (length(testY) < 6) {
		return(retval)
	}
	while ( TRUE ) {
		o = tryCatch(outlier(testY),    warning=function(w) {
		                                    logwarn(w, logger=logger); stop()
		                                },
		                                error=function(e) {
		                                    logerror(e, logger=logger);
		                                    logerror(testY, logger=logger);
		                                    logerror(y, logger=logger)
		                                }
		)
		pos = which(y == o)
		testResult = tryCatch(grubbs.test(testY), warning=function(w) { logwarn(w, logger=logger);
		                                                                logwarn(testY, logger=logger);
		                                                                stop() })
		if ( testResult$p.value < p.value && length(testY) > 5 ) {
			retval[pos] = FALSE
		} else {
			return(retval)
		}
		testY = rm.outlier(testY)
	}
}

tp4Create = function(q, d, X, y, options) tpCreate(4, q, d, X, y, options)



buildModel = function(processCreate, peakData, removeOutliers, options) {
  x = scaleSingle(peakData$time)
  y = scaleSingle(peakData$intensity)

  if ( length(x) == 0 ) {
    model = NULL
  } else {
    if ( removeOutliers ) {
      d = removeOutliers(y)
      correctedX = x[d]
      correctedY = y[d]
      attr(correctedX, 'scaled:center') = attr(x, 'scaled:center')
      attr(correctedX, 'scaled:scale') = attr(x, 'scaled:scale')
      attr(correctedY, 'scaled:center') = attr(y, 'scaled:center')
      attr(correctedY, 'scaled:scale') = attr(y, 'scaled:scale')
      x = correctedX
      y = correctedY
    }
    model = processCreate(1, 1, t(t(x)), t(t(y)), options)
    
    #model = tryCatch(processCreate(1, 1, t(t(x)), t(t(y)), options),
    #                 error=function(e) { print(e); print(x); print(y); blegh() })
    model$nParams = 3
  }
  model
}

getOptimalParameters = function(models, objectiveFun, gradFun, startingPoint=c(0,0,0)) {
  logger <- getPiMPLogger('gpModel.getOptimalParameters')

  initialValues = startingPoint
  optOptions = optimiDefaultOptions()
  optOptions$maxit = 100
  optOptions$display = TRUE
  
  if ( length(models) > 500 ) {
    optModels = models[1:500]
  } else {
    optModels = models
  }
  
  loginfo('Initial Params: %s', initialValues, logger=logger)
  optimisedParams = SCGoptim(initialValues, objectiveFun, gradFun, optOptions, optModels)
  hyperParameters = unlist(optimisedParams)
  loginfo('optimisedParams: %s', hyperParameters, logger=logger)
  hyperParameters
}


# This is the function that produces the models to fit the QC data. These
# models can be used with the correctPeaks function to remove the inter-
# and intra-batch effects. The output is a data frame containing the models
# indexed by batch and peak columns. Each model consists of a Gaussian Process
# regression on the max intensity data, using the time the sample was run, and
# a mean of the data values.
gpRegress <- function(processCreate, objectiveFun, gradFun, expandParamFun, data, batchInformation, hyperParameters=NULL, removeOutliers=FALSE) {
    logger <- getPiMPLogger('gpModel.gpRegress')
    uniqueGroups = unique(batchInformation$batch)
    peaks = unique(data$peak)

    options = gpOptions()
    options$kern$comp = list("rbf","white")
    models = list()
    numModels = length(uniqueGroups) * length(peaks)
	loginfo('Num models: %s', numModels, logger=logger)
	
	peakMeans = list()
	for (peak in peaks) {
    m = mean(data[data$peak == peak,'intensity'])
		peakMeans[[peak]] = m
  }

    outputGroup = vector(mode="numeric", length=numModels)
    outputPeak = vector(mode="numeric", length=numModels)
    outputMean = vector(mode="numeric", length=numModels)
    models = vector(mode="list", length=numModels)

	for ( i in 1:length(uniqueGroups) ) {
		batch = uniqueGroups[i]
		loginfo('Batch %s', batch, logger=logger)
        batchData = data[data$group == batch,]
		for ( j in 1:length(peaks) ) {
			peak = peaks[j]
			#cat('Peak', peak, '\n')
            peakData = batchData[batchData$peak == peak,]
			modelNum = (i - 1) * length(peaks) + j
			logdebug('Batch %s peak %s numSamples %s modelNum %s %s %s %s', batch, peak,
				dim(peakData)[1], modelNum, length(outputGroup), length(outputPeak), length(models), logger=logger)
      model = buildModel(processCreate, peakData, removeOutliers, options)
			outputGroup[modelNum] = as.character(batch)
			outputPeak[modelNum] = peak
      outputMean[modelNum] = peakMeans[[peak]]
			models[modelNum] = list(model)
            #outputGroup = append(outputGroup, batch)
            #outputPeak = append(outputPeak, peak)
            #models = append(models, list(model))
        }
    }

	# If we haven't specified any hyper parameters, try to optimise them.
    if ( is.null(hyperParameters) ) {
      hyperParameters = getOptimalParameters(models, objectiveFun, gradFun)
    }

	# Make sure the models have the correct hyper parameters.
    optimisedModels = lapply(models, function(model) if (is.null(model)) { model } else { expandParamFun(model, hyperParameters)})
    models = data.frame(group=factor(outputGroup), peak=outputPeak, mean=outputMean)
    models$model = optimisedModels
  #output = list()
    #output$models = data.frame(group=outputGroup, peak=outputPeak)
    #output$models$model = optimisedModels
    #output$mean = peakMeans
    models
}

predictFromModel = function(meanVarFunction, model, times, varsigma.return=FALSE) {
    # Scale the inputs.
    centeredTimes = times - attr(model$X, 'scaled:center')
    scaledTimes = centeredTimes / attr(model$X, 'scaled:scale')
    scaledTimes = t(t(scaledTimes))
    # Predict from the Gaussian process regression model
    predictedScaledIntensities = meanVarFunction(model, scaledTimes, varsigma.return=varsigma.return)
    # Finally rescale the outputs and do the inter-batch correction
    if ( varsigma.return ) {
      predictedCenteredIntensities = predictedScaledIntensities$mu * attr(model$y, 'scaled:scale')
      predictedIntensities = list(
        mu=predictedCenteredIntensities + attr(model$y, 'scaled:center'),
        varsigma=attr(model$y, 'scaled:scale')^2 * predictedScaledIntensities$varsigma
      )
      #predictedIntensities$mu = predictedCenteredIntensities + attr(model$y, 'scaled:center')
      #predictedIntensities$varsigma = attr(model$y, 'scaled:scale')^2 * predictedScaledIntensities$varsigma
    } else {
      predictedCenteredIntensities = predictedScaledIntensities * attr(model$y, 'scaled:scale')
      predictedIntensities = predictedCenteredIntensities + attr(model$y, 'scaled:center')
    }
    predictedIntensities
}

predictFromModels <- function(meanVarFunction, output, group, peak, times, intensities) {
	# m is the overall mean for a peak (over all batches)
	#m = output$mean[[peak]]
	#if ( is.null(m) ) {
		# There is no mean for this peak, therefore there are no QC samples
		# for this peak
	#	return(intensities)
	#}

	if ( ! peak %in% output$peak ) {
		return(rep(0, length(intensities)))
	}
    selectedModels = output$model[output$group == group & output$peak == peak]
	if ( length(selectedModels) != 1 ) {
		# Sanity check
		show(group)
		show(peak)
		stop('Should not be getting here')
	}
  m = output$mean[output$group == group & output$peak == peak]
	
	# We are dealing with log intensities in the models.
	intensities = log(intensities)
    model = selectedModels[[1]]
    
    if ( is.null(model) ) {
		# If the model is NULL, we simply do a correction to the mean (inter-batch correction)
        predictedIntensities = intensities - mean(intensities) + m
    } else {
		# Else we do an inter- and intra-batch correction
        predictedIntensities = intensities - predictFromModel(meanVarFunction, model, times) + m
    }
	# The outputs are in linear space
    outputIntensities = exp(predictedIntensities)
}

# This function uses the models obtained from gpRegress to remove
# the inter- and intra-batch effects. The data is the 'raw' data,
# from the peakML files.
correctPeaks <- function(meanVarFunction, output, data, batchInformation, types) {
    logger <- getPiMPLogger('Pimp.gpModel.correctPeaks')

    batches = unique(batchInformation$batch)
    mNames = colnames(data$peakDataMtx)
    dataMtx = data$peakDataMtx
    dataPeakColumn = which(mNames == 'GROUPID')
    dataMeasurementColumn = which(mNames == 'MEASUREMENTID')
    dataIntensityColumn = which(mNames == 'MAXINTENSITY')
    dataSumIntensityColumn = which(mNames == 'SUMINTENSITY')
    measurementNames = getMeasurementColumn(data)
    allPeaks = unique(data$peakDataMtx[,dataPeakColumn])
    wantedIds = getWantedIds(batchInformation, types)

    for (peak in allPeaks) {
		logdebug(peak, logger=logger)
        for (batch in batches) {
			# For each peak and batch, find which samples we are interested in and get the peaks out
            batchFiles = intersect(wantedIds, rownames(batchInformation[batchInformation$batch == batch,]))
            selectedPeaks = which(dataMtx[,dataPeakColumn] == peak & measurementNames %in% batchFiles)
            if ( length(selectedPeaks) == 0 ) {
                next
            }
			# Find the times and intensities for the peaks of interest
            times = batchInformation[measurementNames[selectedPeaks],'time']
            intensities = dataMtx[selectedPeaks,dataIntensityColumn]
			# Find what intensities that model predicts for 
            correctedIntensities = predictFromModels(meanVarFunction, output, batch, peak, times, intensities)
			# Find the scaling factors in linear space
            scaling = correctedIntensities / intensities
			# Do the correction, for the max intensity and sum intensity columns
            data$peakDataMtx[selectedPeaks,dataIntensityColumn] = correctedIntensities
            data$peakDataMtx[selectedPeaks,dataSumIntensityColumn] = data$peakDataMtx[selectedPeaks,dataSumIntensityColumn] * scaling

			# Also do the correction for each of the chromatograms
            for (i in 1:length(selectedPeaks)) {
                p = selectedPeaks[i]
                scale = scaling[i]
                data$chromDataList[[p]]['intensities',] = data$chromDataList[[p]]['intensities',] * scale
            }
        }
    }
    data
}

batchCorrect <- function(groups, files, inputFile, outputFile, sampleTypesToKeep, Rawpath=NULL, qcLabel='QC') {
    batchInformation = createBatchInformationFromGroups(groups, files)
    allData = PeakML.Read(inputFile, Rawpath=Rawpath)
    qcData = getQCData(allData, batchInformation, qcLabel)
    models = gpRegress(gpCreate, gObjectiveSum, gGradSum, gpExpandParam, qcData, batchInformation)
    correctedData = correctPeaks(gpPosteriorMeanVar, models, allData, batchInformation, sampleTypesToKeep)
    PeakML.Write(correctedData, outFileName=outputFile)
} 
