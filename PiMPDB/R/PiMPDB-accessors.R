#' get Connection to PiMP database
#' 

#' @export
setMethod("dbconnection", "PiMPDB", function(object) object@dbconnection)

#' @export
setMethod("querydb", "PiMPDB", function(object, query, bind) {
	if(!missing(bind)) {
		#query <- sprintf(query, bind)
    query <- do.call(sprintf, c(list(query), bind))
	}
	tryCatch(result <- dbGetQuery(dbconnection(object), query),
		error=function(e) { stop(e) })
	return(result)
})

setMethod("getExperimentID", "PiMPDB", function(object, analysis.id) {
    id <- querydb(object, "select experiment_id from experiments_analysis where id = %d", bind=analysis.id)
    return(as.integer(id$experiment_id))
})

setMethod("getExperimentSamples", "PiMPDB", function(object, experiment.id) {
    samples <- querydb(object,
                       paste("select DISTINCT fileupload_sample.id, fileupload_sample.name",
                      	 	 "from fileupload_sample, groups_sampleattribute, groups_attribute, experiments_attributecomparison, experiments_comparison",
                        	 "where fileupload_sample.id = groups_sampleattribute.sample_id",
                        	 "and groups_sampleattribute.attribute_id = groups_attribute.id",
                        	 "and groups_attribute.id = experiments_attributecomparison.attribute_id",
                        	 "and experiments_attributecomparison.comparison_id = experiments_comparison.id",
                        	 "and experiments_comparison.experiment_id = %d"),
                        bind=experiment.id
                    )
    return(samples)
})

setMethod("getExperimentControls", "PiMPDB", function(object, experiment.id) {
	samples <- querydb(object, 
					   "SELECT DISTINCT fileupload_calibrationsample.id, fileupload_calibrationsample.name, T11.name AS type
						FROM fileupload_calibrationsample 
						INNER JOIN projects_project ON ( fileupload_calibrationsample.project_id = projects_project.id ) 
						INNER JOIN fileupload_sample ON ( projects_project.id = fileupload_sample.project_id ) 
						INNER JOIN groups_sampleattribute ON ( fileupload_sample.id = groups_sampleattribute.sample_id ) 
						INNER JOIN groups_attribute ON ( groups_sampleattribute.attribute_id = groups_attribute.id ) 
						INNER JOIN experiments_attributecomparison ON ( groups_attribute.id = experiments_attributecomparison.attribute_id ) 
						INNER JOIN experiments_comparison ON ( experiments_attributecomparison.comparison_id = experiments_comparison.id ) 
						INNER JOIN experiments_experiment ON ( experiments_comparison.experiment_id = experiments_experiment.id ) 
						INNER JOIN groups_projfileattribute ON ( fileupload_calibrationsample.id = groups_projfileattribute.calibrationsample_id ) 
						INNER JOIN groups_attribute T11 ON ( groups_projfileattribute.attribute_id = T11.id ) WHERE (experiments_experiment.id = %d)",
						bind=experiment.id)
						return(samples)
})


setMethod("getExperimentGroups", "PiMPDB", function(object, experiment.id) {
    groups <- querydb(object, 
                      paste("select distinct groups_group.id, groups_group.name",
                            "from experiments_comparison, experiments_attributecomparison, groups_attribute, groups_group", 
                            "where experiments_comparison.id=experiments_attributecomparison.comparison_id", 
                            "and experiments_attributecomparison.attribute_id = groups_attribute.id", 
                            "and groups_attribute.group_id = groups_group.id",
                            "and experiments_comparison.experiment_id = %d"),
                      bind=experiment.id
              )
    return(groups)
})

