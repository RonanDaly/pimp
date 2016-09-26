/**
 * @author MC
 * @description : Fonctions to map data on metabolic networks
 */
metExploreD3.GraphMapping = {

	compareMappingConditionChart : function(){
		var sessions = _metExploreViz.getSessionsSet();
		var arrayNodes = [];
		var mappingName = [];
		var condName = [];
		for (var key in sessions) {
			mappingName.push(sessions[key].getActiveMapping());
			condName.push(sessions[key].isMapped());
			if(key!='viz'){
				arrayNodes = sessions[key].getD3Data().getNodes().concat(arrayNodes);
			}
		}

		var categories = [];
		arrayNodes.forEach(function(node){
			var index = arrayNodes.filter(function(n){ return n.getIdentifier()==node.getIdentifier(); });
			if(index.length>1 && categories.indexOf(node)==-1 && node.getMappingDataByNameAndCond(mappingName[0], condName[0])!=undefined)
			 	categories.push(node);
			
		});

		var categoriesName=categories.map(function(node){return node.getName()});

		var mapping = _metExploreViz.getMappingByName(mappingName);
		var dataCond1 = categories.map(function(node){return -Math.abs(parseInt(node.getMappingDataByNameAndCond(mappingName[0], condName[0]).getMapValue()))});
		var dataCond2 = categories.map(function(node){return Math.abs(parseInt(node.getMappingDataByNameAndCond(mappingName[1], condName[1]).getMapValue()))});

        var conditions2=
        [
            {
                name: condName[0],
                data: dataCond1
            }, {
                name: condName[1],
                data: dataCond2
            }
        ];


        // donnees.forEach(function(aData){
        //     aData.color=scale(aData.z);
        // });

        var dataChart2 = {categories:categoriesName, conditions:conditions2};
        var compareChart = new MetXCompareBar(dataChart2, 1300, categoriesName.length*15, "xaxis", "yaxis", mappingName[0]+" analysis");

		// console.log(d3.select(compareChart));
		// var array = [];
		// d3.select(compareChart).select('svg').selectAll('.highcharts-series').selectAll('rect').each(function(){array.push(this.height.animVal.value)});
		
		// console.log(array);
		// var scale = d3.scale.linear()
  //           .domain([Math.min.apply(null, array),Math.max.apply(null, array)])
  //           .range([sessions["viz"].getColorMappingsSet()[1].getValue(),sessions["viz"].getColorMappingsSet()[0].getValue()]);
		
		// d3.select(compareChart).selectAll('svg').selectAll('.highcharts-series').selectAll('rect').attr('fill', function(){return scale(this.height.animVal.value)})
		
		return compareChart;
	},
	/***********************************************
	* Mapping to data from file
	* This function will assignmapping value to each nodes in datas
	*/
	mapNodeDataFile: function(mapping, objects) {
		var session = _metExploreViz.getSessionById('viz');
		var force = session.getForce();
		force.stop(); 
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		if(myMask!= undefined){
			metExploreD3.showMask(myMask);
	        setTimeout(
			function() {
				var networkData = session.getD3Data();
				var conditions = mapping.getConditions();
				var nodes = d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node");
				var node = undefined;
				switch (mapping.getTargetLabel()) {
				    case "reactionDBIdentifier":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	objects.forEach(function(obj){
								var map = new MappingData(obj[mapping.getTargetLabel()], mapping.getName(), conditions[i], obj[conditions[i]]);
								mapping.addMap(map);
								node = networkData.getNodeByDbIdentifier(obj[mapping.getTargetLabel()]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], obj[conditions[i]]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "reactionId":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	objects.forEach(function(obj){
								var map = new MappingData(obj[mapping.getTargetLabel()], mapping.getName(), conditions[i], obj[conditions[i]]);
								mapping.addMap(map);
								node = networkData.getNodeByDbIdentifier(obj[mapping.getTargetLabel()]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], obj[conditions[i]]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "metaboliteId":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	objects.forEach(function(obj){
								var map = new MappingData(obj[mapping.getTargetLabel()], mapping.getName(), conditions[i], obj[conditions[i]]);
								mapping.addMap(map);
								node = networkData.getNodeByDbIdentifier(obj[mapping.getTargetLabel()]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], obj[conditions[i]]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "metaboliteDBIdentifier":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	objects.forEach(function(obj){
								var map = new MappingData(obj[mapping.getTargetLabel()], mapping.getName(), conditions[i], obj[conditions[i]]);
								mapping.addMap(map);
								node = networkData.getNodeByDbIdentifier(obj[mapping.getTargetLabel()]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], obj[conditions[i]]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "inchi":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	objects.forEach(function(obj){
								var map = new MappingData(obj[mapping.getTargetLabel()], mapping.getName(), conditions[i], obj[conditions[i]]);
								mapping.addMap(map);
								node = networkData.getNodeByMappedInchi(obj[mapping.getTargetLabel()]);
								if(node!=undefined){
									node.forEach(function(n){
										var mapNode = new MappingData(n, mapping.getName(), conditions[i], obj[conditions[i]]);
										n.addMappingData(mapNode);
									});
								}
							});
				        };
				        break;
				    default:
        				metExploreD3.displayMessage("Warning", 'The type of node "' + mapping.getTargetLabel() + '" isn\'t know.')
				}
							
				metExploreD3.hideMask(myMask);

				var anim=metExploreD3.GraphNetwork.isAnimated("viz");
				if (anim=='true') {
					var force = session.getForce();
					
					if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
						force.resume();
					}
				}
	   		}, 1);
		}
	},
	/***********************************************
	* Mapping to data
	* This function will assignmapping value to each nodes in datas
	*/
	mapNodeData: function(mapping, lines) {
		console.log(lines);
		var session = _metExploreViz.getSessionById('viz');
		var force = session.getForce();
		force.stop(); 
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
	        setTimeout(
			function() {
				var networkData = session.getD3Data();
				var conditions = mapping.getConditions();
				var nodes = d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node");
				var node = undefined;
				switch (mapping.getTargetLabel()) {
				    case "reactionDBIdentifier":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	lines.forEach(function(line){
								var map = new MappingData(line[0], mapping.getName(), conditions[i], line[i+1]);
								mapping.addMap(map);
								node = networkData.getNodeByDbIdentifier(line[0]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], line[i+1]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "reactionId":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	lines.forEach(function(line){
								var map = new MappingData(line[0], mapping.getName(), conditions[i], line[i+1]);
								mapping.addMap(map);
								node = networkData.getNodeById(line[0]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], line[i+1]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "metaboliteId":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	lines.forEach(function(line){
								var map = new MappingData(line[0], mapping.getName(), conditions[i], line[i+1]);
								mapping.addMap(map);
								node = networkData.getNodeById(line[0]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], line[i+1]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "metaboliteDBIdentifier":
				        for (var i = conditions.length-1 ; i >= 0; i--) {
				        	lines.forEach(function(line){
								var map = new MappingData(line[0], mapping.getName(), conditions[i], line[i+1]);
								mapping.addMap(map);
								node = networkData.getNodeByDbIdentifier(line[0]);
								if(node!=undefined){
									var mapNode = new MappingData(node, mapping.getName(), conditions[i], line[i+1]);
									node.addMappingData(mapNode);
								}
							});
				        };
				        break;
				    case "inchi":
				        // Blah
				        break;
				    default:
        				metExploreD3.displayMessage("Warning", 'The type of node "' + mapping.getTargetLabel() + '" isn\'t know.')
				}
							
				metExploreD3.hideMask(myMask);

				var anim=metExploreD3.GraphNetwork.isAnimated("viz");
				if (anim=='true') {
					var force = session.getForce();
					
					if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
						force.resume();
					}
				}
	   		}, 1);
		}
	},

	/***********************************************
	* Mapping to binary data 0 1
	* This function will look at metabolites that have data
	* maped and will color their stroke in red 
	* !!!!! Have to be modified in order to do some batch
	* rendering
	*/
	mapNodes : function(mappingName, func) {
		
		metExploreD3.onloadMapping(mappingName, function(){

			d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
				.filter(function(d){
					if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return false;
					else return true;
				})
				.attr("mapped", "false")
				.selectAll("rect.stroke")
				.remove();		

			var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
			var mapping = _metExploreViz.getMappingByName(mappingName);
			if(myMask!= undefined){

				metExploreD3.showMask(myMask);
		        setTimeout(
					function() {
						
						var session = _metExploreViz.getSessionById('viz');
						var force = session.getForce();
						force.stop(); 
						var conditions = mapping.getConditions();
						conditions.forEach(
							function(condition)
							{
								d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
									.filter(function(d){
										if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return true;
										else return false;
									})
									.each(
										function(d) {
											
											if(d.getBiologicalType() == 'reaction' )
											{
												if(d.getMappingDataByNameAndCond(mapping.getName(), condition) != null ){
													var reactionStyle = metExploreD3.getReactionStyle();

													_MyThisGraphNode.addText(d, 'viz',reactionStyle);

													d3.select(this)
														.attr("mapped","true")
														.insert("rect", ":first-child")
														.attr("class", "stroke")
														.attr("width", parseInt(d3.select(this).select(".reaction").attr("width"))+10)
														.attr("height", parseInt(d3.select(this).select(".reaction").attr("height"))+10)
														.attr("rx", parseInt(d3.select(this).select(".reaction").attr("rx"))+5)
														.attr("ry",parseInt(d3.select(this).select(".reaction").attr("ry"))+5)
														.attr("transform", "translate(-" + parseInt(parseInt(d3.select(this).select(".reaction").attr("width"))+10) / 2 + ",-"
																				+ parseInt(parseInt(d3.select(this).select(".reaction").attr("height"))+10) / 2
																				+ ")")
														.style("opacity", '0.5')
														.style("fill", 'red');
													session.addSelectedNode(d.getId());

												}
											}
											else
											{
												if(d.getBiologicalType() == 'metabolite')
												{
													var id = d3.select(this).select(".metabolite").attr("identifier");
													
													if(d.getMappingDataByNameAndCond(mapping.getName(), condition) != null){
														var metaboliteStyle = metExploreD3.getReactionStyle();
														
														_MyThisGraphNode.addText(d, 'viz', metaboliteStyle);

														d3.select(this)
															.attr("mapped","true")
															.insert("rect", ":first-child")
															.attr("class", "stroke")
															.attr("width", parseInt(d3.select(this).select(".metabolite").attr("width"))+10)
															.attr("height", parseInt(d3.select(this).select(".metabolite").attr("height"))+10)
															.attr("rx", parseInt(d3.select(this).select(".metabolite").attr("rx"))+5)
															.attr("ry",parseInt(d3.select(this).select(".metabolite").attr("ry"))+5)
															.attr("transform", "translate(-" + parseInt(parseInt(d3.select(this).select(".metabolite").attr("width"))+10) / 2 + ",-"
																					+ parseInt(parseInt(d3.select(this).select(".metabolite").attr("height"))+10) / 2
																					+ ")")
															.style("opacity", '0.5')
															.style("fill", 'red');
														session.addSelectedNode(d.getId());
													}
												}
											}
										}
									)		

								//d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
									.each(
										function(d) {
											if(d3.select(this).select(".stroke")[0][0]==null)
											{
												if(d.getBiologicalType() == 'reaction' )
												{
													if(d.getMappingDataByNameAndCond(mapping.getName(), condition) != null ){
														var reactionStyle = metExploreD3.getReactionStyle();

														_MyThisGraphNode.addText(d, 'viz',reactionStyle);

														d3.select(this)
															.insert("rect", ":first-child")
															.attr("class", "stroke")
															.attr("width", parseInt(d3.select(this).select(".reaction").attr("width"))+10)
															.attr("height", parseInt(d3.select(this).select(".reaction").attr("height"))+10)
															.attr("rx", parseInt(d3.select(this).select(".reaction").attr("rx"))+5)
															.attr("ry",parseInt(d3.select(this).select(".reaction").attr("ry"))+5)
															.attr("transform", "translate(-" + parseInt(parseInt(d3.select(this).select(".reaction").attr("width"))+10) / 2 + ",-"
																					+ parseInt(parseInt(d3.select(this).select(".reaction").attr("height"))+10) / 2
																					+ ")")
															.style("opacity", '0.5')
															.style("fill", 'red');
														session.addSelectedNode(d.getId());

														return true;
													}
													else
													{
														return false;
													}
												}
												else
												{
													if(d.getBiologicalType() == 'metabolite')
													{
														var id = d3.select(this).select(".metabolite").attr("identifier");
														
														if(d.getMappingDataByNameAndCond(mapping.getName(), condition) != null){
															var metaboliteStyle = metExploreD3.getReactionStyle();
															
															_MyThisGraphNode.addText(d, 'viz', metaboliteStyle);

															d3.select(this)
																.insert("rect", ":first-child")
																.attr("class", "stroke")
																.attr("width", parseInt(d3.select(this).select(".metabolite").attr("width"))+10)
																.attr("height", parseInt(d3.select(this).select(".metabolite").attr("height"))+10)
																.attr("rx", parseInt(d3.select(this).select(".metabolite").attr("rx"))+5)
																.attr("ry",parseInt(d3.select(this).select(".metabolite").attr("ry"))+5)
																.attr("transform", "translate(-" + parseInt(parseInt(d3.select(this).select(".metabolite").attr("width"))+10) / 2 + ",-"
																						+ parseInt(parseInt(d3.select(this).select(".metabolite").attr("height"))+10) / 2
																						+ ")")
																.style("opacity", '0.5')
																.style("fill", 'red');
															session.addSelectedNode(d.getId());
															return true;
														}
														else
														{
															return false;
														}
													}
												}
											}
										}
									)		
							}
						);

						metExploreD3.hideMask(myMask);

						if (func!=undefined) {func()};

						var anim=metExploreD3.GraphNetwork.isAnimated("viz");
						if (anim=='true') {	
							var session = _metExploreViz.getSessionById('viz');
							var force = session.getForce();
							
							if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
									force.resume();
							}
						}	

			   		}, 1
			   	);
			}

		
		}); 
	},

	/***********************************************
	* Mapping flux data
	* This function will look at link that have data
	* maped and will color them in gradient of bleu to white
	* @param {} mappingName : mappingName choosed by the user
	* @param {} conditionName : Condition choosed by the user
	* @param {} func : callback function
	*/
	mapFluxes : function(mappingName, conditionName, colorMax, colorMin, useOpacity, func) {
		var mapping = _metExploreViz.getMappingByName(mappingName);
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
	
								
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
	        setTimeout(
				function() {

					var generalStyle = _metExploreViz.getGeneralStyle();
				  	var vis = d3.select("#viz").select("#D3viz");
				  	var session = _metExploreViz.getSessionById('viz');
		          	var nodes = _metExploreViz.getSessionById('viz').getD3Data().getNodes(); 
		          	var conditions = metExploreD3.getConditionsMapped();
					var maxValue = undefined;
		          	var minValue = undefined;
		          	var mappingName = mapping.getName();
		          	var linkStyle = metExploreD3.getLinkStyle();  
		          	var force = session.getForce();
					
					force.linkDistance(function(link){
						if(link.getSource().getIsSideCompound() || link.getTarget().getIsSideCompound())
							return linkStyle.getSize();
						else
							return linkStyle.getSize()*2;
					});

					vis.selectAll("g.node")
						.filter(function(d){
							if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return false;
							else return true;
						})
						.selectAll("rect.stroke")
						.remove();

		          	conditions.forEach(
						function(condition)
						{
							nodes.forEach(function(node){
							 	var mapNode = node.getMappingDataByNameAndCond(mappingName, condition);
				             	if(mapNode != null)
					             	var mapVal = Math.abs(mapNode.getMapValue());
					            else
					             	var mapVal = 0;
				             		
									if(!isNaN(mapVal))
					            	{
					             	  	if(maxValue==undefined){
					                    	minValue = parseFloat(mapVal);
					                    	maxValue = parseFloat(mapVal);
					                  	}
					                  	else
					                 	{
					                    	if(minValue > parseFloat(mapVal))
					                      		minValue = parseFloat(mapVal);

					                   	 	if(maxValue < parseFloat(mapVal))
					                     	 	maxValue = parseFloat(mapVal);
					                  	}
					                }
				          	});	
						}
					);	

	          		if(colorMin==undefined){
	          			colorMin = metExploreD3.GraphUtils.colorNameToHex(generalStyle.getColorMinMappingContinuous());						
	          			if(colorMin==false)
		        			colorMin=generalStyle.getColorMinMappingContinuous();
	          		}
	          		else
	          		{
	          			generalStyle.setMinColorMappingContinuous(colorMin);
	          		}

		        	if(colorMax==undefined){
		        		colorMax = metExploreD3.GraphUtils.colorNameToHex(generalStyle.getColorMaxMappingContinuous());
	          			if(colorMax==false)
		        			colorMax=generalStyle.getColorMaxMappingContinuous();
		        	}
	          		else
	          		{
	          			generalStyle.setMaxColorMappingContinuous(colorMax);
	          		}
		          	
		          	var vis = d3.select("#viz").select("#D3viz");
		          	          	
					var colorStore = session.getColorMappingsSet();
			  		session.resetColorMapping();
			      				

			    	var colorNode = colorMax;
			    	if(conditions[1]==conditionName)
			    		colorNode = colorMin;

			    	if(useOpacity)
			    	{
			    		var quart = 0.5;
			    		var midl = 0.2;
			    	}
			    	else
			    	{
			    		var quart = 1;
			    		var midl = 1;
			    	}

			    	var opacity = d3.scale.linear()
						.domain([-4, -1, 0, 1, 4])
			    		.range([1, quart, midl, quart, 1]);

			    	var scaleValue = d3.scale.linear()
						.domain([-maxValue, 0, maxValue])
						.range([-7, 0, 7]);

			    	session.addColorMapping(maxValue, colorMax); 
					session.addColorMapping(-maxValue, colorMin);
					 
			     	vis.selectAll("g.node")
			        	.each(
			          		function(d) {
			          			if (d.getMappingDatasLength()!=0)
								{
									if(d.getBiologicalType() == 'reaction')
			            			{
										var map1 = d.getMappingDataByNameAndCond(mappingName, conditions[0]);
										var map2 = d.getMappingDataByNameAndCond(mappingName, conditions[1]);
										var map = map1;
								    	if(conditions[1]==conditionName)
								    		map = map2;

										if(map==null)
											var mapVal = 0;
										else
										{
											if(isNaN(map.getMapValue()))
												var mapVal = 0;
			            					else
												var mapVal = map.getMapValue();

							            }
				                      	var reactionStyle = metExploreD3.getReactionStyle();
										_MyThisGraphNode.addText(d, 'viz', reactionStyle);
										d3.select(this)
											.transition().duration(2000)
											.style("opacity", opacity(scaleValue(parseFloat(mapVal))));
 
										session.addSelectedNode(d.getId());    	
									}
					            }
					        }); 	

		          	metExploreD3.hideMask(myMask);

		          	d3.select("#viz").select("#D3viz").selectAll("path.link")
						.style("fill", function(link){
							var reaction, metabolite;
							if(link.getSource().getBiologicalType()=='reaction'){
								reaction = link.getSource();
								metabolite = link.getTarget();
							}
							else
							{
								metabolite = link.getSource();
								reaction = link.getTarget();
							}

							var map1 = reaction.getMappingDataByNameAndCond(mappingName, conditions[0]);
							var map2 = reaction.getMappingDataByNameAndCond(mappingName, conditions[1]);
							
							vis.selectAll('g#node'+metabolite.getId()+'.node')
								.each(function(node){
									
									var map = map1;
							    	if(conditions[1]==conditionName)
							    		map = map2;

							    	if(map==null)
											var mapVal = 0;
									else
									{
										if(isNaN(map.getMapValue()))
											var mapVal = 0;
		            					else
											var mapVal = map.getMapValue();
		            						
						            }

							    	if(node.flux==undefined)
							    		node.flux = scaleValue(mapVal);
							    	else
							    	{
							    		if(Math.abs(node.flux)<Math.abs(scaleValue(mapVal)))
							    			node.flux = scaleValue(mapVal);
							    	}

								});

							vis.selectAll('g#node'+metabolite.getId()+'.node')
								.style("opacity", function(node){
									if(node.getIsSideCompound())
										return 0.2;
									return opacity(node.flux);
								});	

							if(this.id != "linkRev"){
								
								if(map1==null)
										var mapVal = 0;
								else
								{
									if(isNaN(map1.getMapValue()))
										var mapVal = 0;
	            					else
										var mapVal = map1.getMapValue();
	            						
					            }

		                    	if(scaleValue(mapVal) == 0)
		                    	{
		                    		var links = d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("path:link");

									d3.select(this)
										.style("opacity", 0.5)
										.style("stroke", "black")
										.style("stroke-width", 0.5)
										.style("stroke-dasharray", "2,3")
										.each(function(link){
											var first = links[0][0];
											this.parentNode.insertBefore(this, first);
										});
		                    	}
								else
								{
									d3.select(this).style("opacity", opacity(scaleValue(parseFloat(mapVal))));
								}
								if(metabolite.getIsSideCompound())
										d3.select(this).style("opacity", 0.1);

								return colorMax;
							}
							else
							{
								if(map2==null)
										var mapVal = 0;
								else
								{
									if(isNaN(map2.getMapValue()))
										var mapVal = 0;
	            					else
										var mapVal = map2.getMapValue();
	            						
					            }

		                    	if(scaleValue(mapVal) == 0)
		                    	{
									var links = d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("path:link");

									d3.select(this)
										.style("opacity", 0.5)
										.style("stroke", "black")
										.style("stroke-width", 0.5)
										.style("stroke-dasharray", "2,3") 
										.each(function(link){
											var first = links[0][0];
											this.parentNode.insertBefore(this, first);
										});
								}
								else
								{
									d3.select(this).style("opacity", opacity(scaleValue(parseFloat(mapVal))));
								}
								if(metabolite.getIsSideCompound())
										d3.select(this) .style("opacity", 0.1);

								return colorMin;
							} 
						});

		          	if(minValue!=undefined)
		          		metExploreD3.fireEventArg('selectConditionForm', 'afterContinuousMapping', 'flux');
		          	else
		          		metExploreD3.displayMessage("Warning", 'No mapped node on network.');

		          	if (func!=undefined) {func()};
		        
					var anim=metExploreD3.GraphNetwork.isAnimated("viz");
					if (anim=='true') {	
						var session = _metExploreViz.getSessionById('viz');
						
						if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
								force.start();
						}
					}
					metExploreD3.GraphNetwork.tick('viz');
		   		}, 1
		   	);
		}
	},


	/***********************************************
	* Mapping only one flux data
	* This function will look at link that have data
	* maped and will color them in gradient of bleu to white
	* @param {} mappingName : mappingName choosed by the user
	* @param {} conditionName : Condition choosed by the user
	* @param {} func : callback function
	*/
	mapUniqueFlux : function(mappingName, conditionName, colorMax, useOpacity, func) {
		var mapping = _metExploreViz.getMappingByName(mappingName);
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
	        setTimeout(
				function() {

					var generalStyle = _metExploreViz.getGeneralStyle();
				  	var vis = d3.select("#viz").select("#D3viz");
				  	var session = _metExploreViz.getSessionById('viz');
		          	var nodes = _metExploreViz.getSessionById('viz').getD3Data().getNodes(); 
		          	var conditions = mapping.getConditions();	
					var maxValue = undefined;
		          	var minValue = undefined;
		          	var mappingName = mapping.getName();
		          	var linkStyle = metExploreD3.getLinkStyle();  
		          	var force = session.getForce();
					
					force.linkDistance(function(link){
						if(link.getSource().getIsSideCompound() || link.getTarget().getIsSideCompound())
							return linkStyle.getSize();
						else
							return linkStyle.getSize()*2;
					});

					vis.selectAll("g.node")
						.filter(function(d){
							if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return false;
							else return true;
						})
						.selectAll("rect.stroke")
						.remove();

		          	conditions.forEach(
						function(condition)
						{
							nodes.forEach(function(node){
							 	var mapNode = node.getMappingDataByNameAndCond(mappingName, condition);
				             	if(mapNode != null){

					             	var mapVal = mapNode.getMapValue();
									if(!isNaN(mapVal))
					            	{
					             	  	if(maxValue==undefined){
					                    	minValue = parseFloat(mapVal);
					                    	maxValue = parseFloat(mapVal);
					                  	}
					                  	else
					                 	{
					                    	if(minValue > parseFloat(mapVal))
					                      		minValue = parseFloat(mapVal);

					                   	 	if(maxValue < parseFloat(mapVal))
					                     	 	maxValue = parseFloat(mapVal);
					                  	}
					                }
					            }
				          	});	
						}
					);	
		          	
		          	if(colorMax==undefined)
		        		colorMax=generalStyle.getColorMaxMappingContinuous();
		        	else
		          		generalStyle.setMaxColorMappingContinuous(colorMax);
	          		
		          	var vis = d3.select("#viz").select("#D3viz");
		          	          	
					var colorStore = session.getColorMappingsSet();
			  		session.resetColorMapping();
			      			    	
			    	var colorNode = d3.scale.linear()
						.domain([-4, -1, 1, 4])
			    		.range([colorMax, colorMax, colorMax, colorMax]);


			    	if(useOpacity)
			    	{
			    		var quart = 0.5;
			    		var midl = 0.2;
			    	}
			    	else
			    	{
			    		var quart = 1;
			    		var midl = 1;
			    	}
			    	var opacity = d3.scale.linear()
						.domain([-4, -1, 0, 1, 4])
			    		.range([1, quart, midl, quart, 1]);

			    	var colorMin = d3.scale.linear()
						.domain([-4, -1, 1, 4])
			    		.range([colorMax, colorMax, colorMax, colorMax]);

			    	var scaleValue = d3.scale.linear()
						.domain([minValue, 0, maxValue])
						.range([-7, 0, 7]);

			    	session.addColorMapping(maxValue, colorNode(parseFloat(maxValue)));
					 
			    	vis.selectAll("g.node")
			        	.each(
			          		function(d) {
			          			if (d.getMappingDatasLength()!=0)
								{
									if(d.getBiologicalType() == 'reaction')
			            			{
			            				var condition = metExploreD3.getConditionsMapped()[0];
										var map = d.getMappingDataByNameAndCond(mappingName, condition);

										if(map!=null){
											if(!isNaN(map.getMapValue()))
			            					{
						                      	var reactionStyle = metExploreD3.getReactionStyle();
												_MyThisGraphNode.addText(d, 'viz', reactionStyle);
												d3.select(this)
													.transition().duration(2000)
													.style("opacity", opacity(scaleValue(parseFloat(map.getMapValue()))));

												session.addSelectedNode(d.getId());    	
							                }
										}
									}
					            }
					        }); 	

		          	metExploreD3.hideMask(myMask);

		          	d3.select("#viz").select("#D3viz").selectAll("path.link")
						.style("fill", function(link){
							var reaction, metabolite;
							if(link.getSource().getBiologicalType()=='reaction'){
								reaction = link.getSource();
								metabolite = link.getTarget();
							}
							else
							{
								metabolite = link.getSource();
								reaction = link.getTarget();
							}

			            	var condition = metExploreD3.getConditionsMapped()[0];
							var map = reaction.getMappingDataByNameAndCond(mappingName, condition);

							vis.selectAll('g#node'+metabolite.getId()+'.node')
								.each(function(node){
									
							    	if(map==null)
										var mapVal = 0;

							    	if(node.flux==undefined)
							    		node.flux = scaleValue(mapVal);
							    	else
							    	{
							    		if(Math.abs(node.flux)<Math.abs(scaleValue(mapVal)))
							    			node.flux = scaleValue(mapVal);
							    	}

								});

							vis.selectAll('g#node'+metabolite.getId()+'.node')
								.style("opacity", function(node){
									if(node.getIsSideCompound())
										return 0.2;
									return opacity(node.flux);
								});	

							if(map==null)
								var mapVal = 0;
							else
							{
								if (isNaN(map.getMapValue()))
									var mapVal = 0;
								else
									var mapVal = map.getMapValue();
							}

	                    	if(scaleValue(mapVal) == 0)
	                    	{
	                    		var links = d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("path:link");

								d3.select(this)
									.style("opacity", 0.5)
									.style("stroke", "black")
									.style("stroke-width", 0.5)
									.style("stroke-dasharray", "2,3")
									.each(function(link){
										var first = links[0][0];
										this.parentNode.insertBefore(this, first);
									});
	                    	}
							else
							{
								d3.select(this).style("opacity", opacity(scaleValue(parseFloat(mapVal))));
							}
							if(metabolite.getIsSideCompound())
								d3.select(this).style("opacity", 0.1);

							return colorNode(scaleValue(mapVal));
					
						})
						.filter(function(link){
							return this.id == "linkRev";
						})
						.remove();

		          	if(minValue!=undefined)
		          		metExploreD3.fireEventArg('selectConditionForm', 'afterContinuousMapping', 'flux');
		          	else
		          		metExploreD3.displayMessage("Warning", 'No mapped node on network.');

		          	if (func!=undefined) {func()};
		        
					var anim=metExploreD3.GraphNetwork.isAnimated("viz");
					if (anim=='true') {	
						var session = _metExploreViz.getSessionById('viz');
						
						if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
								force.start();
						}
					}
					metExploreD3.GraphNetwork.tick('viz');
		   		}, 1
		   	);
		}
	},


	/***********************************************
	* Parse flux values to discriminate max and min infinity values 
	* @param {} conditionName : mappingName choosed by the user
	*/
	parseFluxValues : function(mappingName) {
		var mapping = _metExploreViz.getMappingByName(mappingName);
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
	        setTimeout(
				function() {

				  	var session = _metExploreViz.getSessionById('viz');
		          	var nodes = _metExploreViz.getSessionById('viz').getD3Data().getNodes(); 
		          	var conditions = mapping.getConditions();	
					var maxValue = undefined;
		          	var minValue = undefined;
		          	var mappingName = mapping.getName();
		          	var arrayInfinity = [];

			      	conditions.forEach(
						function(condition)
						{
							nodes.forEach(function(node){
							 	var mapNode = node.getMappingDataByNameAndCond(mappingName, condition);
				             	if(mapNode != null)
				             		var mapVal = mapNode.getMapValue();
								else
									var mapVal = 0;
									
								if(!isNaN(mapVal))
				            	{
				            		if(parseFloat(mapVal)!=0 & (999999 - Math.abs(parseFloat(mapVal)))*100/999999<0.001){
				            			arrayInfinity.push(node);
				            		}
				            		else
				            		{	
					             	  	if(maxValue==undefined){
					                    	minValue = parseFloat(mapVal);
					                    	maxValue = parseFloat(mapVal);
					                  	}
					                  	else
					                 	{
					                    	if(minValue > parseFloat(mapVal))
					                      		minValue = parseFloat(mapVal);

					                   	 	if(maxValue < parseFloat(mapVal))
					                     	 	maxValue = parseFloat(mapVal);
					                  	}
				            		}
				                }
				            
				          	});	
						}
					);

					if(arrayInfinity.length>0){
						maxValue = maxValue+maxValue/2;
				        var colors = _metExploreViz.getSessionById('viz').getColorMappingsSet();
						arrayInfinity.forEach(function(node){
							conditions.forEach(
								function(condition)
								{
				            		if((999999 - Math.abs(parseFloat(node.getMappingDataByNameAndCond(mappingName, condition).getMapValue())))*100/999999<0.001){
										colors.forEach(function(color){
											if(color.getName() == parseFloat(node.getMappingDataByNameAndCond(mappingName, condition).getMapValue())) color.setName(minValue);
											if(color.getName() == parseFloat(node.getMappingDataByNameAndCond(mappingName, condition).getMapValue())) color.setName(maxValue);
										});
										node.setMappingDataByNameAndCond(mappingName, condition, maxValue);
				            		}
								}
							);
						});
					}	
					metExploreD3.hideMask(myMask);	
		   		}, 1
		   	);
		}
	},


 	graphMappingFlux : function(mappingName, conditionName, fluxType, colorMax, colorMin, isOpac){
		metExploreD3.onloadMapping(mappingName, function(){
			var session = _metExploreViz.getSessionById('viz');
			metExploreD3.GraphMapping.parseFluxValues(mappingName);
			metExploreD3.GraphLink.loadLinksForFlux("viz", session.getD3Data(), metExploreD3.getLinkStyle(), metExploreD3.getMetaboliteStyle());
			
			if(fluxType=='Compare')
				metExploreD3.GraphMapping.mapFluxes(mappingName, conditionName, colorMax, colorMin, isOpac);
			else
				metExploreD3.GraphMapping.mapUniqueFlux(mappingName, conditionName, colorMax, isOpac);

			
		});
 	},

	
	/*****************************************************
	* Reload Mapping
	*/
	reloadMapping : function(mapping) {
		
		var session = _metExploreViz.getSessionById('viz');
		var force = session.getForce();
		force.stop(); 
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
	        setTimeout(
			function() {
				var networkData = session.getD3Data();
				var conditions = mapping.getConditions();
				var node = undefined;
				switch (mapping.getTargetLabel()) {
				    case "reactionDBIdentifier":
				        mapping.getData().forEach(function(map){
				        	if(typeof map.getNode()=="object")
								var node = networkData.getNodeByDbIdentifier(map.getNode().getDbIdentifier());
							else
								var node = networkData.getNodeByDbIdentifier(map.getNode());

							console.log(node);
							if(node!=undefined){
								var mapNode = new MappingData(node, mapping.getName(), map.getConditionName(), map.getMapValue());
								node.addMappingData(mapNode);
							}
						});
				        break;

					case "reactionId":
				        mapping.getData().forEach(function(map){
				        	if(typeof map.getNode()=="object")
								var node = networkData.getNodeById(map.getNode().getId());
							else
								var node = networkData.getNodeById(map.getNode());

							if(node!=undefined){
								var mapNode = new MappingData(node, mapping.getName(), map.getConditionName(), map.getMapValue());
								node.addMappingData(mapNode);
							}
						});
				        break;

					case "metaboliteId":
				        mapping.getData().forEach(function(map){
				        	if(typeof map.getNode()=="object")
								var node = networkData.getNodeById(map.getNode().getId());
							else
								var node = networkData.getNodeById(map.getNode());

							if(node!=undefined){
								var mapNode = new MappingData(node, mapping.getName(), map.getConditionName(), map.getMapValue());
								node.addMappingData(mapNode);
							}
						});
				        break;

				    case "metaboliteDBIdentifier":
				       	mapping.getData().forEach(function(map){
							if(typeof map.getNode()=="object")
								var node = networkData.getNodeByDbIdentifier(map.getNode().getDbIdentifier());
							else
								var node = networkData.getNodeByDbIdentifier(map.getNode());
							
							if(node!=undefined){
								var mapNode = new MappingData(node, mapping.getName(), map.getConditionName(), map.getMapValue());
								node.addMappingData(mapNode);
							}
						});
				        break;
				    case "inchi":
				        // Blah
				        break;
				    default:
        				metExploreD3.displayMessage("Warning", 'The type of node "' + mapping.getTargetLabel() + '" isn\'t know.')	
        		}
				
				metExploreD3.hideMask(myMask);

				var anim=metExploreD3.GraphNetwork.isAnimated("viz");
				if (anim=='true') {
					var force = session.getForce();
					
					if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
						force.resume();
					}
				}
			}, 1);
		}
	},
	/***********************************************
	* Mapping to discrete data
	* This function will look at metabolites that have data
	* maped and will color them in a calculated color
	* @param {} conditionName : Condition choosed by the user
	*/
	graphMappingDiscreteData : function(mappingName, conditionName, func) {
		metExploreD3.onloadMapping(mappingName, function(){

			var mapping = _metExploreViz.getMappingByName(mappingName);
			var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
			if(myMask!= undefined){

				metExploreD3.showMask(myMask);
		        setTimeout(
					function() {
						
						var session = _metExploreViz.getSessionById('viz');
						var force = session.getForce();
						force.stop(); 
						var conditions = mapping.getConditions();	
						var nodes = session.getD3Data().getNodes(); 
					  	
						var values = [];
						
						var vis = d3.select("#viz").select("#D3viz");
						vis.selectAll("g.node")
							.filter(function(d){
								if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return false;
								else return true;
							})
							.selectAll("rect.stroke")
							.remove();	

						// var idMapping = metExploreD3.getMappingSelection();
						// var mappingInfoStore = metExploreD3.getMappingInfosSet();

						// var theMapping = metExploreD3.findMappingInfo(mappingInfoStore, 'id', idMapping);
					
						// var ids = theMapping.get('idMapped');
						// var idsTab = ids.split(",");
						// var i;

						conditions.forEach(
							function(condition)
							{
								nodes.forEach(function(node){
									var mapNode = node.getMappingDataByNameAndCond(mapping.getName(), condition);
									if(mapNode != null){
										var exist = false;
										var mapVal = mapNode.getMapValue().valueOf();
										
										values.forEach(function(val){
											if(val.valueOf()==mapVal.valueOf())
												exist = true;
										})
										if(!exist)
											values.push(mapVal);
									}

								});
								// 	var metabolite = metExploreD3.getMetaboliteById(metabolite_Store, idsTab[i]);
								// 	if(metabolite!=undefined)
								// 		if (metabolite.get('mapped') != undefined)
								// 			if (metabolite.get('mapped') != 0)
								// 				if(metabolite.get(condition.getCondInMetabolite())!=undefined){
													
								// 				}
								// }		
							}
						);	

						function compareInteger(a,b) {
							if (parseFloat(a) < parseFloat(b))
								return -1;
							if (parseFloat(a) > parseFloat(b))
								return 1;
							return 0;
						}

						function compareString(a,b) {
							if (a < b)
								return -1;
							if (a > b)
								return 1;
							return 0;
						}

						var floats = [];
						var strings = [];
						
						values.forEach(function(value){
							if(isNaN(value))
								strings.push(value);
							else
								floats.push(value);
						});

						floats.sort(compareInteger);
						strings.sort(compareString);

						values = floats.concat(strings);
				        
				        if (values.length == undefined) values.length = 0;
				        center = 128;
				        width = 127;
				        frequency = Math.PI*2*0.95/values.length;
				        var position = top;
						var colorStore = session.getColorMappingsSet();
				        
				        session.resetColorMapping();
						for (var i = 0; i < values.length; i++)
				        {
				        	var red   = Math.sin(frequency*i+2+values.length) * width + center;
							var green = Math.sin(frequency*i+0+values.length) * width + center;
							var blue  = Math.sin(frequency*i+4+values.length) * width + center;

							color = metExploreD3.GraphUtils.RGB2Color(red,green,blue);

							session.addColorMapping(values[i], color);
			        		metExploreD3.GraphMapping.fixMappingColorOnNodeData(color, values[i], conditionName, mapping.getName());
						}

						metExploreD3.hideMask(myMask);

						if (func!=undefined) {func()};

						if(values.length!=0)
							metExploreD3.fireEventArg('selectConditionForm', 'afterDiscreteMapping', 'discrete');
			          	else
			          		metExploreD3.displayMessage("Warning", 'No mapped node on network.');

						var anim=metExploreD3.GraphNetwork.isAnimated("viz");
						if (anim=='true') {	
							var session = _metExploreViz.getSessionById('viz');
							var force = session.getForce();
							
							if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
									force.resume();
							}
						}
			   		}, 1
			   	);
			}
		});
	},

	/***********************************************
	* Fill node with corresponding color
	* @param {} color : Color to fill the node
	* @param {} value : Value corresponding to the color
	* @param {} conditionName : Condition choosed by the user
	*/
	fixMappingColorOnNodeData : function(color, value, conditionName, mappingName){
		var vis = d3.select("#viz").select("#D3viz");
		var session = _metExploreViz.getSessionById('viz');
		var contextColor = color;
		
		vis.selectAll("g.node")
			.filter(
				function(d) {
					if(d.getBiologicalType() == 'reaction')
					{
						if (d.getMappingDatasLength()==0)
							return false;
						else
						{
							var map = d.getMappingDataByNameAndCond(mappingName, conditionName);
							if(map!=null){
								
								if(map.getMapValue()==value){
									
									var reactionStyle = metExploreD3.getReactionStyle();
									_MyThisGraphNode.addText(d, 'viz', reactionStyle);
									session.addSelectedNode(d.getId());
									return true;
								}
								else
								{
									return false;
								}
							}
							else
							{
								return false;
							}
						}	
					}
					else
					{
						if(d.getBiologicalType() == 'metabolite')
						{
							if (d.getMappingDatasLength()==0)
								return false;
							else
							{
								var map = d.getMappingDataByNameAndCond(mappingName, conditionName);
								if(map!=null){
									if(map.getMapValue()==value){
									
										var metaboliteStyle = metExploreD3.getMetaboliteStyle();
										_MyThisGraphNode.addText(d, 'viz', metaboliteStyle);
										session.addSelectedNode(d.getId());
										return true;
									}
									else
									{
										return false;
									}
								}
								else
								{
									return false;
								}
								
							}	
						}
					}

				}
			)
			.transition().duration(3000)
			.attr("mapped", color)
			.style("fill", color)
			.each(function(node){
				if(node.getBiologicalType()=="reaction"){
					var colorText = metExploreD3.GraphUtils.chooseTextColor(contextColor);
					d3.select(this).select('text').style("fill", colorText);
				}
			});	
	},

	/***********************************************
	* Mapping to continuous data
	* This function will look at metabolites that have data
	* maped and will color them in gradient of bleu to yellow
	* @param {} conditionName : Condition choosed by the user
	*/
	graphMappingContinuousData : function(mappingName, conditionName, colorMin, colorMax, func) {
		metExploreD3.onloadMapping(mappingName, function(){
			var mapping = _metExploreViz.getMappingByName(mappingName);
			var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
			if(myMask!= undefined){

				metExploreD3.showMask(myMask);
		        setTimeout(
					function() {

						var generalStyle = _metExploreViz.getGeneralStyle();
					  	var vis = d3.select("#viz").select("#D3viz");
					  	var session = _metExploreViz.getSessionById('viz');
			          	var nodes = _metExploreViz.getSessionById('viz').getD3Data().getNodes(); 
			          	var conditions = mapping.getConditions();	
						var maxValue = undefined;
			          	var minValue = undefined;
			          	var mappingName = mapping.getName();
			          	var stringJSON="{\"mapping\":[";	
						var metaboliteStyle = metExploreD3.getMetaboliteStyle();
						var reactionStyle = metExploreD3.getReactionStyle();
																				
						vis.selectAll("g.node")
							.filter(function(d){
								if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return false;
								else return true;
							})
							.selectAll("rect.stroke")
							.remove();

			          	conditions.forEach(
							function(condition)
							{
								stringJSON+="\n{\""+condition+"\":[";
								nodes.forEach(function(node){
								 	var mapNode = node.getMappingDataByNameAndCond(mappingName, condition);
					             	if(mapNode != null){
										stringJSON+="\n{";

						             	var mapVal = mapNode.getMapValue();
						             	stringJSON+="\"node\" : \"" +node.getName();
						             	stringJSON+="\", \"value\" : \""+mapVal;
										if(!isNaN(mapVal))
						            	{
						             	  	if(maxValue==undefined){
						                    	minValue = parseFloat(mapVal);
						                    	maxValue = parseFloat(mapVal);
						                  	}
						                  	else
						                 	{
						                    	if(minValue > parseFloat(mapVal))
						                      		minValue = parseFloat(mapVal);

						                   	 	if(maxValue < parseFloat(mapVal))
						                     	 	maxValue = parseFloat(mapVal);
						                  	}
						                }
						            	stringJSON+='\"},\n';  
						            }
					          	});	
								stringJSON+=']}\n';	
							}
						);	
						stringJSON+=']}\n';	
			          		
			        	if(colorMin==undefined)
			        		colorMin=generalStyle.getColorMinMappingContinuous();
			        	else
		          			generalStyle.setMinColorMappingContinuous(colorMin);
	          		
			        	if(colorMax==undefined)
			        		colorMax=generalStyle.getColorMaxMappingContinuous();
		          		else
		          			generalStyle.setMaxColorMappingContinuous(colorMax);
	          		
			          	var vis = d3.select("#viz").select("#D3viz");

						var colorStore = session.getColorMappingsSet();
				      	session.resetColorMapping();
				      	
				      	var colorScale = d3.scale.linear()
						    .domain([parseFloat(minValue), parseFloat(maxValue)])
						    .range([colorMin, colorMax]);

				     	// var color = metExploreD3.GraphUtils.RGB2Color(0,0,255);
				      
				      	// session.addColorMapping("max", color); 

				      	// color = metExploreD3.GraphUtils.RGB2Color(255,255,0);

				      	// session.addColorMapping("min", color); 
				    	
				    	if(minValue==maxValue){
				    		session.addColorMapping(maxValue, colorScale(parseFloat(maxValue))); 
						}
				    	else
				    	{
				    		session.addColorMapping(maxValue, colorScale(parseFloat(maxValue))); 
							session.addColorMapping(minValue, colorScale(parseFloat(minValue))); 
				    	}
				    
				     	vis.selectAll("g.node")
				        	.each(
				          		function(d) {
				          			if (d.getMappingDatasLength()!=0)
									{
										if(d.getBiologicalType() == 'reaction')
				            			{
											var map = d.getMappingDataByNameAndCond(mappingName, conditionName);
											if(map!=null){
												if(!isNaN(map.getMapValue()))
				            					{
							                     	_MyThisGraphNode.addText(d, 'viz', reactionStyle);
													
													d3.select(this)
														.transition().duration(2000)
														.attr("mapped", colorScale(parseFloat(parseFloat(map.getMapValue()))))
														.style("fill", colorScale(parseFloat(map.getMapValue())));


													// var colorNorm = (parseFloat(map.getMapValue()-minValue)*255.0)/(maxValue-minValue);

							      //                   d3.select(this)
							      //                     .transition().duration(2000)
							      //                     .attr("mapped", "rgb("+ parseFloat(255.0-colorNorm) +","+ parseFloat(255.0-colorNorm) +","+colorNorm+")")
							      //                     .style("fill", "rgb("+ parseFloat(255.0-colorNorm) +","+ parseFloat(255.0-colorNorm) +","+colorNorm+")");

							                        var color = metExploreD3.GraphUtils.chooseTextColor(colorScale(parseFloat(map.getMapValue())));
													d3.select(this).select('text').style("fill", color);  
													session.addSelectedNode(d.getId());    	
								                }
											}
										}
						                else
						                {
						                  var map = d.getMappingDataByNameAndCond(mappingName, conditionName);
											if(map!=null){
												if(!isNaN(map.getMapValue()))
				            					{
								                      	var metaboliteStyle = metExploreD3.getMetaboliteStyle();
														_MyThisGraphNode.addText(d, 'viz', metaboliteStyle);

														d3.select(this)
															.transition().duration(2000)
															.attr("mapped", colorScale(parseFloat(parseFloat(map.getMapValue()))))
															.style("fill", colorScale(parseFloat(map.getMapValue())));
														session.addSelectedNode(d.getId());
								        //                 var colorNorm = (parseFloat(map.getMapValue()-minValue)*255.0)/(maxValue-minValue);

								        //                 d3.select(this)
								        //                   .transition().duration(2000)
														  // .attr("mapped","rgb("+ parseFloat(255.0-colorNorm) +","+ parseFloat(255.0-colorNorm) +","+colorNorm+")")
								        //                   .style("fill", "rgb("+ parseFloat(255.0-colorNorm) +","+ parseFloat(255.0-colorNorm) +","+colorNorm+")");
								                    
								                }
											}
						                }
						            }
						        }); 	

			          	metExploreD3.hideMask(myMask);


			          	if(minValue!=undefined)
			          		metExploreD3.fireEventArg('selectConditionForm', 'afterContinuousMapping', 'continuous');
			          	else
			          		metExploreD3.displayMessage("Warning", 'No mapped node on network.');

			          	if (func!=undefined) {func()};
			        
						var anim=metExploreD3.GraphNetwork.isAnimated("viz");
						if (anim=='true') {	
							var session = _metExploreViz.getSessionById('viz');
							var force = session.getForce();
							
							if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
									force.resume();
							}
						}



						


				        // donnees.forEach(function(aData){
				        //     aData.color=scale(aData.z);
				        // });

// 				        d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
// 							.each(function(node){
// 								if (node.getMappingDatasLength()!=0)
// 								{
// 									var maps = node.getMappingDatas();
// 									var dataCond1 = -Math.abs(parseInt(maps[0].getMapValue()));
// 									var dataCond2 = Math.abs(parseInt(maps[1].getMapValue()));

// 							        var conditions2=
// 							        [
// 							            {
// 							                name: maps[0].getConditionName(),
// 							                data: 500
// 							            }, {
// 							                name: maps[1].getConditionName(),
// 							                data: 500
// 							            }
// 							        ];
// var categories2 = [
//             'Alanine and aspartate metabolism',
//             'Alkaloid synthesis'
// ];
//         var conditions2=
//         [
//             {
//                 name: '3j',
//                 data: [-5, -54]
//             }, {
//                 name: '30j',
//                 data: [75, 20]
//             }
//         ];
//         var dataChart2 = {categories:categories2, conditions:conditions2};
//          // var element3 = new MetXCompareBar(dataChart2, 1300, 1000, "xaxis", "yaxis", "title");
// 					        		var minDim=1000;
// 	        						// var dataChart2 = {categories:[node.getName()], conditions:conditions2};
// 	        						var chartSvg = d3.select(this).append("svg")
// 										.attr("viewBox",function(d) {return "0 0 "+minDim+" "+minDim;})
// 										.attr("width", minDim *8/10 + "px")
// 										.attr("height", minDim *8/10+ "px")
// 										// .attr("x", (-minDim/2)+(minDim*1/10))
// 										// .attr("y", (-minDim/2)+(minDim*1/10))
// 					        		var compareChart = new MetXCompareBar(dataChart2, 1000, 200, "xaxis", "yaxis", maps[0].getMappingName() +" analysis");
					        		
// 										chartSvg.html(d3.select(compareChart).select('svg').node().outerHTML)
										
// 										// .attr("width", "100%").attr("height", "100%");
// 								}
// 							});
						// var array = [];
						// d3.select(compareChart).select('svg').selectAll('.highcharts-series').selectAll('rect').each(function(){array.push(this.height.animVal.value)});
						
						// console.log(array);
						// var scale = d3.scale.linear()
				  //           .domain([Math.min.apply(null, array),Math.max.apply(null, array)])
				  //           .range([sessions["viz"].getColorMappingsSet()[1].getValue(),sessions["viz"].getColorMappingsSet()[0].getValue()]);
						
						// d3.select(compareChart).selectAll('svg').selectAll('.highcharts-series').selectAll('rect').attr('fill', function(){return scale(this.height.animVal.value)})
						

			   		}, 1
			   	);
			}

		});
	},



	/*******************************************************************************************************
	*
	* Mapping for MetExplore
	*
	*/
	
	/***********************************************
	* Mapping to binary data 0 1
	* This function will look at metabolites that have data
	* maped and will color them in blue
	* !!!!! Have to be modified in order to do some batch
	* rendering
	* @param {} conditionName : Condition choosed by the user
	*/
	graphMappingBinary : function(conditionName) {
		var networkVizSessionStore = metExploreD3.getSessionsSet();
		var session = metExploreD3.getSessionById(networkVizSessionStore, 'viz');
		var force = session.getForce();
		force.stop(); 
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
        setTimeout(
				function() {
					metExploreD3.GraphMapping.fixMappingColorOnNode("#056da1", 1, conditionName);
					
					metExploreD3.hideMask(myMask);
					var anim=metExploreD3.GraphNetwork.isAnimated("viz");
					if (anim=='true') {
						var networkVizSessionStore = metExploreD3.getSessionsSet();	
						var session = metExploreD3.getSessionById(networkVizSessionStore, 'viz');
						var force = session.getForce();
						
						if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
								force.resume();
						}
					}
		   		}, 1
	   		);
		}		
	},

	/***********************************************
	* Fill node with corresponding color
	* @param {} color : Color to fill the node
	* @param {} value : Value corresponding to the color
	* @param {} conditionName : Condition choosed by the user
	*/
	fixMappingColorOnNode : function(color, value, conditionName){
		var vis = d3.select("#viz").select("#D3viz");
		var metabolite_Store = metExploreD3.getMetabolitesSet();
		var reaction_Store = metExploreD3.getReactionsSet();

		vis.selectAll("g.node")
			.filter(
				function(d) {
					if(d.getBiologicalType() == 'reaction')
					{
						if (metExploreD3.getReactionById(reaction_Store, d.getId()).get(
								'mapped') == undefined)
							return false;
						else
						{
							if((metExploreD3.getReactionById(reaction_Store, d.getId()).get('mapped') != 0)
									&& metExploreD3.getReactionById(reaction_Store, d.getId()).get(conditionName)==value){
								var sessionsStore = metExploreD3.getSessionsSet();
								var reactionStyle = metExploreD3.getReactionStyle();
								_MyThisGraphNode.addText(d, 'viz', reactionStyle, sessionsStore);
								return true;
							}
							else
							{
								return false;
							}
						}	
					}
					else
					{
						if(d.getBiologicalType() == 'metabolite'&& !d.isSideCompound())
					{
						if(metExploreD3.getMetaboliteById(metabolite_Store, d.getId())==null)
							return false;
						if (metExploreD3.getMetaboliteById(metabolite_Store, d.getId()).get(
								'mapped') == undefined)
							return false;
						else
						{
							if((metExploreD3.getMetaboliteById(metabolite_Store, d.getId()).get('mapped') != 0)
									&& metExploreD3.getMetaboliteById(metabolite_Store, d.getId()).get(conditionName)==value){

								var sessionsStore = metExploreD3.getSessionsSet();
								var metaboliteStyle = metExploreD3.getMetaboliteStyle();
								_MyThisGraphNode.addText(d, 'viz', metaboliteStyle, sessionsStore);
								return true;
							}
							else
							{
								return false;
							}
						}	
					}
					}

				}
			)
			.transition().duration(4000)
			.attr("mapped",color)
			.style("fill", color)	
	},

	/***********************************************
	* Change color for a value
	* @param {} color : New color
	* @param {} value : Value corresponding to the color
	* @param {} conditionName : Condition choosed by the user
	*/
	setDiscreteMappingColor : function(color, value, conditionName, selectedMapping){
		
		var session = _metExploreViz.getSessionById('viz');
		var force = session.getForce();
		force.stop(); 
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
	        setTimeout(
				function() {
					
					var vis = d3.select("#viz").select("#D3viz");
					
					var colorStore = session.getColorMappingsSet();
					
					var theColor = session.getColorMappingById(value);	
					theColor.setValue(color);
					
					metExploreD3.GraphMapping.fixMappingColorOnNodeData(color, value, conditionName, selectedMapping);
				
					metExploreD3.hideMask(myMask);
					
		   		}, 1
		   	);
		}
	},

	/***********************************************
	* Change color for a value
	* @param {} color : New color
	* @param {} value : Value corresponding to the color
	* @param {} conditionName : Condition choosed by the user
	*/
	setContinuousMappingColor : function(color, value, conditionName, selectedMapping){
		
		var session = _metExploreViz.getSessionById('viz');
		var force = session.getForce();
		force.stop(); 
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
					
			var vis = d3.select("#viz").select("#D3viz");
			
			var colorStore = session.getColorMappingsSet();
			
			var theColor = session.getColorMappingById(value);	
			theColor.setValue(color);
			
			metExploreD3.hideMask(myMask);
		}
	},

	/***********************************************
	* Remove the mapping graphically
	* @param {} conditionName : Condition choosed by the user
	*/
	removeGraphMapping : function(conditionName) {
		var session = _metExploreViz.getSessionById('viz');
		var vis = d3.select("#viz").select("#D3viz");
		var metabolite_Store = metExploreD3.getMetabolitesSet();
		var reaction_Store = metExploreD3.getReactionsSet();

		vis.selectAll("g.node")
			.filter(
				function(d) {
					if(d.getBiologicalType() == 'reaction'){
						if (metExploreD3.getReactionById(reaction_Store, d.getId()).get(
								'mapped') == undefined)
							return false;
						else
							return metExploreD3.getReactionById(reaction_Store, d.getId()).get('mapped') != 0
					}
					else
					{
						if(d.getBiologicalType() == 'metabolite'){
							if (metExploreD3.getMetaboliteById(metabolite_Store, d.getId()).get(
									'mapped') == undefined)
								return false;
							else
								return metExploreD3.getMetaboliteById(metabolite_Store, d.getId()).get('mapped') != 0
						}
					}
				}
			)
			.transition().duration(1000)
			.attr("transform", function(d){
				return "translate("+d.x+", "+d.y+") scale(1)";
			})
			.style("fill", "white");
		
		vis.selectAll("g.node")
			.filter(function(d){
				if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return false;
				else return true;
			})
			.attr("mapped", "false")
			.selectAll("rect.stroke")
			.remove();					
	},
	

	/***********************************************
	* Remove the mapping graphically
	* @param {} conditionName : Condition choosed by the user
	*/
	removeGraphMappingData : function(conditionName) {
		var session = _metExploreViz.getSessionById('viz');
		var vis = d3.select("#viz").select("#D3viz");

		vis.selectAll("g.node")
			.transition().duration(1000)
			.attr("transform", function(d){
				return "translate("+d.x+", "+d.y+") scale(1)";
			})
			.style("fill", "white")
			.style("opacity",1)
			.each(function(node){
				if(node.getBiologicalType()=="reaction"){
					if(node.isSelected())
						d3.select(this).select('text').transition().duration(4000).style("fill", "white");
					else
						d3.select(this).select('text').transition().duration(4000).style("fill", "black");
				}
			});	

		vis.selectAll("g.node")
			.filter(function(d){
				if(this.getAttribute("mapped")==undefined || this.getAttribute("mapped")==false || this.getAttribute("mapped")=="false") return false;
				else return true;
			})
			.attr("mapped", "false")
			.selectAll("rect.stroke")
			.remove();

		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var linkStyle = metExploreD3.getLinkStyle();
		metExploreD3.GraphLink.refreshLink('viz', session, linkStyle, metaboliteStyle);					
	},

	launchAfterMappingFunction:function(mappingTitle, func) {
        var mapping = _metExploreViz.getMappingByName(mappingTitle); 
        if (mapping !== null) {
           // the variable is defined
           func(mapping);
           return;
        }
        var that = this;
        setTimeout(function(){that.launchAfterMappingFunction(mappingTitle, func);}, 100);    
    },

    onloadMapping : function(mapping, func){
        this.launchAfterMappingFunction(mapping, func);
    },
    /***********************************************
    * Remove the mapping in MetExploreViz
    * @param {} conditionName : Condition choosed by the user
    */
    removeMappingData : function(mappingObj) {
        this.onloadMapping(mappingObj.get('title'), function(mapping){
	        metExploreD3.fireEventArg('selectConditionForm', "removeMapping", mapping);
	        	// metExploreD3.fireEventArg('selectConditionForm', "closeMapping", null);
	        	

	        
    	});
     /*   var array = [];
        _metExploreViz.getMappingsSet().forEach(function(map){
            if (map.getName().search(mapping.get('title'))!=-1) {
               array.push(); 
            };
        });*/

    },

	loadDataFromJSON : function(json) {
		var mappingJSON = metExploreD3.GraphUtils.decodeJSON(json);
		if(mappingJSON){
			var session = _metExploreViz.getSessionById('viz');
			var force = session.getForce();
			force.stop(); 
			var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
			if(myMask!= undefined){

				metExploreD3.showMask(myMask);
		        setTimeout(
				function() {	
					var conds =[];
					mappingJSON.mappings.forEach(function(condition){
			        	conds.push(condition.name);
			        });
		   			
		   			var mapping = new Mapping(mappingJSON.name, conds, mappingJSON.targetLabel);
					
					_metExploreViz.addMapping(mapping);

	        		metExploreD3.GraphMapping.generateMapping(mapping, mappingJSON.mappings);
					
					metExploreD3.hideMask(myMask);


			        metExploreD3.fireEventArg('selectMappingVisu', "jsonmapping", mapping);
					var anim=metExploreD3.GraphNetwork.isAnimated("viz");
					if (anim=='true') {
						var force = session.getForce();
						
						if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
							force.resume();
						}
					}
				}, 1);
			}
		}
	},

	/*****************************************************
    * Update the network to fit the cart content
    */
    loadDataTSV : function(url, func) {
    	var session = _metExploreViz.getSessionById('viz');
		var force = session.getForce();
		force.stop(); 
		var myMask = metExploreD3.createLoadMask("Mapping in progress...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
	        d3.tsv(url, function(data) {
	            
	            var urlSplit = url.split('/');
	            var title = url.split('/')[urlSplit.length-1];

	            var targetName = Object.keys(data[0])[0];

	            var indexOfTarget = Object.keys(data[0]).indexOf(targetName);
	            var arrayAttr = Object.keys(data[0]);
	            if (indexOfTarget > -1) {
	                arrayAttr.splice(indexOfTarget, 1);
	            }

	            var array = [];
	            var mapping = new Mapping(title, arrayAttr, targetName, array);
	            _metExploreViz.addMapping(mapping);  
	            
	            metExploreD3.GraphMapping.mapNodeDataFile(mapping, data);

	            metExploreD3.fireEventArg('selectMappingVisu', "jsonmapping", mapping);
	            metExploreD3.hideMask(myMask);
	            if (func!=undefined) {func()};
	            var anim=metExploreD3.GraphNetwork.isAnimated("viz");
				if (anim=='true') {
					var force = session.getForce();
					
					if ((d3.select("#viz").select("#D3viz").attr("animation") == 'true') || (d3.select("#viz").select("#D3viz") .attr("animation") == null)) {
						force.resume();
					}
				}   
	        });
		}
    },
    
	generateMapping: function(mapping, nodeMappingByCondition){
		var session = _metExploreViz.getSessionById('viz');
		var networkData = session.getD3Data();
		switch (mapping.getTargetLabel()) {
            case "reactionDBIdentifier":
            	if(!(nodeMappingByCondition.length==1 && nodeMappingByCondition[0].name=="undefined"))
                {
                	nodeMappingByCondition.forEach(function(condition){
    					condition.data.forEach(function(map){
							var mapData = new MappingData(map.node, mapping.getName(), condition.name, map.value);
							mapping.addMap(mapData);
    						var node = networkData.getNodeByDbIdentifier(map.node);
    						if(node!=undefined){
    							var mapNode = new MappingData(node, mapping.getName(), condition.name, map.value);
    							node.addMappingData(mapNode);
    						}
    	        		});	
                 	 });
                }
                else
                {
                	nodeMappingByCondition[0].data.forEach(function(map){
						var mapData = new MappingData(map.node, mapping.getName(), nodeMappingByCondition[0].name, map.value);
						mapping.addMap(mapData);
						var node = networkData.getNodeByDbIdentifier(map.node);
						if(node!=undefined){
							var mapNode = new MappingData(node, mapping.getName(), nodeMappingByCondition[0].name, map.value);
							node.addMappingData(mapNode);
						}
	        		});	
                }
                break;
            case "metaboliteDBIdentifier":
                nodeMappingByCondition.forEach(function(condition){
					condition.data.forEach(function(map){   
						var mapData = new MappingData(map.node, mapping.getName(), condition.name, map.value);
						mapping.addMap(mapData); 
						var node = networkData.getNodeByDbIdentifier(map.node);
						if(node!=undefined){
							var mapNode = new MappingData(node, mapping.getName(), condition.name, map.value);
							node.addMappingData(mapNode);
						}
	        		});	
             	 });
                break;
            case "reactionId":
            	if(!(nodeMappingByCondition.length==1 && nodeMappingByCondition[0].name=="undefined"))
                {
                	nodeMappingByCondition.forEach(function(condition){
    					condition.data.forEach(function(map){
							var mapData = new MappingData(map.node, mapping.getName(), condition.name, map.value);
							mapping.addMap(mapData);
    						var node = networkData.getNodeById(map.node);
    						if(node!=undefined){
    							var mapNode = new MappingData(node, mapping.getName(), condition.name, map.value);
    							node.addMappingData(mapNode);
    						}
    	        		});	
                 	 });
                }
                else
                {
                	nodeMappingByCondition[0].data.forEach(function(map){
						var mapData = new MappingData(map.node, mapping.getName(), nodeMappingByCondition[0].name, map.value);
						mapping.addMap(mapData);
						var node = networkData.getNodeById(map.node);
						if(node!=undefined){
							var mapNode = new MappingData(node, mapping.getName(), nodeMappingByCondition[0].name, map.value);
							node.addMappingData(mapNode);
						}
	        		});	
                }
                break;
            case "metaboliteId":
                nodeMappingByCondition.forEach(function(condition){
					condition.data.forEach(function(map){ 
						var mapData = new MappingData(map.node, mapping.getName(), condition.name, map.value);
						mapping.addMap(mapData); 
						var node = networkData.getNodeById(map.node);
						if(node!=undefined){
							var mapNode = new MappingData(node, mapping.getName(), condition.name, map.value);
							if(map.inchi!= undefined)
								node.mappedInchi = map.inchi;

							node.addMappingData(mapNode);
						}
	        		});	
             	});
                break;
            case "inchi":
                // Blah
                break;
            default:
                metExploreD3.displayMessage("Warning", 'The type of node "' + mapping.getTargetLabel() + '" isn\'t know.')
        }
	}
}