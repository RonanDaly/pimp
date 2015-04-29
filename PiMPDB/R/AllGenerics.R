setGeneric("dbconnection", function(object) standardGeneric("dbconnection"))

setGeneric("dbdisconnect", function(object) standardGeneric("dbdisconnect"))

setGeneric("querydb", function(object, query, bind=NULL) standardGeneric("querydb"))

setGeneric("getExperimentID", function(object, analysis.id) standardGeneric("getExperimentID"))

setGeneric("getProjectID", function(object, analysis.id) standardGeneric("getProjectID"))

setGeneric("getExperimentSamples", function(object, experiment.id) standardGeneric("getExperimentSamples"))

setGeneric("getExperimentGroups", function(object, experiment.id) standardGeneric("getExperimentGroups"))

setGeneric("getExperimentGroupMembers", function(object, group.id, experiment.id) standardGeneric("getExperimentGroupMembers"))

setGeneric("getExperimentGroupMembersAll", function(object, group.id, experiment.id) standardGeneric("getExperimentGroupMembersAll"))

setGeneric("getMemberSamples", function(object, member.id) standardGeneric("getMemberSamples"))

setGeneric("getControlMemberSamples", function(object, member.id) standardGeneric("getControlMemberSamples"))

setGeneric("getExperimentComparisons", function(object, experiment.id) standardGeneric("getExperimentComparisons"))

setGeneric("getExperimentComparisonMembers", function(object, comparison.id) standardGeneric("getExperimentComparisonMembers"))

setGeneric("getAnalysisParameters", function(object, analysis.id) standardGeneric("getAnalysisParameters"))

setGeneric("getExperimentControls", function(object, experiment.id) standardGeneric("getExperimentControls"))

setGeneric("getControlGroups", function(object, experiment.id) standardGeneric("getControlGroups"))

setGeneric("getAnnotationDatabases", function(object, analysis.id) standardGeneric("getAnnotationDatabases"))