setMethod("getControlGroups", "PiMPDB", function(object, experiment.id) {
    groups <- querydb(object, 
                      paste("SELECT DISTINCT groups_group.id, groups_group.name
                            FROM groups_group
                            INNER JOIN groups_attribute ON ( groups_group.id = groups_attribute.group_id )
                            INNER JOIN groups_projfileattribute ON ( groups_attribute.id = groups_projfileattribute.attribute_id )
                            INNER JOIN fileupload_calibrationsample ON ( groups_projfileattribute.calibrationsample_id = fileupload_calibrationsample.id )
                            WHERE (fileupload_calibrationsample.project_id) IN (
                                SELECT projects_project.id 
                                FROM projects_project 
                                INNER JOIN fileupload_sample ON ( projects_project.id = fileupload_sample.project_id ) 
                                INNER JOIN groups_sampleattribute ON ( fileupload_sample.id = groups_sampleattribute.sample_id ) 
                                INNER JOIN groups_attribute ON ( groups_sampleattribute.attribute_id = groups_attribute.id ) 
                                INNER JOIN experiments_attributecomparison ON ( groups_attribute.id = experiments_attributecomparison.attribute_id ) 
                                INNER JOIN experiments_comparison ON ( experiments_attributecomparison.comparison_id = experiments_comparison.id ) 
                                WHERE experiments_comparison.experiment_id = %d )"),
                      bind=experiment.id
              )
    return(groups)
})


setMethod("getExperimentGroupMembers", "PiMPDB", function(object, group.id, experiment.id) {
    group <- querydb(object,
#                     "select id, name from groups_attribute where group_id = %d",
                      paste("select groups_attribute.id, groups_attribute.name",
                            "from groups_attribute, experiments_attributecomparison, experiments_comparison, experiments_experiment",
                            "where groups_attribute.id = experiments_attributecomparison.attribute_id",
                            "and experiments_attributecomparison.comparison_id = experiments_comparison.id",
                            "and experiments_comparison.experiment_id = experiments_experiment.id",
                            "and group_id = %d",
                            "and experiments_experiment.id = %d"),
                      bind=c(group.id, experiment.id)
                    )
    return(group)
})

setMethod("getExperimentGroupMembersAll", "PiMPDB", function(object, group.id) {
    group <- querydb(object,
                      paste("select id, name from groups_attribute where group_id = %d"),
                      bind=group.id
                      )
    return(group)
})


setMethod("getMemberSamples", "PiMPDB", function(object, member.id) {
    members <- querydb(object,
                       paste("select fileupload_sample.id, fileupload_sample.name",
                             "from fileupload_sample, groups_sampleattribute",
                             "where fileupload_sample.id = groups_sampleattribute.sample_id",
                             "and groups_sampleattribute.attribute_id = %d"),
                       bind=member.id
                       )
    return(members)
})

setMethod("getControlMemberSamples", "PiMPDB", function(object, member.id) {
    members <- querydb(object,
                       paste("select fileupload_calibrationsample.id, fileupload_calibrationsample.name",
                             "from fileupload_calibrationsample, groups_projfileattribute",
                             "where fileupload_calibrationsample.id = groups_projfileattribute.calibrationsample_id",
                             "and groups_projfileattribute.attribute_id  = %d"),
                       bind=member.id
                       )
    return(members)
})

setMethod("getExperimentComparisons", "PiMPDB", function(object, experiment.id) {
    comparisons <- querydb(object,
                    paste("select experiments_comparison.id, experiments_comparison.name, group_concat(groups_attribute.name, '-') AS contrast",
                    	  "from experiments_comparison, experiments_attributecomparison, groups_attribute",
                    	  "where experiments_comparison.id = experiments_attributecomparison.comparison_id",
                    	  "and experiments_attributecomparison.attribute_id = groups_attribute.id",
                    	  "and experiments_comparison.experiment_id = %d",
                    	  "group by comparison_id",
                    	  "order by experiments_attributecomparison.control DESC"),
                    	  bind=experiment.id)

    return(comparisons)
})

setMethod("getExperimentComparisonMembers", "PiMPDB", function(object, comparison.id) {
    members <- querydb(object,
                       "select attribute_id from experiments_attributecomparison where comparison_id=%d",
                       bind=comparison.id)
    return(as.character(members$attribute_id))
})

setMethod("getAnalysisParameters", "PiMPDB", function(object, analysis.id) {
    parameters <- querydb(object,
                          paste("select experiments_parameter.name, experiments_parameter.value, experiments_parameter.state",
                                "from experiments_parameter, experiments_params_param, experiments_analysis",
                                "where experiments_parameter.id = experiments_params_param.parameter_id",
                                "and experiments_params_param.params_id = experiments_analysis.params_id",
                                "and experiments_analysis.id = %d"),
                          bind=analysis.id
                         )
    return(parameters)
})

setMethod("getProjectID", "PiMPDB", function(object, analysis.id) {
	id <- querydb(object,
						    paste("SELECT DISTINCT projects_project.id", 
						  		"FROM projects_project",
								"INNER JOIN fileupload_sample ON ( projects_project.id = fileupload_sample.project_id )",
								"INNER JOIN groups_sampleattribute ON ( fileupload_sample.id = groups_sampleattribute.sample_id )",
								"INNER JOIN groups_attribute ON ( groups_sampleattribute.attribute_id = groups_attribute.id )",
								"INNER JOIN experiments_attributecomparison ON ( groups_attribute.id = experiments_attributecomparison.attribute_id )",
								"INNER JOIN experiments_comparison ON ( experiments_attributecomparison.comparison_id = experiments_comparison.id )",
								"INNER JOIN experiments_experiment ON ( experiments_comparison.experiment_id = experiments_experiment.id )",
								"INNER JOIN experiments_analysis ON ( experiments_experiment.id = experiments_analysis.experiment_id )",
								"WHERE experiments_analysis.id = %d"),
								bind=analysis.id)
	return(as.integer(id$id))
	})

setMethod("getAnnotationDatabases", "PiMPDB", function(object, analysis.id) {
  databases <- querydb(object, 
                       paste("SELECT experiments_database.name",
                       "FROM experiments_database",
                       "INNER JOIN experiments_params_databases ON experiments_database.id = experiments_params_databases.database_id",
                       "WHERE experiments_params_databases.params_id = %d"),
                       bind=analysis.id)
  return(as.character(databases))
  })






