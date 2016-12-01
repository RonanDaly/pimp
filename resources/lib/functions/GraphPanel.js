/**
 * @author MC
 * @description : To manage the panel where is the graph
 */
metExploreD3.GraphPanel = {
	
	/*****************************************************
	* Get panel height
    * @param {} panel : active panel
	*/
	getHeight : function(panel){ 
		return d3.select("#"+panel).select("#D3viz").style("height");
	},
    
    /*****************************************************
	* Get panel width
    * @param {} panel : active panel
	*/
	getWidth : function(panel){ 
		return d3.select("#"+panel).select("#D3viz").style("width");
	},

	/*****************************************************
	* To resize svg viz when layout is modified 
	*/
	resizeViz : function(panel){

		var scale = metExploreD3.getScaleById(panel);
		if(scale!=undefined){

			d3.select("#metexplore").text('');
			d3.select("#"+panel).select("#D3viz").attr('width', $("#"+panel).width()); //max width
	        d3.select("#"+panel).select("#D3viz").attr('height', $("#"+panel).height()); //max height
			
			d3.select("#"+panel)
				.select("#D3viz")
				.select("#foreignObject")	
				.attr("transform", "translate("+($("#"+panel).width()-300)+",100) scale(1)")

			// Redefine Zoom and brush
			var scaleZ = scale.getZoomScale();
			var xScale =
			  d3.scale.linear()
			    .domain([0, $("#"+panel).width()])
			    .range([0, $("#"+panel).width()]);

			var yScale =
			  d3.scale.linear()
			    .domain([$("#"+panel).height(), 0])
			    .range([$("#"+panel).height(), 0]);

			var transform = scale.getZoom().translate();

			scale.getZoom()
				.x(xScale)
				.y(yScale)
				.translate(transform)
				.scale(scaleZ);
			
			// scale.setZoomScale(scaleZ);

			// .x( xScale )
			// .y( yScale )
			// .scaleExtent([ 0.01, 30 ])
			// .on("zoom", function(e){
			// 	var session = metExploreD3.getSessionById(this.parentNode.id);
		   //      		// if visualisation is actived we add item to menu
		   //      		if(session.isActive()){
			// 		that.zoom(this.parentNode.id);
			// 	}
			// });

			// scale
			// 	.getStoreByGraphName(panel)
			// 	.setScale(xScale, yScale, 1, 1, 1, metExploreD3.GraphNetwork.zoomListener.scale(), metExploreD3.GraphNetwork.zoomListener);			
			// var brushing = false;

			d3.select("#"+panel).select('#D3viz').select('#brush')
				.call(d3.svg.brush()
					.x(xScale)
					.y(yScale)
					.on("brushstart", function(d) {
						document.addEventListener("mousedown", function(e) {
							if (e.button === 1) {
								e.stopPropagation();
								e.preventDefault();
								e.stopImmediatePropagation();
							}
						});

						var scrollable = d3.select("#"+panel).select("#buttonHand").attr("scrollable");

						_MyThisGraphNode.activePanel = this.parentNode.parentNode.id;

						var session = _metExploreViz.getSessionById(_MyThisGraphNode.activePanel);
							
						if(d3.event.sourceEvent.button!=1 && scrollable!="true"){

							if(session!=undefined)  
							{
								// We stop the previous animation
								if(session.isLinked()){
									var sessionMain = _metExploreViz.getSessionById('viz');
									if(sessionMain!=undefined)
									{
										var force = sessionMain.getForce();
										if(force!=undefined)  
										{		
											force.stop();
										}	
									}
								}
								else
								{	
									
									var force = session.getForce();
									if(force!=undefined)  
									{
										force.stop();
																
									}
								}
							}
							
							brushing = true;
							d3.select("#"+panel).select("#brush").classed("hide", false);
							d3.select("#"+panel).select("#D3viz").on("mousedown.zoom", null);
							nodeBrushed = d3.select("#"+panel).select("#graphComponent").selectAll("g.node");
							nodeBrushed.each(function(d) { 
									d.previouslySelected = d.isSelected(); 
								}
							);
						}
						else
						{
							var force = session.getForce();
							if(force!=undefined)  
							{
								force.stop();				
							}
							
							d3.select("#"+panel).selectAll("#D3viz").style("cursor", "all-scroll");	
							d3.selectAll("#brush").classed("hide", true);
						}
					})
					.on("brushend", function() {
						if(d3.event.sourceEvent.button!=1 && brushing){
							var extent = d3.event.target.extent();
							if(extent[1][0]-extent[0][0]>20 || extent[1][1]-extent[0][1]>20){	

				                var iSselected;
								var extent = d3.event.target.extent();
								var scale = metExploreD3.getScaleById(panel);
								var zoomScale = scale.getZoomScale();

								var myMask = metExploreD3.createLoadMask("Selection in progress...", panel);
								if(myMask!= undefined){
									
									metExploreD3.showMask(myMask);

							        metExploreD3.deferFunction(function() {
							            nodeBrushed
											.classed("selected", function(d) {
												var xScale=scale.getZoom().x();
												var yScale=scale.getZoom().y();

												iSselected = (xScale(extent[0][0]) <= xScale(d.x) && xScale(d.x) < xScale(extent[1][0]))
							                              && (yScale(extent[0][1]) <= yScale(d.y) && yScale(d.y) < yScale(extent[1][1]));
												if((d.isSelected()==false && iSselected==true)||(d.isSelected()==true && iSselected==false && !d.previouslySelected))
							 					{	
							 						_MyThisGraphNode.selection(d, panel);
							 					}
												return iSselected;
											});
							            metExploreD3.hideMask(myMask);
										var session = _metExploreViz.getSessionById(_MyThisGraphNode.activePanel);
										if(session!=undefined)  
										{
											// We stop the previous animation
											if(session.isLinked()){
												var sessionMain = _metExploreViz.getSessionById('viz');
												if(sessionMain!=undefined)
												{
													var animLinked=metExploreD3.GraphNetwork.isAnimated(sessionMain.getId());
													if (animLinked=='true') {
														var force = sessionMain.getForce();
														if(force!=undefined)  
														{		
															if((metExploreD3.GraphNetwork.isAnimated(sessionMain.getId()) == 'true') 
																|| (metExploreD3.GraphNetwork.isAnimated(sessionMain.getId()) == null)) {
																	force.start();
															}
														}
													}
												}
											}
											else
											{	
												
												var force = session.getForce();
												var animLinked=metExploreD3.GraphNetwork.isAnimated(session.getId())
													if (animLinked=='true') {
														var force = session.getForce();
														if(force!=undefined)  
														{		
															if((metExploreD3.GraphNetwork.isAnimated(session.getId()) == 'true') || (metExploreD3.GraphNetwork.isAnimated(session.getId()) == null)) {
																	force.start();
															}
														}
													}
											}
										}
										brushing = false;
							        }, 100);
								}
							}
						}
						else
						{
							var session = _metExploreViz.getSessionById(_MyThisGraphNode.activePanel);
							if(session!=undefined)  
							{
								// We stop the previous animation
								if(session.isLinked()){
									var sessionMain = _metExploreViz.getSessionById('viz');
									if(sessionMain!=undefined)
									{
										var animLinked=metExploreD3.GraphNetwork.isAnimated(sessionMain.getId())
										if (animLinked=='true') {
											var force = sessionMain.getForce();
											if(force!=undefined)  
											{		
												if((metExploreD3.GraphNetwork.isAnimated(sessionMain.getId()) == 'true') 
													|| (metExploreD3.GraphNetwork.isAnimated(sessionMain.getId()) == null)) {
														force.start();
												}
											}
										}
									}
								}
								else
								{	
									
									var force = session.getForce();
									var animLinked=metExploreD3.GraphNetwork.isAnimated(session.getId())

									if (animLinked=='true') {
										var force = session.getForce();
										if(force!=undefined)  
										{		
											if(d3.select(metExploreD3.GraphNetwork.isAnimated(session.getId()) == 'true') 
												|| (metExploreD3.GraphNetwork.isAnimated(session.getId()) == null)) {
													force.start();
											}
										}
									}
								}
							}
						}
						d3.event.target.clear();
							d3.select(this).call(d3.event.target);
							var scale = metExploreD3.getScaleById(panel);

						d3.select("#"+panel).selectAll("#D3viz")
							.style("cursor", "default");

						d3.select("#"+panel).selectAll("#D3viz")
							.call(scale.getZoom())
							.on("dblclick.zoom", null)
							.on("mousedown", null);
						
						d3.event.target.extent();
						d3.selectAll("#brush").classed("hide", false);
					})
				);

			d3.select("#viz").select("#D3viz")
				.select("#logoViz")
				.select("image")
				.attr('x', $("#viz").width() - 88)
				.attr('y', $("#viz").height() - 70);

			d3.select("#metexplore").text('MetExploreViz').attr('x', $("#viz").width() - 112).attr(
					'y',  $("#viz").height() - 10);	    
		}
	},

	/*****************************************************
	* To resize svg panels when layout is modified 
    * @param {} panel : active panel
	*/
	resizePanels : function(panel){
		var sessionsStore = _metExploreViz.getSessionsSet();
		var session = _metExploreViz.getSessionById(panel);
		var h = $("#"+panel).height();
		var w = $("#"+panel).width();

		d3.select("#"+panel)
			.select("#D3viz")
			.select("foreignObject")
			.attr("x", w-300);
		
		if(d3.select("#"+panel).select("#D3viz").select("#buttonZoomIn")[0][0]!=null
			&& d3.select("#"+panel).select("#D3viz").select("#buttonZoomOut")[0][0]!=null
			&& d3.select("#"+panel).select("#D3viz").select("#buttonHand")[0][0]!=null)
		{	
			var x = d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#buttonZoomIn")
				.attr('x');
			var deltaX = w-60-x;					
			
			d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#buttonZoomIn")
				.attr("transform", "translate("+deltaX+",0) scale(1)");
				
			x = d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#buttonZoomOut")
				.attr('x');
			deltaX = w-110-x;					
			
			d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#buttonZoomOut")
				.attr("transform", "translate("+deltaX+",0) scale(1)");
			x = d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#buttonHand")
				.attr('x');
			deltaX = w-160-x;					
			
		    d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#buttonHand")
				.attr("transform", "translate("+deltaX+",0) scale(1)");

			x = d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#whiteBlack")
				.attr('x');
			deltaX = w-100-x;					
			
		    d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#whiteBlack")
				.attr("transform", "translate("+deltaX+",0) scale(1)");

			x = d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#invertColor")
				.attr('x');
			deltaX = w-100-x;					
			
		    d3
				.select("#"+panel)
				.select("#D3viz")
				.select("#invertColor")
				.attr("transform", "translate("+deltaX+",0) scale(1)");
		}
		if(session!=undefined)  
		{
			if(session.isLinked()){
		
				var sessionMain = _metExploreViz.getSessionById("viz");
				var force = sessionMain.getForce();
				if(force!=undefined){
					var h = $("#viz").height();
					var w = $("#viz").width();
					force.size([ w, h ]);
	                var anim=d3.select("#viz").select("#buttonAnim").attr("animation");
	                if(anim=="true")  
	                    force.resume();
				}
			}
			else
			{
				var force = session.getForce();
				if(force!=undefined){
					var h = $("#"+panel).height();
					var w = $("#"+panel).width();
					force.size([ w, h ]);
	                var anim=d3.select("#"+panel).select("#buttonAnim").attr("animation");
	                if(anim=="true")  
	                    force.resume();
				}
			}
		}
		var sessions = _metExploreViz.getSessionsSet();
		var session = _metExploreViz.getSessionById(panel);
		if(session!=undefined)  
		{
			var anim = metExploreD3.GraphNetwork.isAnimated(panel);;
			if (anim == "true") {
				if(session.isLinked())
				{
					for (var key in sessions) {
						if(sessions[key].isLinked())
							metExploreD3.GraphNetwork.animationButtonOn(sessions[key].getId());
					}
					var force = _metExploreViz.getSessionById("viz").getForce();
					force.resume();
				}
				else
				{
					metExploreD3.GraphNetwork.animationButtonOn(panel);
					var force = session.getForce();
					force.resume();
				}
			} 
		}
	},

	/*****************************************************
	* To remove svg components of panel
    * @param {} panel : active panel
	*/
	removeSvgComponents : function(panel){
		d3.select("#"+panel).select("#D3viz").selectAll("*").remove();
	},

	/*****************************************************
	* Update the network to fit the cart content
	*/
	refreshJSON : function(json) {
		var jsonParsed = metExploreD3.GraphUtils.decodeJSON(json);
		if(jsonParsed){
			if(!_metExploreViz.isLaunched())
				metExploreD3.GraphPanel.initiateViz('D3');
			
			var vizComp = Ext.getCmp("viz");
			if(vizComp!=undefined){
				var myMask = metExploreD3.createLoadMask("Refresh in process...", 'viz');
				if(myMask!= undefined){

					metExploreD3.showMask(myMask);
					
					var that = this;
			        setTimeout(
						function() {
							metExploreD3.fireEvent('selectConditionForm', "resetMapping");
	                	
							// var startall = new Date().getTime();
							// var start = new Date().getTime();
							// console.log("----Viz: START refresh/init Viz");
							
							if(jsonParsed.sessions!=undefined)
								metExploreD3.GraphPanel.loadDataJSON(json, end);
							else
								metExploreD3.GraphPanel.initDataJSON(json, end); // Init of metabolite network

							// 62771 ms for recon before refactoring
							// 41465 ms now
							// var endall = new Date().getTime();
							// var timeall = endall - startall;
							// console.log("----Viz: FINISH refresh/ all "+timeall);
							/*metExploreD3.hideMask(myMask);
							metExploreD3.fireEvent('graphPanel', 'afterrefresh');*/
							function end(){
								metExploreD3.hideMask(myMask);
								metExploreD3.fireEvent('graphPanel', 'afterrefresh');
							}
				    }, 100);
			    }
			}
		}
	},

	/*****************************************************
	* Update the network 
	*/
	refreshPanel : function(json, func) {
		var me = this;
		metExploreD3.hideInitialMask();
		if(metExploreD3.GraphUtils.decodeJSON(json).nodes || metExploreD3.GraphUtils.decodeJSON(json).sessions){
			if(!_metExploreViz.isLaunched() || metExploreD3.getGeneralStyle().windowsAlertIsDisable()){
				
				metExploreD3.GraphPanel.refreshJSON(json);
				if(typeof func==='function') func();
			}
			else
			{
				Ext.Msg.show({
		           title:'Are you sure?',
		           msg: 'This action will remove previous network. <br />Would you like to do this?',
		           buttons: Ext.Msg.OKCANCEL,
		           fn: function(btn){
						if(btn=="ok")
						{	
							metExploreD3.GraphPanel.refreshJSON(json);
							if(func!=undefined && typeof func==='function') func();
						}
		           },
		           icon: Ext.Msg.QUESTION
		       });
			}
		}
		else
		{
			//SYNTAX ERROR
			metExploreD3.displayWarning("Syntaxe error", 'File have bad syntax. Use a saved file from MetExploreViz or see <a href="http://metexplore.toulouse.inra.fr/metexploreViz/doc/documentation.php#generalfunctioning">MetExploreViz documentation</a>.');
		}		
	},

	/*****************************************************
	* Fill the data models with the store reaction
	*/
	loadDataJSON : function(json, endFunc){
		var jsonParsed = metExploreD3.GraphUtils.decodeJSON(json);
		if(jsonParsed){

			if(metExploreD3.bioSourceControled())
			{
				_metExploreViz.setBiosource(jsonParsed.biosource);
				metExploreD3.fireEventParentWebSite("loadNetworkBiosource", {biosource : jsonParsed.biosource, func:loadJSON, endFunc:endFunc, json:json});
			}
			else
			{
				loadJSON();
				endFunc();
			}
			function loadJSON(){
				var networkVizSession = _metExploreViz.getSessionById("viz");
			
				var oldForce = networkVizSession.getForce();
				// Reset visualisation---less than a ms
				if(oldForce!=undefined){
					oldForce.nodes([]);
					oldForce.links([]);

					oldForce.on("start", null);
					oldForce.on("end", null);
					oldForce.on("tick", null);

				}

				networkVizSession.reset();


				if(jsonParsed.comparedPanels)
				{	
					jsonParsed.comparedPanels.forEach(function(comparedPanel){
						_metExploreViz.addComparedPanel(new ComparedPanel(comparedPanel.panel, comparedPanel.visible, comparedPanel.parent, comparedPanel.title));
					});
				}	
					
				if(jsonParsed.mappings)
				{
					jsonParsed.mappings.forEach(function(mapping){
						var mapping = new Mapping(mapping.name, mapping.conditions, mapping.targetLabel);
						_metExploreViz.addMapping(mapping);
					});
				}		

				if(jsonParsed.generalStyle)
				{
					var oldGeneralStyle = metExploreD3.getGeneralStyle();                   
					var style = new GeneralStyle(
						oldGeneralStyle.getWebsiteName(), 
						jsonParsed.generalStyle.colorMinMappingContinuous, 
						jsonParsed.generalStyle.colorMaxMappingContinuous, 
						jsonParsed.generalStyle.maxReactionThreshold, 
						jsonParsed.generalStyle.displayLabelsForOpt, 
						jsonParsed.generalStyle.displayLinksForOpt, 
						jsonParsed.generalStyle.displayConvexhulls, 
						jsonParsed.generalStyle.clustered,  
						jsonParsed.generalStyle.displayCaption, 
						oldGeneralStyle.hasEventForNodeInfo(), 
						oldGeneralStyle.loadButtonIsHidden(), 
						oldGeneralStyle.windowsAlertIsDisable()
					);
					metExploreD3.setGeneralStyle(style);
				}

				var sessions = jsonParsed.sessions;				
				for (var key in sessions) {
					if(key!='viz')
			        {
						var networkVizSession = new NetworkVizSession();
					    networkVizSession.setVizEngine("D3");
					    networkVizSession.setId(key);
					    networkVizSession.setLinked(sessions[key].linked);
					    _metExploreViz.addSession(networkVizSession);	
						

						var accord = Ext.getCmp("comparePanel");
			        	var comparedPanel = _metExploreViz.getComparedPanelById(key);
			        	
						var item = [
			        		{
			        			id:comparedPanel.getParent(),
			        			title:comparedPanel.getTitle(), 
			        			html:"<div id=\""+comparedPanel.getParent()+"\" height=\"100%\" width=\"100%\"></div>", 
			        			flex: 1, 
			        			closable: true, 
			        			collapsible: true, 
			        			collapseDirection: "left" 
			        		}
			        	];
						
						accord.add(item);
						accord.expand();

						metExploreD3.fireEventArg("comparePanel", 'initiateviz', key);
						//metExploreD3.GraphNetwork.refreshSvg(panelId);
					}	


					if(sessions[key].colorMappings)
					{
						sessions[key].colorMappings.forEach(function(colorMapping){
							networkVizSession.addColorMapping(colorMapping.name, colorMapping.value);
						});
					}	

					var anim = sessions[key].animated;

					if(!anim)
						anim = false;

					networkVizSession.setAnimated(anim);

					var networkData = new NetworkData(key);
					networkData.cloneObject(sessions[key].d3Data);

					var nodes = networkData.getNodes();
					nodes.forEach(function(node){
						if(node.getBiologicalType()=="metabolite")
						{
							if(networkData.getCompartmentByName(node.getCompartment())==null)
								networkData.addCompartment(node.getCompartment());
						}
						else
						{
							node.getPathways().forEach(function(pathway){
								if(networkData.getPathwayByName(pathway)==null)
									networkData.addPathway(pathway);
							});
						}

						if(node.getMappingDatasLength()>0)
						{
							node.getMappingDatas().forEach(function(mappingData){
								mappingData.setNode(node);
								if(_metExploreViz.getMappingByName(mappingData.getMappingName())!=null){
									var mapping = _metExploreViz.getMappingByName(mappingData.getMappingName());
									mapping.addMap(mappingData);
								}
							});
						}
					});
					
					networkData.setId(key);

					if(key=='viz') _metExploreViz.setInitialData(_metExploreViz.cloneNetworkData(networkData));
					networkVizSession.setD3Data(networkData);

					if(sessions[key].selectedNodes)
					{
						sessions[key].selectedNodes.forEach(function(nodeId){
							networkVizSession.addSelectedNode(nodeId);
						});
					}			
					

					if(_metExploreViz.getMappingsLength()>0 && key=="viz" && !metExploreD3.getGeneralStyle().windowsAlertIsDisable())
					{
						metExploreD3.displayMessageYesNo("Mapping",'Do you want keep mappings.',function(btn){
			                if(btn=="yes")
			                {   
			                    _metExploreViz.getMappingsSet().forEach(function(mapping){
			                    	metExploreD3.GraphMapping.reloadMapping(mapping);
				                	metExploreD3.fireEventArg('selectMappingVisu', "jsonmapping", mapping);
			                    }); 
				                metExploreD3.fireEventArg('buttonRefresh', "reloadMapping", true);
			                }
			                else
			                {
			                	metExploreD3.fireEventArg('buttonMap', "reloadMapping", false);
				                metExploreD3.fireEventArg('buttonRefresh', "reloadMapping", false);
			                	metExploreD3.fireEventArg('selectConditionForm', "closeMapping", _metExploreViz.getActiveMapping);
				                _metExploreViz.resetMappings();
			                	// metExploreD3.fireEventArg('buttonRefresh', "reloadMapping", false);
			                	// metExploreD3.fireEventArg('buttonRefresh', "reloadMapping", false);
			                	// metExploreD3.fireEvent('selectMappingVisu', "resetMapping");
			                	// _metExploreViz.resetMappings();
			                }
			           });
						
					}

					if(sessions[key].mapped)
					{
						networkVizSession.setMapped(sessions[key].mapped);
					}	

					if(sessions[key].mappingDataType)
					{
						networkVizSession.setMappingDataType(sessions[key].mappingDataType);
					}	
					
					if(sessions[key].activeMapping)
					{
						networkVizSession.setActiveMapping(sessions[key].activeMapping);
					}
				}


				if(jsonParsed.linkStyle)
				{
					var style = new LinkStyle(jsonParsed.linkStyle.size, jsonParsed.linkStyle.lineWidth, jsonParsed.linkStyle.markerWidth, jsonParsed.linkStyle.markerHeight, jsonParsed.linkStyle.markerInColor, jsonParsed.linkStyle.markerOutColor, jsonParsed.linkStyle.markerStrokeColor, jsonParsed.linkStyle.markerStrokeWidth, jsonParsed.linkStyle.strokeColor);
					metExploreD3.setLinkStyle(style);
					
				}
					
				if(jsonParsed.metaboliteStyle)
				{
					var style = new MetaboliteStyle(jsonParsed.metaboliteStyle.height, jsonParsed.metaboliteStyle.width, jsonParsed.metaboliteStyle.rx, jsonParsed.metaboliteStyle.ry, jsonParsed.metaboliteStyle.fontSize, jsonParsed.metaboliteStyle.strokeWidth, jsonParsed.metaboliteStyle.label, jsonParsed.metaboliteStyle.strokeColor);
					metExploreD3.setMetaboliteStyle(style);
				}

				if(jsonParsed.reactionStyle)
				{
					var style = new ReactionStyle(jsonParsed.reactionStyle.height, jsonParsed.reactionStyle.width, jsonParsed.reactionStyle.rx, jsonParsed.reactionStyle.ry, jsonParsed.reactionStyle.label, jsonParsed.reactionStyle.fontSize, jsonParsed.reactionStyle.strokeColor, jsonParsed.reactionStyle.strokeWidth);
					metExploreD3.setReactionStyle(style);
				}

				for (var key in sessions) {
					metExploreD3.GraphNetwork.refreshSvg(key);	
			    }
				endFunc();
			}
		}
	},

	/*****************************************************
	* Fill the data models with the store reaction
	*/
	initDataJSON : function(json, func){
		var jsonParsed = metExploreD3.GraphUtils.decodeJSON(json);
		if(jsonParsed){
			var networkVizSession = _metExploreViz.getSessionById("viz");
			
			var networkData = networkVizSession.getD3Data();
			
	        _metExploreViz.resetOldCoodinates();
	        networkData.getNodes().forEach(function(node){
	        	_metExploreViz.addOldCoodinates({"id":node.getId(), "x":node.x, "px":node.px, "y":node.y, "py":node.py});
	        });

			var oldForce = networkVizSession.getForce();
			// Reset visualisation---less than a ms
			if(oldForce!=undefined){
				oldForce.nodes([]);
				oldForce.links([]);

				oldForce.on("start", null);
				oldForce.on("end", null);
				oldForce.on("tick", null);

			}
			networkVizSession.reset();
			networkVizSession.setAnimated(true);

			var networkData = new NetworkData('viz');
			networkData.cloneObject(jsonParsed);
			var nodes = networkData.getNodes();
			nodes.forEach(function(node){
				if(node.getBiologicalType()=="metabolite")
				{
					if(networkData.getCompartmentByName(node.getCompartment())==null)
						networkData.addCompartment(node.getCompartment());
				}
				else
				{
					node.getPathways().forEach(function(pathway){
						if(networkData.getPathwayByName(pathway)==null)
							networkData.addPathway(pathway);
					});
				}

			});
			
			networkData.setId('viz');
			_metExploreViz.setInitialData(_metExploreViz.cloneNetworkData(networkData));
			networkVizSession.setD3Data(networkData);

		    metExploreD3.GraphNetwork.refreshSvg("viz");

		    var oldCoodinates = _metExploreViz.getOldCoodinates();
			if(oldCoodinates.length>0)
			{
				var overlap = false;
				var i = 0;
			    while (i < oldCoodinates.length-1 && !overlap) {
				    if(networkData.getNodeById(oldCoodinates[i].id)!=undefined)
				    	overlap=true;
				    i++;
				}

				if(overlap && !metExploreD3.getGeneralStyle().windowsAlertIsDisable()){
					metExploreD3.displayMessageYesNo("Coodinates",'Do you want keep node coordinates.',function(btn){
		                if(btn=="yes")
		                {   
		                	var selected = [];
				            oldCoodinates.forEach(function(coor){
				            	var node = networkData.getNodeById(coor.id);
					            if(node!=undefined){
					            	node.x = coor.x;
					            	node.y = coor.y;
					            	node.px = coor.px;
					            	node.py = coor.py;
					            	selected.push(coor.id);
								
					            }
				            });
				            d3.select("#viz").select("#graphComponent")
								.selectAll("g.node")
						        .filter(function(d) { return selected.indexOf(d.id)!=-1; })
						        .each(function(d) { 
						        	d.setLocked(!d.isLocked());
									d.fixed=d.isLocked();
						        });

				            d3.select("#viz").select("#graphComponent")
								.selectAll("g.node")
						        .filter(function(d) { return selected.indexOf(d.id)!=-1; })
						        .each(function(d) { _MyThisGraphNode.selection(d, "viz"); });
						 
		                }
		          	});
				}
			}

			

			if(_metExploreViz.getMappingsLength()>0)
			{
	            _metExploreViz.getMappingsSet().forEach(function(mapping){
	            	metExploreD3.GraphMapping.reloadMapping(mapping);
	            	metExploreD3.fireEventArg('selectMappingVisu', "jsonmapping", mapping);
	            }); 
	            metExploreD3.fireEventArg('buttonRefresh', "reloadMapping", true);
			}
		}
		func();			
	},

	/*****************************************************
	* Initialization of visualization
    * @param {} vizEngine : library used to make the visualization
	*/
	initiateViz : function(vizEngine) {

		d3.select("#viz").selectAll("#presentationViz, #presentationLogoViz").classed("hide", true);
		metExploreD3.fireEvent('viz', 'initiateviz');
		// Previously we used Cytoscape.js. Now we use D3.js,
		// that what is this test for
		_metExploreViz.setLaunched(true);
		if (vizEngine == 'D3') {
			metExploreD3.GraphNetwork.delayedInitialisation('viz');	
		}
	},

	loadData : function(panel){

		var newSession = _metExploreViz.getSessionById(panel);

		// var newDisplayNodeName = oldSession.getDisplayNodeName();
		// var newIsMapped = oldSession.isMapped();

		// var newSession = new NetworkVizSession();
	 //    newSession.setVizEngine("D3");
	 //    newSession.setId('viz');
	 //    newSession.setMapped(newIsMapped);
	 //    newSession.setDisplayNodeName(newDisplayNodeName);

	   
		return newSession;
	}
}
