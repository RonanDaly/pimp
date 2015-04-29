options(java.parameters=paste("-Xmx",1024*8,"m",sep=""))

##need to setwd
args <- commandArgs(trailingOnly=TRUE)
analysis.id <- as.integer(args[1])

if(is.na(analysis.id)) {
	stop("Analysis ID must be an integer.")
}

library(PiMPDB)
library(PiMP)
library(yaml)

db.settings <- yaml.load_file("/opt/django/yaml/pimp_database.yml")[['database']]

#db <- new("PiMPDB", dbname="~/Downloads/sqlite3.db", dbtype="sqlite")
db <- new("PiMPDB", dbuser=db.settings$user, dbpassword=db.settings$password, dbname="pimp_prod", dbhost=db.settings$host, dbtype=db.settings$type)

experiment.id <- getExperimentID(db, analysis.id)
project.id <- getProjectID(db, analysis.id)

DATA_DIR = "/opt/django/data/pimp_data/projects"
PROJECT_DIR = file.path(DATA_DIR, project.id)
setwd(PROJECT_DIR)

experiment.samples <- getExperimentSamples(db, experiment.id)
experiment.groups <- getExperimentGroups(db, experiment.id)

samples <- getExperimentSamples(db, experiment.id)
controls <- getExperimentControls(db, experiment.id)
experiment.contrasts <- getExperimentComparisons(db, experiment.id)
# experiment.factors <- getExperimentGroups(db, experiment.id)
# experiment.levels <- getExperimentGroupMembers(db, experiment.factors$id)
analysis.params <- getAnalysisParameters(db, analysis.id)

##files
files <- list()
files$positive <- file.path("samples", "POS", samples$name)
files$negative <- file.path("samples", "NEG", samples$name)

##QCs
blank.idx <- which(controls$type=="blank")
blank.pos <- file.path("calibration_samples", "POS", controls$name[blank.idx])
blank.neg <- file.path("calibration_samples", "NEG", controls$name[blank.idx])

files$positive <- c(files$positive, blank.pos)
files$negative <- c(files$negative, blank.neg)

stds.idx <- which(controls$type=="standard")
stds <- file.path("calibration_samples", "standard", controls$name[stds.idx])

##build groups list
groups <- list()
for(i in 1:nrow(experiment.groups)) {
	members <- getExperimentGroupMembers(db, experiment.groups$id[i], experiment.id)
	for(j in 1:nrow(members)) {
		samples <- getMemberSamples(db, members$id[j])
		groups[[members$name[j]]] <- file_path_sans_ext(samples$name)
	}
}

if(length(blank.idx) > 0) {
	groups$Blank <- file_path_sans_ext(controls$name[blank.idx])
}

#comparisons
contrasts <- experiment.contrasts$name

#databases
databases <- c("kegg", "hmdb", "lipidmaps")
#databases <- getAnnotationDatabases(db, analysis.id)

#params
param.idx <- which(analysis.params$state==1)
if(length(param.idx) > 0) {
	params <- analysis.params[param.idx,]

	for(i in 1:nrow(params)) {
		if(params$name[i]=="ppm") {
			xcms.params$ppm <- params$value[i]
		}
		else if(params$name[i]=="rt.alignment") {
			mzmatch.params$rt.alignment <- "obiwarp"
		}
		else if(params$name[i]=="rtwindow") {
			mzmatch.params$id.rtwindow <- params$value[i]
		}
		else {
			if(is.na(params$value[i])){
				mzmatch.params[[params$name[i]]] <- TRUE
			}
			else {
				mzmatch.params[[params$name[i]]] <- params$value[i]
			}
		}
	}
}

nSlaves <- ifelse(length(unlist(groups)) >= 20, 20, length(unlist(groups)))

Pimp.runPipeline(files=files, groups=groups, standards=stds, contrasts=contrasts, databases=databases, nSlaves=nSlaves, reports="xml", analysis.id=analysis.id, db=db, mzmatch.params=mzmatch.params, xcms.params=xcms.params)
