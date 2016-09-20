
/**
 * @author MC
 * @description : Tu manage the metabolic network
 */

    	
metExploreD3.GraphNetwork = {
    
    task:"",

	/*******************************************
    * Initialization of variables  
    * @param {} panel : The panel where are the node
    */ 
	delayedInitialisation : function(panel) {

    	var that = {};

	    that.render = function() {
	    	var vis = d3.select('#'+panel);
			vis 
				.append("svg")
				.attr("width", "100%")
				.attr("height", "100%")
				.attr("class", "D3viz")
				.attr("id", "D3viz")
				.style("background-color", "#fff");
		};
		that.render();
		metExploreD3.GraphLink.delayedInitialisation(panel);

		metExploreD3.GraphNode.delayedInitialisation(panel);	
		return that;
	},

	/*******************************************
    * Refresh the graph interface & resize it if it's big at the beginnning
    * @param {} panel : The panel to refresh
    */ 
	tick : function(panel){
		if(_metExploreViz.getComparedPanelById(panel)!=null || panel=="viz"){
			
			var scale = metExploreD3.getScaleById(panel);
    
			metExploreD3.GraphLink.tick(panel, scale);
			metExploreD3.GraphNode.tick(panel);
			
			var  previousScale = scale.getZoomScale();
			
			var anim=metExploreD3.GraphNetwork.isAnimated(panel);
			
			// Resize it if it's big at the beginnning
			var session = _metExploreViz.getSessionById(panel);
			var generalStyle = metExploreD3.getGeneralStyle();
			// Control if the user can see all the graph
			if (anim && previousScale>0.05 && session.isResizable()) {
				
				var vizRect = document.getElementById(panel).getBoundingClientRect();
				var graphComponentRect = d3.select("#"+panel).select("#D3viz")[0][0].getElementById('graphComponent').getBoundingClientRect();
				
				var width = parseInt(d3.select("#"+panel).select("#D3viz")
					.style("width"));
				var height = parseInt(d3.select("#"+panel).select("#D3viz")
					.style("height"));

				if(vizRect.top>graphComponentRect.top 
					|| vizRect.left>graphComponentRect.left 
					|| vizRect.bottom<graphComponentRect.bottom 
					|| vizRect.right<graphComponentRect.right)
				{
					var dataLength =session.getD3Data().getNodesLength();
					var delay = 3000;
					if (dataLength < generalStyle.getReactionThreshold() || !generalStyle.isDisplayedLabelsForOpt())						
						delay = 3000;
						
					metExploreD3.fixDelay(metExploreD3.GraphNetwork.task, delay);

					var zoomListener = scale.getZoom();

					var updateScale = 0.01*dataLength/100;
			    	var newScale = previousScale-(previousScale*updateScale);
	            	zoomListener.scale(newScale);

					var newWidth = newScale*width;
					var newHeight = newScale*height;
					var xScale = (width-newWidth)/2;
					var yScale = (height-newHeight)/2;
					zoomListener.translate([xScale,yScale]);
					
					zoomListener.event(d3.select("#"+panel).select("#D3viz"));	
	            	
	            	scale.setZoomScale(newScale);
					scale.setXScale(zoomListener.x());
					scale.setYScale(zoomListener.y());	
				}
				else
				{
					if(!((vizRect.top+height/10>graphComponentRect.top && vizRect.bottom-height/10<graphComponentRect.bottom) 
										|| (vizRect.left+width/10>graphComponentRect.left && vizRect.right-width/10<graphComponentRect.right))){
						var dataLength =session.getD3Data().getNodesLength();
						var delay = 3000;
						if (dataLength < generalStyle.getReactionThreshold() || !generalStyle.isDisplayedLabelsForOpt())						
							delay = 3000;
							
						metExploreD3.fixDelay(metExploreD3.GraphNetwork.task, delay);

						var zoomListener = scale.getZoom();

						if(updateScale==undefined) updateScale = 0.01;
						else updateScale = updateScale/2;

				    	var newScale = previousScale+(previousScale*updateScale);
		            	zoomListener.scale(newScale);

						var newWidth = newScale*width;
						var newHeight = newScale*height;
						var xScale = (width-newWidth)/2;
						var yScale = (height-newHeight)/2;
						zoomListener.translate([xScale,yScale]);
						
						zoomListener.event(d3.select("#"+panel).select("#D3viz"));	
		            	
		            	scale.setZoomScale(newScale);
						scale.setXScale(zoomListener.x());
						scale.setYScale(zoomListener.y());	
					}
				}
			}
		}
	},

	/*******************************************
    * Zoom on the main panel and on link graph
    * @param {} panel : The panel to refresh
    */ 
	zoom:function(panel) {
		var scale = metExploreD3.getScaleById(panel);
		d3.select("#"+panel).select("#D3viz").select("#graphComponent").attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
		var zoomListener = scale.getZoom();

		// Firstly we changed the store which correspond to viz panel
		scale.setZoomScale(d3.event.scale);
		scale.setXScale(zoomListener.x());
		scale.setYScale(zoomListener.y());

		metExploreD3.GraphLink.tick(panel, scale);
	},

	/*******************************************
    * Zoom on the main panel and on link graph with button
    */ 
    zoomIn:function() {
		_MyThisGraphNode.dblClickable=false;
		var panel = this.parentNode.parentNode.id;
		var scale = metExploreD3.getScaleById(panel);
		var zoomListener = scale.getZoom();
		var session = _metExploreViz.getSessionById(panel);
		var vizRect = document.getElementById(panel).getBoundingClientRect();
		var graphComponentRect = d3.select("#"+panel).select("#D3viz")[0][0].getElementById('graphComponent').getBoundingClientRect();
			
		var zoomListener = scale.getZoom();
		var width = parseInt(d3.select("#"+panel).select("#D3viz")
			.style("width"));
		var height = parseInt(d3.select("#"+panel).select("#D3viz")
			.style("height"));

    	zoomListener.scale(scale.getZoomScale()*1.1);

		
		zoomListener.event(d3.select("#"+panel).select("#D3viz"));		
		
		scale.setXScale(zoomListener.x());
		scale.setYScale(zoomListener.y());

		// Firstly we changed the store which correspond to viz panel
		scale.setZoomScale(scale.getZoomScale()*1.1);

		metExploreD3.GraphLink.tick(panel, scale);
	},

	/*******************************************
    * Zoom out the main panel and on link graph with button
    * @param {} panel : The panel to refresh
    */ 
	zoomOut:function() {
		_MyThisGraphNode.dblClickable=false;
		var panel = this.parentNode.parentNode.id;
		var scale = metExploreD3.getScaleById(panel);
		var zoomListener = scale.getZoom();
		var session = _metExploreViz.getSessionById(panel);
		var vizRect = document.getElementById(panel).getBoundingClientRect();
		var graphComponentRect = d3.select("#"+panel).select("#D3viz")[0][0].getElementById('graphComponent').getBoundingClientRect();
			
		var zoomListener = scale.getZoom();
		var width = parseInt(d3.select("#"+panel).select("#D3viz")
			.style("width"));
		var height = parseInt(d3.select("#"+panel).select("#D3viz")
			.style("height"));

    	zoomListener.scale(scale.getZoomScale()*0.9);
	
		zoomListener.event(d3.select("#"+panel).select("#D3viz"));		
		
		scale.setXScale(zoomListener.x());
		scale.setYScale(zoomListener.y());

		// Firstly we changed the store which correspond to viz panel
		scale.setZoomScale(scale.getZoomScale()*0.9);

		metExploreD3.GraphLink.tick(panel, scale);
	},

	/*******************************************
    * Put animation button on
    * @param {} panel : The panel where the button must be on
    */ 
	animationButtonOn:function(panel) {
		d3.select("#"+panel).select("#buttonAnim").select("image").remove();
			
		d3.select("#"+panel).select("#buttonAnim").append("image").attr(
			"xlink:href",
			document.location.href.split("index.html")[0] + "resources/icons/pause.svg").attr(
			"width", "50").attr("height", "50")
			.attr("transform",
					"translate(10,10) scale(.5)");

		metExploreD3.GraphNetwork.setAnimated(panel, true);
	},

	/*******************************************
    * Put animation button off
    * @param {} panel : The panel where the button must be off
    */ 
	animationButtonOff:function(panel) {
		d3.select("#"+panel).select("#buttonAnim").select("image").remove();
			
		d3.select("#"+panel).select("#buttonAnim").append("image").attr(
				"xlink:href",
				document.location.href.split("index.html")[0] + "resources/icons/play.svg").attr(
				"width", "50").attr("height", "50")
				.attr("transform",
						"translate(10,10) scale(.5)");
	
		metExploreD3.GraphNetwork.setAnimated(panel, false);
	},

	/*******************************************
    * Start or stop the animation
    */ 
	play:function(d) {
		var sessions = _metExploreViz.getSessionsSet();
		var panel = this.parentNode.parentNode.id;
		
		var session = _metExploreViz.getSessionById(panel);
		if(session!=undefined)  
		{
			var anim = metExploreD3.GraphNetwork.isAnimated(panel);;
			if (anim == "false") {
				if(session.isLinked())
				{
					for (var key in sessions) {
						if(sessions[key].isLinked()){
							metExploreD3.GraphNetwork.animationButtonOn(sessions[key].getId());
						}
					}

					var force = _metExploreViz.getSessionById("viz").getForce();
					force.start();
				}
				else
				{
					metExploreD3.GraphNetwork.animationButtonOn(panel);
					var force = session.getForce();
					force.start();

				}
			} else {
				if(session.isLinked())
				{
					for (var key in sessions) {
						if(sessions[key].isLinked()){
							metExploreD3.GraphNetwork.animationButtonOff(sessions[key].getId());
						}
					}
					var force = _metExploreViz.getSessionById("viz").getForce();
					force.stop();
				}
				else
				{
					metExploreD3.GraphNetwork.animationButtonOff(panel);
					var force = session.getForce();
					force.stop();

					
				}
			}
		}
	},

	/*******************************************
    * Link or unlink the main graph and the selected graph  
    */ 
	setLink:function(d) {
		that = this;
		var panel = this.parentNode.parentNode.id;
		var session = _metExploreViz.getSessionById(panel);
		var mainSession = _metExploreViz.getSessionById('viz');
		if(session!=undefined)  
		{
			var force = session.getForce();
			var linked = d3.select(this).attr("isLink");
			d3.select(this).select("image").remove();
			if (linked == "false") {
				metExploreD3.GraphNetwork.link(that);
			} else {
				metExploreD3.GraphNetwork.unLink(that);
			}
		}
	},
	
	/*******************************************
    * Link the main graph and the selected graph  
    * @param {} panel : The panel to link
    */
    link :function(that){
		var panel = that.parentNode.parentNode.id;
		var session = _metExploreViz.getSessionById(panel);
		var mainSession = _metExploreViz.getSessionById('viz');
		var anim = metExploreD3.GraphNetwork.isAnimated("viz");


		d3.select(that).attr("isLink", "true");
		session.setLinked(true);
		mainSession.setLinked(true);

		if (anim == "true")
			metExploreD3.GraphNetwork.animationButtonOn(panel);
		else
			metExploreD3.GraphNetwork.animationButtonOff(panel);
		

		var linked = d3.select(that).attr("isLink");
		d3.select(that).select("image").remove();
		d3.select(that).append("image")
			.attr("xlink:href",document.location.href.split("index.html")[0] + "resources/icons/link.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform","translate(10,50) scale(.5)");

		if(session!=undefined)  
		{
			if(mainSession.getDuplicatedNodesCount()>0){

				var allNodes = d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll("g.node")
					.filter(function(d) {
						return d.getBiologicalType()=='metabolite';
					});

				mainSession.getDuplicatedNodes().forEach(function(id){
					allNodes
					.filter(function(d) {
						return d.getId()==id;
					})
					.each(function(d){ d.setIsSideCompound(true);});
				});
				metExploreD3.GraphNetwork.duplicateSideCompoundsById(mainSession.getDuplicatedNodes(), panel);
				
				metExploreD3.GraphNetwork.looksLinked();
				if(session.isLinked()){
					metExploreD3.GraphNetwork.graphAlignment(panel);
				}
			}
			else
			{
				metExploreD3.GraphNetwork.graphAlignment(panel);
			}
		}
		metExploreD3.GraphNetwork.initCentroids();
	},
	
	/*******************************************
    * Unlink the main graph and the selected graph  
    * @param {} panel : The panel to unlink
    */
    unLink :function(that){
		var panel = that.parentNode.parentNode.id;
		var session = _metExploreViz.getSessionById(panel);

		d3.select(that).append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/unlink.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate(10,50) scale(.5)");
		
		d3.select(that).attr("isLink", "false");
		session.setLinked(false);
		metExploreD3.GraphNetwork.looksLinked();

		var anim = metExploreD3.GraphNetwork.isAnimated(panel);
		if (anim == "true"){
			var force = session.getForce();
			force.start();	
		}
	},

	/*******************************************
    * True if at least one network is linked with the main network
    */
    looksLinked : function(){
    	var sessions = _metExploreViz.getSessionsSet();
		var mainSession = _metExploreViz.getSessionById('viz');
		mainSession.setLinked(false);

		for (var key in sessions) {
			if(sessions[key].isLinked())
				mainSession.setLinked(true);
		}	
	},

	/*******************************************
    * Refresh the graph data, it generate graph visualization
    * @param {} panel : The panel to refresh
    */
    refreshSvg : function(panel) {	

    	var networkData = _metExploreViz.getSessionById(panel).getD3Data();
    	var nodes = networkData.getNodes();

    	metExploreD3.fireEventParentWebSite("refreshCart", nodes);

    	var optArray = [];
		for (var i = 0; i < nodes.length - 1; i++) {
		    optArray.push(nodes[i].name);
		}
		optArray = optArray.sort();
		
		// Get height and witdh of panel		
		var h = parseInt(metExploreD3.GraphPanel.getHeight(panel));
		var w = parseInt(metExploreD3.GraphPanel.getWidth(panel));
		var linkStyle = metExploreD3.getLinkStyle();
		var generalStyle = metExploreD3.getGeneralStyle();				
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var reactionStyle = metExploreD3.getReactionStyle();

		var maxDimRea = Math.max(reactionStyle.getWidth(),reactionStyle.getHeight());
		var maxDimMet = Math.max(metaboliteStyle.getWidth(),metaboliteStyle.getHeight());
		var maxDim = Math.max(maxDimRea, maxDimMet);
		// Initiate the D3 force drawing algorithm
		var force = d3.layout.force().friction(0.90).gravity(0.06)
				.charge(-150)
				.linkDistance(function(link){
					if(link.getSource().getIsSideCompound() || link.getTarget().getIsSideCompound())
						return linkStyle.getSize()/2+maxDim;
					else
						return linkStyle.getSize()+maxDim;
				})
				.size([ w, h ]);
		
		
		var session = _metExploreViz.getSessionById(panel);
		
		session.setActivity(true);
		session.setForce(force);
		// Call GraphCaption to draw the caption
		if(panel=='viz')
			metExploreD3.GraphCaption.drawCaption();
		
		// var startall = new Date().getTime();
		// var start = new Date().getTime();
		// console.log("----Viz: START refresh/init Viz");
		
		// Define the zoomListener and put it in a store

		var xScale =
			  d3.scale.linear()
			    .domain([0, w])
			    .range([0, w]);

			var yScale =
			  d3.scale.linear()
			    .domain([h, 0])
			    .range([h, 0]);

		if(session.getScale()==undefined){
		
			// Define the zoomListener which calls the zoom function on the "zoom" event constrained within the scaleSents
			var that = metExploreD3.GraphNetwork;
			metExploreD3.GraphNetwork.zoomListener = d3.behavior
				.zoom()
				.x( xScale )
				.y( yScale )
				.scaleExtent([ 0.01, 30 ])
				.on("zoom", function(e){
						
						if(metExploreD3.GraphNetwork.zoomListener.scale()<0.8) d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", true);
						else d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", false);

					var session = _metExploreViz.getSessionById(panel);
	        		
	        		if(d3.event.sourceEvent !=null)
							if(d3.event.sourceEvent.type=='wheel')
								session.setResizable(false);
		        	
		        	// if visualisation is actived we add item to menu
	        		if(session.isActive()){
					
						that.zoom(panel);
					}
				});
		
		
			var scale = new Scale(panel);
			scale.setScale(xScale, yScale, 1, 1, 1, metExploreD3.GraphNetwork.zoomListener.scale(), metExploreD3.GraphNetwork.zoomListener);

			metExploreD3.setScale(scale, panel);
			
		}
		else
		{
			var that = metExploreD3.GraphNetwork;
			
			metExploreD3.GraphNetwork.zoomListener = d3.behavior
					.zoom()
					.x( xScale )
					.y( yScale )
					.scaleExtent([ 0.01, 30 ])
					.on("zoom", function(e){

						
						if(metExploreD3.GraphNetwork.zoomListener.scale()<0.8) d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", true);
						else d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", false);

						var session = _metExploreViz.getSessionById(this.parentNode.id);
						
						if(d3.event.sourceEvent !=null)
							if(d3.event.sourceEvent.type=='wheel')
								session.setResizable(false);
		        	
		        		// if visualisation is actived we add item to menu
		        		if(session.isActive()){
							that.zoom(this.parentNode.id);
						}
					});
			var scale = new Scale(panel);
			scale.setScale(xScale, yScale, 1, 1, 1, metExploreD3.GraphNetwork.zoomListener.scale(), metExploreD3.GraphNetwork.zoomListener);

			metExploreD3.setScale(scale, panel);		
		}


		force.on("start", function(){
			if (networkData.getNodes().length > generalStyle.getReactionThreshold() && generalStyle.isDisplayedLinksForOpt())
				d3.selectAll("path.link").remove();
		});

		force.on("end", function(){
			var scale = metExploreD3.getScaleById(panel);
			if ((networkData.getNodes().length > generalStyle.getReactionThreshold() && generalStyle.isDisplayedLinksForOpt())) {
				metExploreD3.GraphLink.reloadLinks(panel, networkData, linkStyle, metaboliteStyle);
			}
			metExploreD3.GraphLink.tick(panel, scale);
		});


		// Remove all sub-elements in the SVG that corresponds to the D3Viz part --- tenth mss
		var vis = d3.select("#"+panel);
		vis.svg = vis.select("#D3viz").selectAll("*").remove();

		_metExploreViz.setLinkedByTypeOfMetabolite(false);
		// Brush listener to multiple selection
		var nodeBrushed;
		var brushing = false;
		var brush = d3.select("#"+panel).select("#D3viz")
			.append("g")
			.datum(function() { return {selected: false, previouslySelected: false}; })
			.attr('id','brush')
			.attr("class", "brush")
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
											var xScale=scale.getXScale();
											var yScale=scale.getYScale();

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
		var h = parseInt(metExploreD3.GraphPanel.getHeight(panel));
		var w = parseInt(metExploreD3.GraphPanel.getWidth(panel));
		
		// Options div
		d3.select("#"+panel)
			.select("#D3viz")
			.append("foreignObject")	
			.attr('x', w-300)
			.attr('y', 100)
			.attr("width", "500")
			.attr("height", "500")
			.append("xhtml:div")
			.attr("id","tooltip2")
			.classed("tooltip2", true)
			.classed("hide", true);

		// Define zoomListener
		vis.svg = d3.select("#"+panel).select("#D3viz")
				.call(metExploreD3.GraphNetwork.zoomListener)
				// Remove zoom on double click
				.on("dblclick.zoom", null)
				// .on("wheel.zoom", function(){console.log("wheel")})
				.attr("pointer-events", "all")
				.append('svg:g')
				.attr("class","graphComponent").attr("id","graphComponent");
		
		// If a graph is already loaded
		if(session!=undefined)  
		{
			// We stop the previous animation
			var force = session.getForce();
			// if(force!=undefined)  
			// {		
			// 	force.stop();
			// 	metExploreD3.GraphNetwork.setAnimated(panel, false);
			// }

			if(session.isResizable()!=undefined && session.isResizable()!=false)
				metExploreD3.GraphNetwork.task.cancel();

			// Launch the task to resize the graph at the beginning ->tick function
			session.setResizable(true);
			metExploreD3.GraphNetwork.task = metExploreD3.createDelayedTask(
				function(){
					session.setResizable(false);
				}
			);
		}

		// Define play and stop button ->play function
		d3
			.select("#"+panel)
			.select("#D3viz")
        	.attr("animation", function(){
        		if(session.isAnimated())
        			return true;
        		else
        			return false;
        	})
			.append("svg:g")
			.attr("class","buttonAnim").attr("id","buttonAnim")
			.on("click", metExploreD3.GraphNetwork.play)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", function(){
				if(session.isAnimated())
					return document.location.href.split("index.html")[0] + "resources/icons/pause.svg";
				else
					return document.location.href.split("index.html")[0] + "resources/icons/play.svg";
			})
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate(10,10) scale(.5)");

		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonRescale").attr("id","buttonRescale")
		// .on("click", metExploreD3.GraphNetwork.play)
			.on("click", function(){
				metExploreD3.GraphNetwork.rescale(panel);
			})
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", function(){
				return document.location.href.split("index.html")[0] + "resources/icons/rescale.png";
			})
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate(80,10) scale(.5)");

		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","whiteBlack").attr("id","whiteBlack")
			.attr('x', (w-100))
			.attr('y', 100)
			.on("click", function(){
				if(d3.select("#"+panel).style("-webkit-filter").search('grayscale') == -1
					&& d3.select("#"+panel).style("filter").search('grayscale') == -1)
					d3.select("#"+panel).style("filter", "grayscale(100%)").style("-webkit-filter", "grayscale(100%)");
				else
					d3.select("#"+panel).style("filter", "").style("-webkit-filter", "");
			})
			.style("cursor", "hand")
			.style("visibility", "hidden")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/blackWhite.png")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate("+(w-100)+",100) scale(0.5)");

		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","invertColor").attr("id","invertColor")
			.attr('x', (w-100))
			.attr('y', 150)
			.on("click", function(){
				if(d3.select("#"+panel).style("-webkit-filter").search('invert') == -1
					&& d3.select("#"+panel).style("filter").search('invert') == -1)
					d3.select("#"+panel).style("filter", "invert(100%)").style("-webkit-filter", "invert(100%)");
				else
					d3.select("#"+panel).style("filter", "").style("-webkit-filter", "");
			})
			.style("cursor", "hand")
			.style("visibility", "hidden")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/invertColor.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate("+(w-100)+",150) scale(0.5)");

		

		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonZoomIn").attr("id","buttonZoomIn")
			.attr('x', (w-60))
			.attr('y', 10)
			.on("click", metExploreD3.GraphNetwork.zoomIn)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/zoomin.svg")
			.attr("width", "50")
			.attr("height", "50")
			.style("opacity", 0.2)
			.attr("transform", "translate("+(w-60)+",10) scale(1)")
			.on("mouseover", function(d) {  
				d3.select(this).transition().duration(500).style("opacity", 1);
		    })
	        .on("mouseout", function(d) {   
		    	d3.select(this).transition().duration(500).style("opacity", 0.2);
	        });


		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonZoomOut").attr("id","buttonZoomOut")
			.attr('x', (w-110))
			.attr('y', 10)
			.on("click", metExploreD3.GraphNetwork.zoomOut)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/zoomout.svg")
			.attr("width", "50")
			.attr("height", "50")
			.style("opacity", 0.2)
			.attr("transform", "translate("+(w-110)+",10) scale(1)")
			.on("mouseover", function(d) {  
				d3.select(this).transition().duration(500).style("opacity", 1);
		    })
	        .on("mouseout", function(d) {   
		    	d3.select(this).transition().duration(500).style("opacity", 0.2);
	        });
    
	    d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonHand").attr("id","buttonHand")
			.attr('x', (w-160))
			.attr('y', 10)
        	.attr("scrollable", "false")
			.on("click", metExploreD3.GraphNetwork.moveGraph)
			.style("opacity", 1)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/handcursor.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate("+(w-160)+",10) scale(1)");
		
		d3
			.select("#"+panel)
			.select("#D3viz")
			.select("buttonHand")
			.style("opacity", 0);

	    d3.select('#'+panel)
			.on("mouseover", function(){
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomOut")
					.transition().duration(500).style("opacity", 1);
					
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomIn")
					.transition().duration(500).style("opacity", 1);	
				
				var session = _metExploreViz.getSessionById(panel);
        		// if visualisation is actived we add item to menu
        		if(session.isActive()){
					var scrollable = d3.select("#"+panel).select("#buttonHand").attr("scrollable");
					if(scrollable == "false")
						d3.select("#"+panel)
							.select("#D3viz")
							.select("#buttonHand")
							.transition().duration(500).style("opacity", 0.2);
					else
						d3.select("#"+panel)
							.select("#D3viz")
							.select("#buttonHand")
							.transition().duration(500).style("opacity", 1);
				}				
			})
			.on("mouseout", function(){
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomOut")
					.transition().duration(500).style("opacity", 0);

				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomIn")
					.transition().duration(500).style("opacity", 0);

				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonHand")
					.transition().duration(500).style("opacity", 0);
			})

		// Start the animation
		if(session.isAnimated())
    		metExploreD3.GraphNetwork.setAnimated(panel, true);
    	else
    		metExploreD3.GraphNetwork.setAnimated(panel, false);


    	// Refresh coresponding nodes and links 
    	var linkStyle = metExploreD3.getLinkStyle();
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		
		metExploreD3.GraphLink.refreshLink(panel, session, linkStyle, metaboliteStyle);
		metExploreD3.GraphNode.refreshNode(panel);
		
		// Define play and stop button ->play function
		if(panel!="viz"){
			d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonLink").attr("id","buttonLink")
        	.attr("isLink", "false")
			.on("click", metExploreD3.GraphNetwork.setLink)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", function(){
				if(session.isLinked())	
					return document.location.href.split("index.html")[0] + "resources/icons/link.svg";
				else
					return document.location.href.split("index.html")[0] + "resources/icons/unlink.svg";
			})
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate(10,50) scale(.5)");

		}
		else
		{
			metExploreD3.GraphNetwork.looksLinked();
			if(session.isLinked()){
				metExploreD3.GraphNetwork.graphAlignment(panel);
			}
		}
		
		// 62771 ms for recon before refactoring
		// 41465 ms now
		// var endall = new Date().getTime();
		// var timeall = endall - startall;
		// console.log("----Viz: FINISH refresh/ all "+timeall);
		var networkData = session.getD3Data();	
		var force = session.getForce();
		
		/*var stringJSON="{\"nodes\":";	
		stringJSON+=Ext.encode(networkData.getNodes());	
		stringJSON+=",\n\"links\":";
		stringJSON+=Ext.encode(networkData.getLinks());
		stringJSON+='}\n';	
		console.log(stringJSON);*/
		
		// Get bound effect
		// console.log(force.alpha());

		force
			.nodes(networkData.getNodes())
			.links(networkData.getLinks())
			.on("tick", function(e){
				var useClusters = metExploreD3.getGeneralStyle().useClusters();
				var componentDisplayed = metExploreD3.getGeneralStyle().isDisplayedConvexhulls();
				if(useClusters && componentDisplayed!=false){
					var k = e.alpha * .1;
					networkData.getNodes().forEach(function(node) {
						if(componentDisplayed=="Compartments"){
							var group = null;
							if(node.getBiologicalType()=="metabolite"){
								group = node.getCompartment();
								
							}
							else
							{
								var nbComp = [];
								for (var key in session.groups) {
								  	if (session.groups.hasOwnProperty(key)) {
										var index = session.groups[key].values.indexOf(node);
										if(index!=-1)
											nbComp.push(session.groups[key].key);
								  	}
								}	
								if(nbComp.length<2)
									group = nbComp[0];
							}
							if(group!=null)
					    	{
					    		var forceCentroids = _metExploreViz.getSessionById(panel).getForceCentroids();
								var theCentroid = forceCentroids.nodes()
					    			.find(function(centroid){
					    				return centroid.id == group;
					    			}
					    		);	
						    	node.x += (theCentroid.x - node.x) * k;
						    	node.y += (theCentroid.y - node.y) * k;	
						    }		
						}
						else
						{	
							if(componentDisplayed=="Pathways" && node.getPathways().length<2){
						    	var group = session.getGroupByKey(node.getPathways()[0]);
						    	// here you want to set center to the appropriate [x,y] coords
						    	if(group!=null)
						    	{
						    		// var center = group.center;  
						    		// d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.centroid")
			    					// 	.filter(function(centroid){
			    					// 		console.log(node.getPathways()[0]);
			    					// 		console.log(centroid.id);
			    					// 		return centroid.id == node.getPathways()[0];
			    					// 	})
			    					// 	.each(function(centroid){
			    					// 		var center = {x:centroid.x, y:centroid.y};
			    					// 	});
			    					var forceCentroids = _metExploreViz.getSessionById(panel).getForceCentroids();
						    		var theCentroid = forceCentroids.nodes()
						    			.find(function(centroid){
						    				return centroid.id == node.getPathways()[0];
						    			}
						    		);	
							    	node.x += (theCentroid.x - node.x) * k;
							    	node.y += (theCentroid.y - node.y) * k;	
							    }							
								
							}
						}
					});
				}
				// // Go when the bound effect is under .08
				// if(force.alpha() < .08){
				if(force.alpha() >= .005){
				        setTimeout(metExploreD3.GraphNetwork.tick(panel), 0);
				}
				// }
			});

		if(session.isAnimated())
			force.start();
		else
		{
			force.start();
			force.stop();
			metExploreD3.GraphNetwork.tick(panel);
		}
        
        var isDisplay = generalStyle.isDisplayedConvexhulls();
        

		if(isDisplay && panel=="viz") metExploreD3.GraphLink.displayConvexhulls(panel);

		session.setForce(force);
	},

	rescale : function(panel){
		var graphComponentRect = d3.select("#"+panel).select("#D3viz")[0][0].getElementById('graphComponent').getBoundingClientRect();
		var vizRect = document.getElementById(panel).getBoundingClientRect();
		var hViz = vizRect.bottom - vizRect.top-20;
		var hGC = graphComponentRect.bottom - graphComponentRect.top;
		console.log(hGC);
		var scale = metExploreD3.getScaleById(panel);
		var zoomListener = scale.getZoom();

		var newScale = hViz*zoomListener.scale()/hGC;
		console.log(newScale);
		scale.setZoomScale(newScale);

		var wGC = graphComponentRect.right-graphComponentRect.left;
		var hGC = graphComponentRect.bottom-graphComponentRect.top;

		var hViz = vizRect.bottom - vizRect.top-20;
		var wViz = vizRect.right - vizRect.left-20;
		d3.select("#"+panel).select("#D3viz").select("#graphComponent")
		var zoom = scale.getZoom();
		zoom.scale(newScale);
		var dcx = (wViz/2-((wViz/2)*zoom.scale()));
		var dcy = (hViz/2-((hViz/2)*zoom.scale()));
		zoom.translate([dcx,dcy]);
		d3.select("#"+panel).select("#D3viz").select("#graphComponent").attr("transform", "translate("+ dcx + "," + dcy +")scale(" + newScale + ")");

	},
	initCentroids : function(){
		//d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node").filter(function(node){return node.getPathways().length>1}).style("fill", 'red');

		var panel = "viz";
		var h = parseInt(metExploreD3.GraphPanel.getHeight(panel));
		var w = parseInt(metExploreD3.GraphPanel.getWidth(panel));
		var linkStyle = metExploreD3.getLinkStyle();
		var generalStyle = metExploreD3.getGeneralStyle();				
		var session = _metExploreViz.getSessionById(panel);
    	var networkData = session.getD3Data();
		var force2 = d3.layout.force().friction(0.90).gravity(0.08).charge(-4000).theta(0.2)
    			.linkDistance(600)
				.size([ w, h ]);

		session.setForceCentroids(force2);

		var componentDisplayed = metExploreD3.getGeneralStyle().isDisplayedConvexhulls();
		
		var components = [];

		if(componentDisplayed=="Compartments"){
			networkData.getCompartments().forEach(function(compartment){
				components.push({"id":compartment.identifier,x:2,y:2});
			});

			var links = [];

			d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
				.filter(function(node){
					return node.getBiologicalType()=="reaction";
				})
				.filter(function(node){
					var nbComp = 0;
					for (var key in session.groups) {
					  	if (session.groups.hasOwnProperty(key)) {
					  	  	
							var index = session.groups[key].values.indexOf(node);
							if(index!=-1)
								nbComp++;
					  	}
					}	
					return nbComp.length>1
				})
				.each(function(node){
					node.getCompartment().forEach(function(compartment){
						node.getCompartment().forEach(function(compartment2){
							if(compartment!=compartment2){
								var sourceIndex = components.findIndex(function(path){
									return path.id==compartment;
								});
								var targetIndex = components.findIndex(function(path){
									return path.id==compartment2;
								});

								var theLink = links.find(function(link){
									return link.source==sourceIndex && link.target==targetIndex;
								});
								
								if(theLink==undefined)
									links.push({"source":sourceIndex, "target":targetIndex});
								
							}
						});				
					});

				});
		}
		else
		{
			networkData.getPathways().forEach(function(pathway){
				components.push({"id":pathway,x:2,y:2});
			});

			var links = [];

			d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node").filter(function(node){return node.getPathways().length>1})
				.each(function(node){
					node.getPathways().forEach(function(pathway){
						node.getPathways().forEach(function(pathway2){
							if(pathway!=pathway2){
								var sourceIndex = components.findIndex(function(path){
									return path.id==pathway;
								});
								var targetIndex = components.findIndex(function(path){
									return path.id==pathway2;
								});

								var theLink = links.find(function(link){
									return link.source==sourceIndex && link.target==targetIndex;
								});
								
								if(theLink==undefined)
									links.push({"source":sourceIndex, "target":targetIndex});
								
							}
						});				
					});

				});
		}
				
		

		// var lien = d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("linkCentroid")
		//       .data(links)
		//     	.enter().append("path")
		//       .attr("class", "linkCentroid")
		//       .style("stroke", "red")
		//       .style("stroke-width", 1);

		// d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.centroid")
		// 	.data(pathways).enter()
		// 	.append("svg:g").attr("class", "centroid")
		// 	.style("fill", "white")
		// 	.append("rect")
		// 	.attr("id",function(pathway){ return pathway.id})
		// 	.attr("width", 6)
		// 	.attr("height", 6)
		// 	.attr("rx", 3)
		// 	.attr("ry", 3)
		// 	.attr("transform", "translate(-" + 6/2 + ",-"
		// 							+ 6/2
		// 							+ ")")
		// 	.style("stroke", "blue")
		// 	.style("stroke-width", 6);

		
		force2
			.nodes(components)
			.links(links)
			// .on("tick", function(e){
			// 	d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			// 		.selectAll("g.centroid")
			// 		.attr("cx", function(d) {
			// 			return d.x;
			// 		})
			// 		.attr("cy", function(d) {
			// 			return d.y;
			// 		})
			// 		.attr("transform", function(d) {
			// 			//  scale("+ +")
			// 			var scale = 1;
			// 			if(d3.select(this)!=null){
			// 				var transformString = d3.select(this).attr("transform");
			// 				if(d3.select(this).attr("transform")!=null){
			// 					var indexOfScale = transformString.indexOf("scale(");
			// 					if(indexOfScale!=-1)
			// 						scale = parseInt(transformString.substring(indexOfScale+6, transformString.length-1));
			// 				}
			// 			}
			// 			return "translate(" + d.x + "," + d.y + ") scale("+scale+")";
			// 		});

			// 	// lien.attr("x1", function(d) { return d.source.x; })
			//  //        .attr("y1", function(d) { return d.source.y; })
			//  //        .attr("x2", function(d) { return d.target.x; })
			//  //        .attr("y2", function(d) { return d.target.y; });
			// })
			.start();
	},

	/*******************************************
    * Change the cursor state to move the graph  
    */
    moveGraph : function(){

		_MyThisGraphNode.dblClickable=false;
		var panel = this.parentNode.parentNode.id;
		var scrollable = d3.select("#"+panel).select("#buttonHand").attr("scrollable");
		
		if(scrollable == "false"){
			d3.select("#"+panel).select("#D3viz").select("#buttonHand").transition().duration(500).style("opacity", 1);
			d3.select("#"+panel).select("#buttonHand").attr("scrollable", true);
		}
		else
		{
			d3.select("#"+panel).select("#D3viz").select("#buttonHand").transition().duration(500).style("opacity", 0.2);
			d3.select("#"+panel).select("#buttonHand").attr("scrollable", false);
		}
	},

	/*******************************************
    * Align linked graphs
    * @param {} panel : The panel to align with the main
    */
    graphAlignment : function(panel){
		var session = _metExploreViz.getSessionById(panel);

		if(panel!="viz")
		{
			var mainSession = _metExploreViz.getSessionById("viz");
			d3.select("#"+panel).select("#D3viz").select("#graphComponent")
				.selectAll("g.node")
				.each(function(node){
					var nodeLinked = this;
					var color = d3.select(nodeLinked).select('rect').style("fill");
					d3.select("#viz").select("#D3viz").select("#graphComponent")
						.selectAll("g.node")
						.each(function(d){
							if(d.getId() == node.getId())
							{
								// Align nodes with the main graph
								node.x = d.x;
								node.y = d.y;

								if(d.getMappingDatasLength()>0){
					                d.getMappingDatas().forEach(function(mappingData){
					                	if(mappingData.getMapValue()==undefined)
											node.addMappingData(new MappingData(node, mappingData.getMappingName().valueOf(), mappingData.getConditionName().valueOf(), undefined));
					                	else
					                		node.addMappingData(new MappingData(node, mappingData.getMappingName().valueOf(), mappingData.getConditionName().valueOf(), mappingData.getMapValue().valueOf()));
					                });
					            }
								// Select same nodes that the main graph
								if(node.selected && !d.isSelected()){
									_MyThisGraphNode.selection(d, "viz");
								}

								if(!node.selected && d.isSelected()){
									_MyThisGraphNode.selection(node, panel);
								}
								var colorMain = d3.select(this).select('rect.'+d.getBiologicalType()).style("fill");
								
								if(color!=colorMain){
									d3.select(nodeLinked)
										.select('rect.'+d.getBiologicalType())
										.style("fill", colorMain);

									if(d.getBiologicalType()=="metabolite")
										var style = metExploreD3.getMetaboliteStyle();
									else
									{
										var style = metExploreD3.getReactionStyle();

										var colorText = metExploreD3.GraphUtils.chooseTextColor(colorMain);
										d3.select(nodeLinked).select('text').style("fill", colorText);
									}

									var nbMapped = d3.select(this).select('rect.'+d.getBiologicalType()).attr("mapped");
									if(nbMapped>0){
										d3.select(nodeLinked)
											.insert("rect", ":first-child")
											.attr("class", "stroke")
											.attr("width", style.getWidth()+4)
											.attr("height", style.getHeight()+4)
											.attr("rx", style.getRX())
											.attr("ry", style.getRY())
											.attr("transform", "translate(-" + parseInt(style.getWidth()+4) / 2 + ",-"
																+ parseInt(style.getHeight()+4) / 2
																+ ")")
										.style("opacity", '0.5')
										.style("fill", 'red');
									}

									session.setMappingDataType(mainSession.getMappingDataType());
									session.setMapped(mainSession.isMapped());
								}
							}
						});
				});
			
			session.setActiveMapping(mainSession.getActiveMapping().valueOf());
			session.resetColorMapping();
			mainSession.getColorMappingsSet().forEach(function(colorMap){
				session.addColorMapping(colorMap.getName().valueOf(), colorMap.getValue().valueOf());
			});

			var force = session.getForce();
			force.stop(); 

			var scale = metExploreD3.getScaleById(panel);
    		metExploreD3.GraphLink.tick(panel, scale);
			metExploreD3.GraphNode.tick(panel);
		}
	},

	/*******************************************
    * Permit to get x compared graph scaled of x main graph
    * @param {} x : The panel to scale
    * @param {} panel : The new panel
    */
    scaledX : function(x, panel) {
		var sessionsStore = metExploreD3.getSessionsSet();
		var xScaled;
		if(panel == "viz"){
			var panelComp;
			for (var key in sessions) {						
				if(sessions[key].getId()=="viz"){
					panelComp = sessions[key].getId();
				}
			}

			var wComp = parseInt(d3.select("#"+panelComp).select("#D3viz")
					.style("width"));

			var wViz = parseInt(d3.select("#viz").select("#D3viz")
					.style("width"));

			xScaled = (x * wComp) / wViz;
					
		}
		else
		{
			var panelComp;
			for (var key in sessions) {						
				if(sessions[key].getId()=="viz"){
					panelComp = sessions[key].getId();
				}
			}

			var wComp = parseInt(d3.select("#"+panel).select("#D3viz")
					.style("width"));

			var wViz = parseInt(d3.select("#viz").select("#D3viz")
					.style("width"));

			xScaled = (x * wViz) / wComp;
		}
		return xScaled;
	},
	
	/*******************************************
    * Permit to get y compared graph scaled of y main graph
    * @param {} y : The panel to scale
    * @param {} panel : The new panel
    */
    scaledY : function(y, panel) {
		var sessionsStore = metExploreD3.getSessionsSet();
		var yScaled;

		if(panel == "viz"){
			var panelComp;
			
			for (var key in sessions) {						
				if(sessions[key].getId()=="viz"){
					panelComp = sessions[key].getId();
				}
			}

			var hComp = parseInt(d3.select("#"+panelComp).select("#D3viz")
					.style("height"));

			var hViz = parseInt(d3.select("#viz").select("#D3viz")
					.style("height"));

			yScaled = (y * hComp) / hViz;
					
		}
		else
		{
			var panelComp;

			for (var key in sessions) {						
				if(sessions[key].getId()=="viz"){
					panelComp = sessions[key].getId();
				}
			}

			var hComp = parseInt(d3.select("#"+panel).select("#D3viz")
					.style("height"));

			var hViz = parseInt(d3.select("#viz").select("#D3viz")
					.style("height"));

			yScaled = (y * hViz) / hComp;
		}
		return Scaled;
	},
	
	

	/*******************************************
    * Add link in visualization
    * @param {} identifier : Id of this link
    * @param {} source : Source of this link
    * @param {} target : Target of this link
    * @param {} interaction : Interaction beetween nodes of this link
    * @param {} reversible : Reversibility of link
    * @param {} panel : The panel where is the new link
    */
    addLinkInDrawing:function(identifier,source,target,interaction,reversible,panel){
		var session = _metExploreViz.getSessionById(panel);
		var networkData = session.getD3Data();
		networkData.addLink(identifier,source,target,interaction,reversible);
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var linkStyle = metExploreD3.getLinkStyle();
		var force = session.getForce();

		var flux = _metExploreViz.getSessionById(panel).getMappingDataType()=="Flux";

		var map = {};

		if(flux){
			d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll("path.link")
				.filter(function(link){
					if(source.getBiologicalType()=="metabolite"){
						return(link.getSource().getId()==source.getIdentifier() || link.getSource().getId()==target.getId())
							&&
							(link.getTarget().getId()==source.getIdentifier() || link.getTarget().getId()==target.getId());
					}
					else
					{
						return(link.getSource().getId()==source.getId() || link.getSource().getId()==target.getIdentifier())
							&&
							(link.getTarget().getId()==source.getId() || link.getTarget().getId()==target.getIdentifier());
					}
				})
				.each(function(link){
					var idReaction;
					if(source.getBiologicalType()=="reaction"){
						idReaction = source.getId();
					}
					else
					{
						idReaction = target.getId();
					}

					var idLinkDOM;
					if (this.id=='linkRev') 
						idLinkDOM = "linkRev";
					else 
						idLinkDOM = "link"; 

					if(map[idReaction]==undefined) map[idReaction]={};

					map[idReaction][idLinkDOM]=
					{
						fill:d3.select(this).style("fill"), 
						strokeDasharray:d3.select(this).style("stroke-dasharray")
					};
				});			

			var divs=d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll("path.link")
			.data(force.links(), function(d) { return d.source.id + "-" + d.target.id;})
			.enter()
			.insert("svg:g",":first-child");

			divs.each(function(link){
				
				d3.select(this)
					.filter(function(link){
						var idReaction;
						if(source.getBiologicalType()=="reaction"){
							idReaction = source.getId();
						}
						else
						{
							idReaction = target.getId();
						}

						return map[idReaction].link!=undefined;
					})
					.append("svg:path")
					.attr("class", String)
					.attr("d", function(link){return metExploreD3.GraphLink.funcPathForFlux(link, panel, this.id);})
					.attr("class", "link")
					.attr("fill-rule", "evenodd")
					.style("stroke",linkStyle.getStrokeColor())
					.style("stroke-width",0.5)
					.style('opacity', 0.1)
					.style('stroke-dasharray', function(link){
						var idReaction;
						if(source.getBiologicalType()=="reaction"){
							idReaction = source.getId();
						}
						else
						{
							idReaction = target.getId();
						}

						return map[idReaction].link.strokeDasharray;
					})
					.style('fill', function(link){
						var idReaction;
						if(source.getBiologicalType()=="reaction"){
							idReaction = source.getId();
						}
						else
						{
							idReaction = target.getId();
						}

						return map[idReaction].link.fill;
					})
					.on("mouseover", function(d)
					 {		
						var reaction, metabolite, source, target;
						if(d.getSource().getBiologicalType()=="reaction"){
							reaction=d.getSource();
							metabolite=d.getTarget();
						}
						else
						{
							reaction=d.getTarget();
							metabolite=d.getSource();
						}
						
						source = d.getSource();
						target = d.getTarget();
						
						var mappingName = _metExploreViz.getSessionById("viz").getActiveMapping();
						var mapping = _metExploreViz.getMappingByName(mappingName);
						var conditions = mapping.getConditions();	
						var mapNode = reaction.getMappingDataByNameAndCond(mappingName, conditions[0]);
						if(mapNode != null){
							var flux = mapNode.getMapValue();
							if(flux<0){
								target = d.getSource();
								source = d.getTarget();
							}
						}
						
						if(!document.getElementById("tooltip2").classList.contains("fixed"))
						{
							var content = 
							"Name: " + d.id 
							+"<br/><b>Source:</b> " + source.getName() 
							+"<br/><b>Target:</b> " + target.getName() +
							((flux!=undefined) ? "<br/>Flux: " + Math.abs(flux) : "" );
						
							content+='<br/>';

					   		document.getElementById("tooltip2").innerHTML = content;
					   		document.getElementById("tooltip2").classList.remove("hide");
						}
					 })
					.on("mouseout", function(d)
					 {
						 document.getElementById("tooltip2").classList.add("hide");
					 });
			

			
				d3.select(this)
					.filter(function(link){
						var idReaction;
						if(source.getBiologicalType()=="reaction"){
							idReaction = source.getId();
						}
						else
						{
							idReaction = target.getId();
						}
						return map[idReaction].linkRev!=undefined;
					})
					.append("svg:path")
					.attr("class", String)
					.attr("id", "linkRev")
					.attr("d", function(link){return metExploreD3.GraphLink.funcPathForFlux(link, panel, this.id);})
					.attr("class", "link")
					.attr("fill-rule", "evenodd")
					.style("stroke",linkStyle.getStrokeColor())
					.style("stroke-width",0.5)
					.style('opacity', 0.1)
					.style('stroke-dasharray', function(link){
						var idReaction;
						if(source.getBiologicalType()=="reaction"){
							idReaction = source.getId();
						}
						else
						{
							idReaction = target.getId();
						}
						return map[idReaction].linkRev.strokeDasharray;
					})
					.style('fill', function(link){
						var idReaction;
						if(source.getBiologicalType()=="reaction"){
							idReaction = source.getId();
						}
						else
						{
							idReaction = target.getId();
						}
						return map[idReaction].linkRev.fill;
					})
					.on("mouseover", function(d)
					 {		
						var reaction, metabolite, source, target;
						if(d.getSource().getBiologicalType()=="reaction"){
							reaction=d.getSource();
							metabolite=d.getTarget();
						}
						else
						{
							reaction=d.getTarget();
							metabolite=d.getSource();
						}
						
						source = d.getSource();
						target = d.getTarget();

						var mappingName = _metExploreViz.getSessionById("viz").getActiveMapping();
						var mapping = _metExploreViz.getMappingByName(mappingName);
						var conditions = mapping.getConditions();	
						var mapNode = reaction.getMappingDataByNameAndCond(mappingName, conditions[1]);
						if(mapNode != null){
							var flux = mapNode.getMapValue();
							if(flux<0){
								target = d.getSource();
								source = d.getTarget();
							}
						}
							
						if(!document.getElementById("tooltip2").classList.contains("fixed"))
						{
							var content = 
							"Name: " + d.id 
							+"<br/><b>Source: </b>" + source.getName() 
							+"<br/><b>Target: </b>" + target.getName() +
							((flux!=undefined) ? "<br/>Flux: " + Math.abs(flux) : "" );
						
							content+='<br/>';

					   		document.getElementById("tooltip2").innerHTML = content;
					   		document.getElementById("tooltip2").classList.remove("hide");
						}
					})
					.on("mouseout", function(d)
					{
						document.getElementById("tooltip2").classList.add("hide");
					});	
			
			});
		}
		else
		{
			link=d3.select("#"+panel).select("#graphComponent").selectAll("path.link")
				.data(force.links(), function(d) { return d.source.id + "-" + d.target.id;})
				.enter()
				.insert("path",":first-child")
	        	.attr("class", String)
				.attr("d", function(link){return metExploreD3.GraphLink.funcPath4(link, panel);})
				.attr("class", "link")
				.attr("fill-rule", "evenodd")
				.attr("fill", function (d) {
					if (d.interaction=="out")
					 	return linkStyle.getMarkerOutColor();
					else
						return linkStyle.getMarkerInColor(); 
				})
				.style("stroke",linkStyle.getStrokeColor())
				.style("stroke-width",0.5)
	           .style("opacity",0.5)
	           .attr("x1", source.x)
	           .attr("y1", source.y)
	           .attr("x2", target.x)
	           .attr("y2", target.y);
		}
        
	},

	/*******************************************
    * identifier parameter is used if there is a new parameter to add.
    * @param {} panel : The panel to unlink
    * @param {} panel : The panel to unlink
    * @param {} panel : The panel to unlink
    * @returns {} newNode : The created node
    */
    addMetaboliteInDrawing: function(theNode, theNodeId, reactionId, panel){

    	var identifier = theNodeId+"-"+reactionId;
		var session = _metExploreViz.getSessionById(panel);
		var networkData = session.getD3Data();
		var force = session.getForce();
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var generalStyle = metExploreD3.getGeneralStyle();

		/***************************/
		// Var which permit to drag
		/***************************/
		var node_drag = d3.behavior.drag()
			.on("dragstart",_MyThisGraphNode.dragstart)
			.on("drag",_MyThisGraphNode.dragmove)
			.on("dragend", _MyThisGraphNode.dragend);
		
		var scale = metExploreD3.getScaleById(panel);

        metExploreD3.fireEventParentWebSite("sideCompound", theNode);

		//create the node in the data structure
		var newNode=networkData.addNode(
			theNode.getName(),
			theNode.getCompartment(),
			theNode.getDbIdentifier(),
			identifier,
			theNode.getReactionReversibility(),
			theNode.getBiologicalType(),
			false,
			theNode.getLabelVisible(),
			theNode.getSvg(),
			theNode.getSvgWidth(),
			theNode.getSvgHeight(),
			theNode.getIsSideCompound(), 
			undefined, 
			true, 
			theNodeId,
			networkData.getNodeById(reactionId).getPathways());

		//newNode.index = networkData.getNodes().indexOf(newNode);

		if(theNode.getMappingDatasLength()!=0){
			theNode.getMappingDatas().forEach(function(mapping){
				networkData.getNodeById(identifier).addMappingData(new MappingData(theNode, mapping.getMappingName(), mapping.getConditionName(), mapping.getMapValue()));
			});
		}
		
		var node = d3.select("#"+panel)
				.select("#D3viz")
				.select("#graphComponent")
				.selectAll("g.node");
		
		var isMapped = false;
		var oldNode = node
			.filter(function(d){
				return d.getId()==theNodeId;
			});

		oldNode.each(function(){ isMapped = this.getAttribute("mapped"); });

		//Add it to the force
		node = node.data(force.nodes(), function(d) { return d.getId(); });
		
		//Node drawing
		node.enter()
			.append("svg:g").attr("class", "node")
			.attr("duplicated",function(node){
				return "true";
			})//to avoid duplicating again
			.call(node_drag)
			.style("fill", "white");

	    // For each metabolite we append a division of the class "rect" with the metabolite style by default or create by the user
		node.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
			.filter(function(d) { return d.getId() == identifier; })
			.style("stroke-opacity",0.5)
			.addNodeForm(
				metaboliteStyle.getWidth()/2,
				metaboliteStyle.getHeight()/2,
				metaboliteStyle.getRX()/2,
				metaboliteStyle.getRY()/2,
				metaboliteStyle.getStrokeColor(),
				metaboliteStyle.getStrokeWidth()/2
			);

		node.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
			.filter(function(d) { return d.getId() == identifier; })
			.on("mouseenter", function(d) { 
					var nodes = d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll("g.node");
					d3.select(this)
						.each(function(node){
							var last = nodes[0][nodes.size()-1];
							this.parentNode.insertBefore(this, last);
						})
						.attr("transform", "translate("+d.x+", "+d.y+") scale(2)");
			})
			.on("mouseover", function(d) { 

				d.fixed = true;
				
				if(d.getBiologicalType()=="reaction"){
					d3.select("#"+panel).select("#D3viz").select("#graphComponent")
						.selectAll("path.link")
						.filter(function(link){return d.getId()==link.getSource().getId();})
						.style("stroke", "green"); 	
					 
					d3.select("#"+panel).select("#D3viz").select("#graphComponent")
						.selectAll("path.link")
						.filter(function(link){return d.getId()==link.getTarget().getId();})
						.style("stroke", "red"); 	
				}
				else
				{
					d3.select("#"+panel).select("#D3viz").select("#graphComponent")
						.selectAll("path.link")
						.filter(function(link){return d.getId()==link.getSource().getId();})
						.style("stroke", "red"); 	
					 
					d3.select("#"+panel).select("#D3viz").select("#graphComponent")
						.selectAll("path.link")
						.filter(function(link){return d.getId()==link.getTarget().getId();})
						.style("stroke", "green"); 
				}
				 
				var xScale=scale.getXScale();
				var yScale=scale.getYScale();
				
				if(!document.getElementById("tooltip2").classList.contains("fixed"))
				{
					var content = 
						"<b>Name:</b> " + d.getName() 
						+"<br/><b>Biological type:</b> " + d.getBiologicalType() +
						((d.getCompartment()!=undefined) ? "<br/><b>Compartment:</b> " + d.getCompartment(): "" )+
						((d.getDbIdentifier()!=undefined) ? "<br/><b>Database identifier:</b> " + d.getDbIdentifier() : "" )+
						((d.getEC()!=undefined) ? "<br/><b>EC number:</b> " + d.getEC() : "" )+
						((d.getReactionReversibility()!=undefined) ? "<br/><b>Reaction reversibility:</b> " + d.getReactionReversibility() : "" )+
						((d.getIsSideCompound()!=undefined) ? "<br/><b>SideCompound:</b> " + d.getIsSideCompound() : "" )+
						((d.getMappingDatasLength()!=0) ? ((d.getMappingDatasLength()==1) ? "<br/><b>Mapping:</b><br/><table style='width:100%; margin-left: 30px; padding-right: 30px;'>" : "<br/><b>Mappings:</b><br/><table style='width:100%; margin-left: 30px; padding-right: 30px;'>"): "");

	    			d.getMappingDatas().forEach(function(map){
	    				content+="<tr><td>" + map.getMappingName() +"</td><td>"+ map.getConditionName() +"</td><td>"+ map.getMapValue() +"</td></tr>";
	    			});

	    			content+="</table>";
	    			
	    			if(d.getSvg()!=undefined  && d.getSvg()!="undefined" && d.getSvg()!=""){
	    				content+='<br/><img src="resources/images/structure_metabolite/'+d.getSvg()+'"/>';
	    			}

			   		document.getElementById("tooltip2").innerHTML = content;
			   		document.getElementById("tooltip2").classList.remove("hide");
				}

			})
	        .on("mouseleave", function(d) {  
				d3.select(this)
					.attr("transform", "translate("+d.x+", "+d.y+") scale(1)");
				if(!d.isSelected())
					d.fixed = false;
				var linkStyle = metExploreD3.getLinkStyle();  

		   		document.getElementById("tooltip2").classList.add("hide");

	    		d3.select("#"+panel).select("#D3viz").select("#graphComponent")
					.selectAll("path.link")
					.filter(function(link){return d.getId()==link.getSource().getId() || d.getId()==link.getTarget().getId();})
					.style("stroke",linkStyle.getStrokeColor());

				if(d.getBiologicalType()=="reaction"){
					d3.select(this).selectAll("rect").selectAll(".reaction, .fontSelected").transition()
						.duration(750)
	                    .attr("width", reactionStyle.getWidth())
	                    .attr("height", reactionStyle.getHeight())
	                    .attr( "transform", "translate(-" + reactionStyle.getWidth() / 2 + ",-" + reactionStyle.getHeight() / 2 + ")");
				}
				else
				{
					
					d3.select(this).selectAll("rect").selectAll(".reaction, .fontSelected").transition()
						 .duration(750)
	                     .attr("width", metaboliteStyle.getWidth())
	                     .attr("height", metaboliteStyle.getHeight())
						 .attr("transform", "translate(-" + metaboliteStyle.getWidth() / 2 + ",-"
												+ metaboliteStyle.getHeight() / 2
												+ ")");
				}
	        });

			var selection = node.filter(function(d) { return d.getId() == identifier; });
 			
	 		metExploreD3.GraphNode.colorStoreByCompartment(selection);
			
			if (networkData.getNodes().length < generalStyle.getReactionThreshold() || !generalStyle.isDisplayedLabelsForOpt()) {
				var minDim = Math.min(metaboliteStyle.getWidth()/2,metaboliteStyle.getHeight()/2);
				// We define the text for a metabolie WITHOUT the coresponding SVG image 
				node
					.filter(function(d) { return d.getId() == identifier; })
					.filter(function(d) { return d.getLabelVisible() == true; })
					.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
					.filter(function(d) { return d.getSvg() == "undefined" || d.getSvg() == undefined || d.getSvg() == ""; })
					.append("svg:text")
			        .attr("fill", "black")
			        .attr("class", function(d) { return d.getBiologicalType(); })
					.text(function(d) { return $("<div/>").html(d.getName()).text(); })
					.style(
						"font-size",
						function(d) {
							return Math.min((2 * minDim/2), (2 * minDim/2 - 3) / this.getComputedTextLength()
									* 10)
									+ "px";
						})
					.attr("dy", ".3em")
					.style("pointer-events", 'none')
					.style("opacity",0.5);

				// We define the text for a metabolie WITH the coresponding SVG image 
				// Text definition
				node
					.filter(function(d) { return d.getId() == identifier })
					.filter(function(d) {
							return d.getLabelVisible() == true;
						})
					.filter(function(d) {
							return d.getBiologicalType() == 'metabolite';
						})
					.filter(function(d) {
							return d.getSvg() != "undefined" && d.getSvg() != undefined && d.getSvg() != "";
						})
					.append("svg:text")
			        .attr("fill", "black")
					.attr("class", function(d) {
							return d.getBiologicalType();
						})
						// .text(function(d) { return d.getName(); })
					.text(function(d) {
							return $("<div/>").html(d.getName()).text();
						})
					.style(
								"font-size",
								function(d) {
									return Math.min(
													(minDim) / 2,
													((minDim - 3)/ this.getComputedTextLength() * 10) / 2
												)+ "px";
								})
					.attr("dy", ".3em")
					.style("pointer-events", 'none')
					.attr("y",+(3 / 4 * (minDim/2) ));

				// Image definition
				node
					.filter(function(d) { return d.getId() == identifier })
					.filter(
							function(d) {
								return (d.getBiologicalType() == 'metabolite' && d.getSvg() != "undefined" && d.getSvg() != undefined && d.getSvg() != "");
							})
					.append("svg")
					.attr(
							"viewBox",
							function(d) {
								return "0 0 " + minDim
										+ " " + minDim;
							})
					.attr("width", minDim *8/10 + "px")
					.attr("height", minDim *8/10+ "px")
					.attr("x", (-minDim/2)+(minDim*1/10))
					.attr("preserveAspectRatio", "xMinYMin")
					.attr("y", (-minDim/2)+(minDim*1/10))
					.attr("class", "structure_metabolite")
					.append("image")
					.style("opacity",0.5)
					.attr(
							"xlink:href",
							function(d) {
								return "resources/images/structure_metabolite/"
										+ d.getSvg();
							}).attr("width", "100%").attr(
							"height", "100%");

				// We define the text for a reaction
				node
					.filter(function(d) { return d.getId() == identifier; })
					.filter(function(d) {
						return d.getLabelVisible() == true;
					})
					.filter(function(d) {
						return d.getBiologicalType() == 'reaction';
					})
					.append("svg:text")
		            .attr("fill", "black")
					.attr("class", function(d) {
						return d.getBiologicalType();
					})
					// .text(function(d) { return d.getName(); })
					.text(function(d) {
						return $("<div/>").html(d.getName()).text();
					})
					.style(
							"font-size",
							function(d) {
								return Math.min(2 * minDim,(minDim - 2)/ this.getComputedTextLength()* 10)+ "px";
							}).attr("dy", ".3em");
			}

			if(isMapped!=undefined && isMapped!=false && isMapped!="false"){
				if(isMapped==true || isMapped=="true"){
					node
						.filter(function(d) { return d.getId() == identifier; })
						.attr("mapped","true")
						.insert("rect", ":first-child")
						.attr("class", "stroke")
						.attr("width", metaboliteStyle.getWidth()/2+10)
						.attr("height", metaboliteStyle.getHeight()/2+10)
						.attr("rx", metaboliteStyle.getRX()/2+5)
						.attr("ry",metaboliteStyle.getRY()/2+5)
						.attr("transform", "translate(-" + parseInt(metaboliteStyle.getWidth()/2+10) / 2 + ",-"
												+ parseInt(metaboliteStyle.getWidth()/2+10) / 2
												+ ")")
						.style("opacity", '0.5')
						.style("fill", 'red');
				}
				else
				{	

					var color = isMapped;
					node
						.filter(function(d) { return d.getId() == identifier; })
						.attr("mapped",color)
						.style("fill", color)	
				}
			}

			var originalX = 100;
			var originalY = 100;

			node.filter(function(d) { return d.getBiologicalType() == 'reaction'; })
				.filter(function(d) { return d.getId() == reactionId; })
				.each(function(reactNode){
					var dX =  reactNode.x - theNode.x;
					var dY =  reactNode.y - theNode.y;
					
					var d = Math.sqrt(Math.pow(dX, 2) + Math.pow(dY, 2)); 
					originalX = reactNode.x - (40 * dX)/d;
					originalY = reactNode.y - (40 * dY)/d;
				});

			node.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
				.filter(function(d) { return d.getId() == identifier; })
				.attr("transform", function(d) {
					return "translate(" + originalX + "," + originalY + ")";
				})
				.each(function(node){
					node.px = originalX;
					node.py = originalY; 
					node.x = originalX;
					node.y = originalY;

				
			});

			// add the node from group to draw convex hulls
			var component=undefined;
			session.groups.forEach(function(group){
				if(component=="compartment"){
					if(group.key==newNode.getCompartment())
						group.values.push(newNode);
				}
				else
				{
					var pathFound = newNode.getPathways().find(function(pathw)
		                {
		                    return group.key==pathw;
		                }
	                );
					if(pathFound!=undefined)
						group.values.push(newNode);
				}
			});

			if (metExploreD3.GraphNetwork.isAnimated(panel)==true || metExploreD3.GraphNetwork.isAnimated(panel)=="true") {
				force.start();
			}
			return newNode;
	},

	/*******************************************
    * Duplicate a node
    * Each time the metabolite occurs in a reaction we create a new node and connect it only to the reaction
    * @param {} theNode : The node to duplicate
    * @param {} panel : The panel to unlink
    */
    duplicateANode : function(theNode, panel) {
		var session = _metExploreViz.getSessionById(panel);
		session.addDuplicatedNode(theNode.getId());

		var force = session.getForce();
		var networkData = session.getD3Data();
		var reactionsConsumingNode,reactionsProducingNode;
		reactionsProducingNode = [];
		reactionsConsumingNode = [];
		var vis = d3.select("#"+panel).select("#D3viz");
		/***************************/
		// Var which permit to drag
		/***************************/
		var node_drag = d3.behavior.drag()
			.on("dragstart",function(d){
				_MyThisGraphNode.dragstart(d);
			})
			.on("drag",function(d){
					_MyThisGraphNode.dragmove(d);
			}).on("dragend", _MyThisGraphNode.dragend);
		var scale = metExploreD3.getScaleById(panel);

		//Create the list of nodes to duplicate.
		//Two tables are created, one when side compounds are substrates and one when they are products
         vis.selectAll("path.link")
         	.filter(function(link){
				return link.getInteraction()!="hiddenForce";
			})
			.each(function(d) {
				var source = d.source;
				var target = d.target;
				if(source==theNode)
				{
					if(reactionsConsumingNode.indexOf(target)==-1)
						reactionsConsumingNode.push(target);
				}
				else
				{
					if(target==theNode)
					{
						if(reactionsProducingNode.indexOf(source)==-1)
							reactionsProducingNode.push(source);
					}
				}
			})

		reactionsConsumingNode.forEach(function(reaction){
			var newID=theNode.getId()+"-"+reaction.getId();
			//add the node to the data and viz
			var newNode=metExploreD3.GraphNetwork.addMetaboliteInDrawing(theNode,theNode.getId(),reaction.getId(),panel);

			//add the link from theNode to the reaction
			metExploreD3.GraphNetwork.addLinkInDrawing(newID+"-"+reaction.getId(),newNode,reaction,"in",reaction.getReactionReversibility(),panel);

		});

		reactionsProducingNode.forEach(function(reaction){
			var newID=theNode.getId()+"-"+reaction.getId();
			//add the link from the reaction to theNode
			var newNode=metExploreD3.GraphNetwork.addMetaboliteInDrawing(theNode,theNode.getId(), reaction.getId(),panel);
			
			metExploreD3.GraphNetwork.addLinkInDrawing(reaction.getId()+"-"+newID,reaction,newNode,"out",reaction.getReactionReversibility(),panel);
			
		});

		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var reactionStyle = metExploreD3.getReactionStyle();

		var maxDimRea = Math.max(reactionStyle.getWidth(),reactionStyle.getHeight());
		var maxDimMet = Math.max(metaboliteStyle.getWidth(),metaboliteStyle.getHeight());
		var maxDim = Math.max(maxDimRea, maxDimMet);
		
		
		var linkStyle = metExploreD3.getLinkStyle();  
		force.linkDistance(function(link){
			if(link.getSource().getIsSideCompound() || link.getTarget().getIsSideCompound())
				return linkStyle.getSize()/2+maxDim;
			else
				return linkStyle.getSize()+maxDim;
		});
	}, 	
	

	/*******************************************
    * Duplicate side compounds
    * @param {} panel : The panel where the SC must be duplicated
    */
    duplicateSideCompounds : function(panel, func){
		
		if(panel==undefined) panel="viz";

		var vis = d3.select("#"+panel).select("#D3viz");
		var sideCompounds = [];
				
		var myMask = metExploreD3.createLoadMask("Duplicate in progress...", panel);
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);

			metExploreD3.deferFunction(function() {			         
				vis.selectAll("g.node")
					.filter(function(d) {
						return d.getIsSideCompound() && d.getBiologicalType()=="metabolite";
					})
					.filter(function(d){
						if(this.getAttribute("duplicated")==undefined) return true;
						else return !this.getAttribute("duplicated");
					})
					.each(function(node){
						metExploreD3.GraphNetwork.duplicateSideCompound(node, panel);
						sideCompounds.push(node);
					});

				metExploreD3.hideMask(myMask);
				sideCompounds.forEach(function(sideC){
					metExploreD3.GraphNetwork.removeANode(sideC, panel);
				});

				if(_metExploreViz.isLinkedByTypeOfMetabolite()){
					metExploreD3.GraphLink.linkTypeOfMetabolite();
				}
			
				var sessions = _metExploreViz.getSessionsSet();
				var aSession = _metExploreViz.getSessionById(panel);
					
				if (func!=undefined) {func()};

				if(panel!='viz' && aSession.isLinked()){
					metExploreD3.fireEvent('graphPanel', 'afterDuplicate');
				}
				else
				{
					for (var key in sessions) {						
						if(sessions[key].isLinked() && sessions[key].getId()!='viz')
							metExploreD3.deferFunction(function() {			         
									
								sessions[key].setLinked(false);
								metExploreD3.GraphNetwork.looksLinked();

								var force = sessions[key].getForce();
								// force.start();

								var mainSession = _metExploreViz.getSessionById('viz');
								if(sessions[key]!=undefined)  
								{
									if(mainSession.getDuplicatedNodesCount()>0){
									
										var force = sessions[key].getForce();
										sessions[key].setLinked(true);
										mainSession.setLinked(true);
										
										metExploreD3.GraphNetwork.duplicateSideCompounds(sessions[key].getId());
										
										metExploreD3.GraphNetwork.looksLinked();
										if(sessions[key].isLinked()){
											metExploreD3.GraphNetwork.graphAlignment(sessions[key].getId());
										}
									}
									else
									{
										metExploreD3.GraphNetwork.graphAlignment(sessions[key].getId());
										sessions[key].setLinked(true);
										mainSession.setLinked(true);
									}
								}
							}, 100);
					};
				}
			}, 1);
		}
		metExploreD3.GraphNetwork.initCentroids();
	},
	
	/*******************************************
    * Duplicate side compounds with an ids array  
    * @param {} panel : The panel where the SC must be duplicated
    */
    duplicateSideCompoundsById : function(ids, panel){
		
		var vis = d3.select("#"+panel).select("#D3viz");
		var sideCompounds = [];
				
		var myMask = metExploreD3.createLoadMask("Duplicate in progress...", panel);
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);

			metExploreD3.deferFunction(function() {			         
				vis.selectAll("g.node")
					.filter(function(d) {
						return ids.indexOf(d.getId())!=-1;
					})
					.filter(function(d){
						if(this.getAttribute("duplicated")==undefined) return true;
						else return !this.getAttribute("duplicated");
					})
					.each(function(node){
						metExploreD3.GraphNetwork.duplicateSideCompound(node, panel);
						sideCompounds.push(node);
					});

 
				metExploreD3.hideMask(myMask);
				sideCompounds.forEach(function(sideC){
					metExploreD3.GraphNetwork.removeANode(sideC, panel);
				});	

				if(_metExploreViz.isLinkedByTypeOfMetabolite()){
					metExploreD3.GraphLink.linkTypeOfMetabolite();
				}

			}, 0);
		}
		metExploreD3.GraphNetwork.initCentroids();
	},

	/*******************************************
    * Duplicate side compounds which is selected
    * @param {} panel : The panel where the SC must be duplicated
    */
    duplicateSideCompoundsSelected : function(panel) {
		var vis = d3.select("#"+panel).select("#D3viz");
		var sideCompounds = [];
		
		var myMask = metExploreD3.createLoadMask("Duplicate in progress...", panel);
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);

			metExploreD3.deferFunction(function() {			         
				vis.selectAll("g.node")
							.filter(function(d) {
								return d.isSelected() && d.getBiologicalType()=="metabolite";
							})
							.filter(function(d){
								if(this.getAttribute("duplicated")==undefined) return true;
								else return !this.getAttribute("duplicated");
							})
							.each(function(node){
								if(metExploreD3.getMetabolitesSet()!=undefined){
									var theMeta = metExploreD3.getMetaboliteById(metExploreD3.getMetabolitesSet(), node.getId());
									theMeta.set("sideCompound", true);
								}	
								node.setIsSideCompound(true);	
								metExploreD3.GraphNetwork.duplicateSideCompound(node, panel);
								sideCompounds.push(node);
							});


				metExploreD3.hideMask(myMask);
				sideCompounds.forEach(function(sideC){
					metExploreD3.GraphNetwork.removeANode(sideC, panel);
				});
			
				if(_metExploreViz.isLinkedByTypeOfMetabolite()){
					metExploreD3.GraphLink.linkTypeOfMetabolite();
				}

				var sessions = _metExploreViz.getSessionsSet();
				var aSession = _metExploreViz.getSessionById(panel);
				
				if(panel!='viz' && aSession.isLinked()){
					metExploreD3.fireEvent('graphPanel', 'afterDuplicate');
				}
				else
				{
					for (var key in sessions) {						
						if(sessions[key].isLinked() && sessions[key].getId()!='viz')
							metExploreD3.deferFunction(function() {			         
									
								sessions[key].setLinked(false);
								metExploreD3.GraphNetwork.looksLinked();

								var force = sessions[key].getForce();
								// force.start();

								var mainSession = _metExploreViz.getSessionById('viz');
								if(sessions[key]!=undefined)  
								{
									if(mainSession.getDuplicatedNodesCount()>0){
									
										var force = sessions[key].getForce();
										sessions[key].setLinked(true);
										mainSession.setLinked(true);
										
										metExploreD3.GraphNetwork.duplicateSideCompoundsSelected(sessions[key].getId());
										
										metExploreD3.GraphNetwork.looksLinked();
										if(sessions[key].isLinked()){
											metExploreD3.GraphNetwork.graphAlignment(sessions[key].getId());
										}
									}
									else
									{
										metExploreD3.GraphNetwork.graphAlignment(sessions[key].getId());
										sessions[key].setLinked(true);
										mainSession.setLinked(true);
									}
								}
							}, 100);
					};
				}
			}, 0);
		}
		metExploreD3.GraphNetwork.initCentroids();
	},

	/*******************************************
    * Duplicate a side compound which is selected
    * @param {} panel : The panel where the SC must be duplicated
    */
    duplicateASideCompoundSelected : function(theNode, panel) {
				
		var vis = d3.select("#"+panel).select("#D3viz");
		var sideCompounds = [];
		
		var myMask = metExploreD3.createLoadMask("Duplicate in progress...", panel);
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);

	        
			metExploreD3.deferFunction(function() {			         
				vis.selectAll("g.node")
							.filter(function(d) {
								if(theNode.querySelector("rect.metabolite")!=null)
									return d.getId()==theNode.querySelector("rect.metabolite").id && d.isSelected() && d.getBiologicalType()=="metabolite";
								else
									return false;
							})
							.filter(function(d){
								if(this.getAttribute("duplicated")==undefined) return true;
								else return !this.getAttribute("duplicated");
							})
							.each(function(node){
								if(metExploreD3.getMetabolitesSet()!=undefined){
									var theMeta = metExploreD3.getMetaboliteById(metExploreD3.getMetabolitesSet(), node.getId());
									theMeta.set("sideCompound", true);
								}
								node.setIsSideCompound(true);
								metExploreD3.GraphNetwork.duplicateSideCompound(node, panel);
								sideCompounds.push(node);
							});


				metExploreD3.hideMask(myMask);
				sideCompounds.forEach(function(sideC){
					metExploreD3.GraphNetwork.removeANode(sideC, panel);
				});
				
				if(_metExploreViz.isLinkedByTypeOfMetabolite()){
					metExploreD3.GraphLink.linkTypeOfMetabolite();
				}

				var sessions = _metExploreViz.getSessionsSet();
				var aSession = _metExploreViz.getSessionById(panel);
				
				if(panel!='viz' && aSession.isLinked()){
					metExploreD3.fireEvent('graphPanel', 'afterDuplicate');
				}
				else
				{
					for (var key in sessions) {						
						if(sessions[key].isLinked() && sessions[key].getId()!='viz')
						{
							metExploreD3.deferFunction(function() {			         
									
								sessions[key].setLinked(false);
								metExploreD3.GraphNetwork.looksLinked();

								var force = sessions[key].getForce();
								// force.start();

								var mainSession = _metExploreViz.getSessionById('viz');
								if(sessions[key]!=undefined)  
								{
									if(mainSession.getDuplicatedNodesCount()>0){

										var force = sessions[key].getForce();
										sessions[key].setLinked(true);
										mainSession.setLinked(true);
										
										metExploreD3.GraphNetwork.duplicateASideCompoundSelected(theNode, sessions[key].getId());
										
										metExploreD3.GraphNetwork.looksLinked();
										if(sessions[key].isLinked()){
											metExploreD3.GraphNetwork.graphAlignment(sessions[key].getId());
										}
									}
									else
									{
										metExploreD3.GraphNetwork.graphAlignment(sessions[key].getId());
										sessions[key].setLinked(true);
										mainSession.setLinked(true);
									}
								}
							}, 100);
						}
					}
				}
			}, 0);
		}
		metExploreD3.GraphNetwork.initCentroids();
	},

	/*******************************************
    * Duplication of side compounds 
    * @param {} theNodeElement : node to duplicate 
    * @param {} panel :panel where node must be duplicated
    */
    duplicateSideCompound : function(theNodeElement, panel){
		var session = _metExploreViz.getSessionById(panel);

		var vis = d3.select("#"+panel).select("#D3viz");
		
		if(session!=undefined) 
		{
			// We stop the previous animation
			if(session.isLinked()){
				var session = _metExploreViz.getSessionById('viz');
				if(session!=undefined)
				{
					var force = session.getForce();
					if(force!=undefined)  
					{		
						if(metExploreD3.GraphNetwork.isAnimated("viz")== "true" || metExploreD3.GraphNetwork.isAnimated("viz")==true)
							force.resume();
					}	
				}
			}
			else
			{	
				
				var force = session.getForce();
				if(force!=undefined)  
				{
					if(metExploreD3.GraphNetwork.isAnimated(panel)== "true" || metExploreD3.GraphNetwork.isAnimated(panel)==true)
						force.resume();
											
				}
			}
		}
		metExploreD3.GraphNetwork.duplicateANode(theNodeElement, panel);

		
		if(session!=undefined)  
		{
			if(force!=undefined)  
			{		
				if(metExploreD3.GraphNetwork.isAnimated(panel)== "true" || metExploreD3.GraphNetwork.isAnimated(panel)==true)
					force.start();
			}	
		}
		metExploreD3.GraphNetwork.initCentroids();
	},

	/*******************************************
    * Remove selected nodes
    * @param {} panel : The panel where are selected nodes
    */
    removeSelectedNode : function(panel) {
		var session = _metExploreViz.getSessionById(panel);
		var force = session.getForce();
		var networkData = session.getD3Data();
		
		var myMask = metExploreD3.createLoadMask("Remove in process...", panel);
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);

	        // listMask.push(myMask);

	        metExploreD3.deferFunction(function() {

				var vis = d3.select("#"+panel).select("#D3viz");
				
				if(session!=undefined) 
				{
					// We stop the previous animation
					if(session.isLinked()){
						var session = _metExploreViz.getSessionById('viz');
						if(session!=undefined)
						{
							var force = session.getForce();
							if(force!=undefined)  
							{	
								if(metExploreD3.GraphNetwork.isAnimated("viz")=="true")
									force.stop();
							}	
						}
					}
					else
					{	
						
						var force = session.getForce();
						if(force!=undefined)  
						{
							if(metExploreD3.GraphNetwork.isAnimated(panel)=="true")
								force.stop();
													
						}
					}
				}
				vis.selectAll("g.node")
					.filter(function(d) {
						return d.isSelected();
					})
					.each(function(node){
						metExploreD3.GraphNetwork.removeANode(node, panel);
					});

/*		var session = _metExploreViz.getSessionById(panel);

var force = session.getForce();
var networkData = session.getD3Data();
var linksToRemove = [];
var vis = d3.select("#"+panel).select("#D3viz");

// Remove the node from group to draw convex hulls  
session.groups.forEach(function(group){
	if(group.key==theNode.getCompartment()){
		var index = group.values.indexOf(theNode);
		
		if(index!=-1)
			group.values.splice(index, 1);
	}

	theNode.getPathways().forEach(function(pathway){
		if(group.key==pathway){
			var index = group.values.indexOf(theNode);
			
			if(index!=-1)
				group.values.splice(index, 1);
		}
	}) 
});

vis.selectAll("path.link")
	.filter(function(d) {
		var source = d.source;
		var target = d.target;
		return (source==theNode || target==theNode);
	})
	.remove();

	var nodes = vis.selectAll("g.node");

	nodes
		.filter(function(d) {
			return theNode==d;
		})
		.transition().duration(1000).style("opacity", 0)
		.remove();

var selectedNodes = session.getSelectedNodes();
var index = selectedNodes.indexOf(theNode.getId());
if(index!=-1)
	selectedNodes.splice(index, 1);

setTimeout(
	function() {
		
		for (i = 0; i < networkData.getLinks().length; i++) {
			var d = networkData.getLink(i);
			var source = d.source;
			var target = d.target;

			if(source==theNode || target==theNode)
				linksToRemove.push(d);
		}
			
		// Remove the node from group to draw convex hulls  
		session.groups.forEach(function(group){
			if(group.key==theNode.getCompartment()){
				
				var index = group.values.indexOf(theNode);
				if(index!=-1)
					group.values.splice(index, 1);
				
				if(group.values.length==0){
				 	index = session.groups.indexOf(group);
					if(index!=-1){
						session.groups.splice(index, 1);
						d3.select("#"+panel).select("#D3viz")
							.select("path#"+group.key)
							.remove();
					}
				}
			}
			theNode.getPathways().forEach(function(pathway){
				if(group.key==pathway){
					var index = group.values.indexOf(theNode);
					if(index!=-1)
						group.values.splice(index, 1);
					
					if(group.values.length==0){
					 	index = session.groups.indexOf(group);
						if(index!=-1){
							session.groups.splice(index, 1);
							d3.select("#"+panel).select("#D3viz")
								.select("path#"+group.key)
								.remove();
						}
					}
				}
			}) 
		});

		var index = force.nodes().indexOf(theNode);
		if(index!=-1)
			force.nodes().splice(index, 1);
	

		for (i = 0; i < linksToRemove.length; i++) {
			var link = linksToRemove[i];
			var index = force.links().indexOf(link);

			if(index!=-1)
				force.links().splice(index, 1);
		}
	}
, 1);*/

            	metExploreD3.hideMask(myMask);

            	metExploreD3.GraphNetwork.removeIsolatedNode(panel);

				if(session!=undefined)  
				{
					if(force!=undefined)  
					{		
						if(metExploreD3.GraphNetwork.isAnimated(panel)=="true")
							force.start();
					}	
				}
       		 }, 1);
       	}		
       	metExploreD3.GraphNetwork.initCentroids();	
	},

	/*******************************************
    * Remove only clicked node
    * @param {} panel : The panel where are selected nodes
    */
    removeOnlyClickedNode : function(theNode, panel) {
		var session = _metExploreViz.getSessionById(panel);
		var force = session.getForce();
		var networkData = session.getD3Data();
	
		var myMask = metExploreD3.createLoadMask("Remove in process...", panel);
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);

	        // listMask.push(myMask);

	        metExploreD3.deferFunction(function() {

				var vis = d3.select("#"+panel).select("#D3viz");
				
				if(session!=undefined) 
				{
					// We stop the previous animation
					if(session.isLinked()){
						var session = metExploreD3.getSessionById(sessionsStore, 'viz');
						if(session!=undefined)
						{
							var force = session.getForce();
							if(force!=undefined)  
							{	
								if(metExploreD3.GraphNetwork.isAnimated("viz")=="true")
									force.resume();
							}	
						}
					}
					else
					{	
						
						var force = session.getForce();
						if(force!=undefined)  
						{
							if(metExploreD3.GraphNetwork.isAnimated(panel)=="true")
								force.resume();
													
						}
					}
				}
				metExploreD3.GraphNetwork.removeASelectedNode(theNode, panel);
				metExploreD3.GraphNetwork.removeIsolatedNode(panel);

				if(session!=undefined)  
				{
					if(force!=undefined)  
					{		
						if(metExploreD3.GraphNetwork.isAnimated(panel)=="true")
							force.start();
					}	
				}

            	metExploreD3.hideMask(myMask);
       		 }, 100);
       	}			
	},

	/*******************************************
    * Remove one selected node 
    * @param {} theNodeElement : node to remove
    * @param {} panel : The panel where are selected node
    */
    removeASelectedNode : function(theNodeElement, panel) {
		var session = _metExploreViz.getSessionById(panel);

		
		var myMask = metExploreD3.createLoadMask("Remove in process...", panel);
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);

	        
        	var vis = d3.select("#"+panel).select("#D3viz");
			
			if(session!=undefined) 
			{
				// We stop the previous animation
				if(session.isLinked()){
					var session = metExploreD3.getSessionById(sessionsStore, 'viz');
					if(session!=undefined)
					{
						var force = session.getForce();
						if(force!=undefined)  
						{	
							if(metExploreD3.GraphNetwork.isAnimated("viz")== "true")
								force.resume();
						}	
					}
				}
				else
				{	
					
					var force = session.getForce();
					if(force!=undefined)  
					{
						if(metExploreD3.GraphNetwork.isAnimated(panel)== "true")
							force.resume();
												
					}
				}
			}
			metExploreD3.GraphNetwork.removeANode(theNodeElement, panel);

			if(session!=undefined)  
			{
				if(force!=undefined)  
				{		
					if(metExploreD3.GraphNetwork.isAnimated("viz")== "true")
						force.start();
				}	
			}
	    	metExploreD3.hideMask(myMask);
	    }
	    metExploreD3.GraphNetwork.initCentroids();
	},

	/*******************************************
    * Remove a node
    * @param {} theNode : The node to remove
    * @param {} panel : The panel
    */
    removeANode : function(theNode, panel) {
		var session = _metExploreViz.getSessionById(panel);
		
		var force = session.getForce();
		var networkData = session.getD3Data();
		var linksToRemove = [];
		var vis = d3.select("#"+panel).select("#D3viz");
		
		vis.selectAll("path.link")
			.filter(function(d) {
				var source = d.source;
				var target = d.target;
				if(source==theNode || target==theNode) linksToRemove.push(d);
				return (source==theNode || target==theNode);
			})
			.remove();

		var nodes = vis.selectAll("g.node");

		nodes
			.filter(function(d) {
				return theNode==d;
			})
			.transition().duration(1000)
			.style("opacity", 0)
			.remove();
		
		setTimeout(
			function() {
				
				var selectedNodes = session.getSelectedNodes();
				var index = selectedNodes.indexOf(theNode.getId());
				if(index!=-1)
					selectedNodes.splice(index, 1);
				// for (i = 0; i < networkData.getLinks().length; i++) {
				// 	var d = networkData.getLink(i);
				// 	var source = d.source;
				// 	var target = d.target;

				// 	if(source==theNode || target==theNode)
				// 		linksToRemove.push(d);
				// }
					
				// Remove the node from group to draw convex hulls  
				session.groups.forEach(function(group){
					if(group.key==theNode.getCompartment()){
						
						var index = group.values.indexOf(theNode);
						if(index!=-1)
							group.values.splice(index, 1);
						
						if(group.values.length==0){
						 	index = session.groups.indexOf(group);
							if(index!=-1){
								session.groups.splice(index, 1);
								d3.select("#"+panel).select("#D3viz")
									.select("path#"+group.key)
									.remove();
							}
						}
					}
					theNode.getPathways().forEach(function(pathway){
						if(group.key==pathway){
							var index = group.values.indexOf(theNode);
							if(index!=-1)
								group.values.splice(index, 1);
							
							if(group.values.length==0){
							 	index = session.groups.indexOf(group);
								if(index!=-1){
									session.groups.splice(index, 1);
									d3.select("#"+panel).select("#D3viz")
										.select("path#"+group.key)
										.remove();
								}
							}
						}
					}) 
				});

				var index = force.nodes().indexOf(theNode);
				if(index!=-1)
					force.nodes().splice(index, 1);
			

				for (i = 0; i < linksToRemove.length; i++) {
					var link = linksToRemove[i];
					var index = force.links().indexOf(link);

					if(index!=-1)
						force.links().splice(index, 1);
				}
			}
		, 1);
		// metExploreD3.GraphNetwork.tick('viz');
	},
	
		/*******************************************
    * Remove node which is Isolated
    * @param {} panel : The panel
    */
 //    removeIsolatedNode : function(panel) {
	// 	var session = _metExploreViz.getSessionById(panel);
	// 	var force = session.getForce();
	// 	var networkData = session.getD3Data();
	// 	var nodesToRemove = [];
	// 	var vis = d3.select("#"+panel).select("#D3viz");

	// 	var nodes = vis.selectAll("g.node");
		
	// 	nodes.filter(function(node){
	// 		var haveALink=false;
	// 		vis.selectAll("path.link")
	// 			.each(function(link){
	// 				var src = link.source;
	// 				var tgt = link.target;
	// 				if(src.getId()==node.getId() || tgt.getId()==node.getId()){
	// 					haveALink=true;
	// 				}
	// 			});
	// 		if(!haveALink)
	// 			nodesToRemove.push(node);


	// 		return !haveALink;
	// 	})
	// 		.transition().duration(1000).style("opacity", 0)
	// 	.remove();
		
	// 	setTimeout(
	// 		function() {
				
	// 			for (i = 0; i < nodesToRemove.length; i++) {
	// 				var node = nodesToRemove[i];
					
	// 				// Remove the node from group to draw convex hulls  
	// 				session.groups.forEach(function(group){
	// 					if(group.key==node.getCompartment()){
							
	// 						var index = group.values.indexOf(node);
	// 						if(index!=-1)
	// 							group.values.splice(index, 1);
							
	// 						if(group.values.length==0){
	// 						 	index = session.groups.indexOf(group);
	// 							if(index!=-1){
	// 								session.groups.splice(index, 1);
	// 								d3.select("#"+panel).select("#D3viz")
	// 									.select("path#"+group.key)
	// 									.remove();
	// 							}
	// 						}
	// 					}
	// 					node.getPathways().forEach(function(pathway){
	// 						if(group.key==pathway){
	// 							var index = group.values.indexOf(node);
	// 							if(index!=-1)
	// 								group.values.splice(index, 1);
								
	// 							if(group.values.length==0){
	// 							 	index = session.groups.indexOf(group);
	// 								if(index!=-1){
	// 									session.groups.splice(index, 1);
	// 									d3.select("#"+panel).select("#D3viz")
	// 										.select("path#"+group.key)
	// 										.remove();
	// 								}
	// 							}
	// 						}
	// 					}) 
	// 				});

	// 				var index = force.nodes().indexOf(
	// 						node);
	// 				if(index!=-1)
	// 					force.nodes().splice(index, 1);
	// 			}

	// 			for (i = 0; i < nodesToRemove.length; i++) {
	// 				var node = nodesToRemove[i];
	// 				var index = force.nodes().indexOf(
	// 						node);
					
	// 				if(index!=-1)
	// 					force.nodes().splice(index, 1);
	// 			}				
	// 		}
	// 	, 10);
	// },
		/*******************************************
    * Remove node which is Isolated
    * @param {} panel : The panel
    */
    removeIsolatedNode : function(panel) {
		var session = _metExploreViz.getSessionById(panel);
		var force = session.getForce();
		var networkData = session.getD3Data();
		var nodesToRemove = [];
		var vis = d3.select("#"+panel).select("#D3viz");

		var arrayId = [];
		var nodes = networkData.getNodes().map(function(node){
			return node.getId();
		});

		var haveALink=false;
		vis.selectAll("path.link")
			.each(function(link){
				var src = link.source;
				var tgt = link.target;
				var indexSrc = nodes.indexOf(src.getId());
				if(indexSrc!=-1){
					nodes.splice(indexSrc,1);
				}

				var indexTgt = nodes.indexOf(tgt.getId());
				if(indexTgt!=-1){
					nodes.splice(indexTgt,1);
				}
			});
		vis.selectAll("g.node").filter(function(node){
			return nodes.indexOf(node.getId())!=-1;
		})
			.transition().duration(1000).style("opacity", 0)
		.remove();

		setTimeout(
			function() {
				
				for (i = 0; i < nodesToRemove.length; i++) {
					var node = nodesToRemove[i];
					
					// Remove the node from group to draw convex hulls  
					session.groups.forEach(function(group){
						if(group.key==node.getCompartment()){
							
							var index = group.values.indexOf(node);
							if(index!=-1)
								group.values.splice(index, 1);
							
							if(group.values.length==0){
							 	index = session.groups.indexOf(group);
								if(index!=-1){
									session.groups.splice(index, 1);
									d3.select("#"+panel).select("#D3viz")
										.select("path#"+group.key)
										.remove();
								}
							}
						}
						node.getPathways().forEach(function(pathway){
							if(group.key==pathway){
								var index = group.values.indexOf(node);
								if(index!=-1)
									group.values.splice(index, 1);
								
								if(group.values.length==0){
								 	index = session.groups.indexOf(group);
									if(index!=-1){
										session.groups.splice(index, 1);
										d3.select("#"+panel).select("#D3viz")
											.select("path#"+group.key)
											.remove();
									}
								}
							}
						}) 
					});

					var index = force.nodes().indexOf(
							node);
					if(index!=-1)
						force.nodes().splice(index, 1);
				}

				for (i = 0; i < nodesToRemove.length; i++) {
					var node = nodesToRemove[i];
					var index = force.nodes().indexOf(
							node);
					
					if(index!=-1)
						force.nodes().splice(index, 1);
				}				
			}
		, 10);
	},
	
	/*******************************************
    * Remove side compounds
    */
    removeSideCompounds : function(){
		var vis = d3.select("#viz").select("#D3viz");
		vis.selectAll("g.node")
			.filter(function(d) {
				return d.getBiologicalType()=="metabolite" && d.getIsSideCompound();
			})
			.each(function(node){
				metExploreD3.GraphNetwork.removeASelectedNode(node, "viz");
			});

        	metExploreD3.GraphNetwork.removeIsolatedNode("viz");	
        	metExploreD3.GraphNetwork.initCentroids();
	},

	/*******************************************
    * Update animation of graph
    * @param {} panel : The panel to animate or not
    * @param {} bool
    */
    setAnimated: function(panel, bool){
		if(bool){
			d3.select("#"+panel).select("#D3viz").attr("animation", "true");
			_metExploreViz.getSessionById(panel).setAnimated(true);
		}
		else
		{
			d3.select("#"+panel).select("#D3viz").attr("animation", "false");
			_metExploreViz.getSessionById(panel).setAnimated(false);
		}
	},

	/*******************************************
    * True if graph is animated
    * @param {} panel : The panel animated or not
    */
    isAnimated : function(panel){
		return d3.select("#"+panel).select("#D3viz").attr("animation");
	},

	/*******************************************
    * Function to select all nodes (back-end)  
    * @param {} panel 
    */
    selectAllNodes : function(panel){
		return d3.select("#"+panel).select("#D3viz").selectAll("g.node");
	},

	/*******************************************
    * Function to stop force
    */
    stopForce : function(session){
		var force = session.getForce();
		if(force!=undefined)  
		{		
			force.stop();
			metExploreD3.GraphNetwork.setAnimated(session.getId(), false);
		}
	},

	/*******************************************
    * Load the graph data, it generate graph visualization
    * @param {} panel : The panel to load
    */
    loadSvg : function(sessionLoaded, panel) {

    	// TROP LOURD
 		/*
 		console.log("sessionLoaded ", sessionLoaded);
    	console.log("sessionLoaded.getD3Data().data ", sessionLoaded.getD3Data().data);
    	sessionLoaded.data.d3Data=sessionLoaded.getD3Data().data;
    	console.log("sessionLoaded.data ", sessionLoaded.data);
    	console.log("toJSON ", JSON.stringify(sessionLoaded));
    	console.log("Ext.encode(sessionLoaded.data) ", Ext.encode(sessionLoaded.data));
    	var object = Ext.decode(Ext.encode(sessionLoaded.data));
    	console.log("object ", object);

    	var session = Ext.create('MetExplore.model.NetworkVizSession');
		session.data = object;
    	console.log("session ", session);
		*/
		// Get height and witdh of panel		
		var h = parseInt(metExploreD3.GraphPanel.getHeight(panel));
		var w = parseInt(metExploreD3.GraphPanel.getWidth(panel));
		
		var linkStyle = metExploreD3.getLinkStyle();
		
				
		// Initiate the D3 force drawing algorithm
		var force = sessionLoaded.getForce();
		var scale = metExploreD3.getScaleById(panel);
		// Call GraphCaption to draw the caption
		metExploreD3.GraphCaption.drawCaption();
		
		// var startall = new Date().getTime();
		// var start = new Date().getTime();
		// console.log("----Viz: START refresh/init Viz");
		
		// Define the zoomListener and put it in a store

		if(scale==undefined){
		
			// Define the zoomListener which calls the zoom function on the "zoom" event constrained within the scaleSents
			var that = metExploreD3.GraphNetwork;
			metExploreD3.GraphNetwork.zoomListener = d3.behavior
				.zoom()
				.x( xScale )
				.y( yScale )
				.scaleExtent([ 0.01, 30 ])
				.on("zoom", function(e){
						
						if(metExploreD3.GraphNetwork.zoomListener.scale()<0.8) d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", true);
						else d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", false);

					var session = _metExploreViz.getSessionById(panel);
	        		
	        		if(d3.event.sourceEvent !=null)
							if(d3.event.sourceEvent.type=='wheel')
								session.setResizable(false);
		        	
		        	// if visualisation is actived we add item to menu
	        		if(session.isActive()){
					
						that.zoom(panel);
					}
				});
		
		
			scale.add({
				'graphName' : panel,
				'xScale' : xScale,
				'yScale' : yScale,
				'zoomScale' : 1,
				'xScaleCompare' : 1,
				'yScaleCompare' : 1,
				'zoomScaleCompare' : metExploreD3.GraphNetwork.zoomListener.scale(),
				"zoom" : metExploreD3.GraphNetwork.zoomListener
			});	
			
		}
		else
		{
			var that = metExploreD3.GraphNetwork;
			
			var xScale =
			  d3.scale.linear()
			    .domain([0, w])
			    .range([0, w]);

			var yScale =
			  d3.scale.linear()
			    .domain([h, 0])
			    .range([h, 0]);

			metExploreD3.GraphNetwork.zoomListener = d3.behavior
					.zoom()
					.x( xScale )
					.y( yScale )
					.scaleExtent([ 0.01, 30 ])
					.on("zoom", function(e){
						
						if(metExploreD3.GraphNetwork.zoomListener.scale()<0.8) d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", true);
						else d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", false);

						var session = _metExploreViz.getSessionById(this.parentNode.id);
		        		
		        		if(d3.event.sourceEvent !=null)
							if(d3.event.sourceEvent.type=='wheel')
								session.setResizable(false);
		        	
		        		// if visualisation is actived we add item to menu
		        		if(session.isActive()){
							that.zoom(this.parentNode.id);
						}
					});
			scale
				.setScale(xScale, yScale, 1, 1, 1, metExploreD3.GraphNetwork.zoomListener.scale(), metExploreD3.GraphNetwork.zoomListener);			
		}

		// Remove all sub-elements in the SVG that corresponds to the D3Viz part --- tenth mss
		var vis = d3.select("#"+panel);
		vis.svg = vis.select("#D3viz").selectAll("*").remove();

		// Brush listener to multiple selection
		var nodeBrushed;
		var brushing = false;
		var brush = d3.select("#"+panel).select("#D3viz")
			.append("g")
			.datum(function() { return {selected: false, previouslySelected: false}; })
			.attr('id','brush')
			.attr("class", "brush")
			.call(d3.svg.brush()
				.x(xScale)
				.y(yScale)
				.on("brushstart", function(d) {
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
											var xScale=scale.getXScale();
											var yScale=scale.getYScale();

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

						d3.event.target.clear();
						d3.select(this).call(d3.event.target);
						var scale = metExploreD3.getScaleById(panel);

						d3.select("#"+panel).selectAll("#D3viz")
							.style("cursor", "default");

						d3.select("#"+panel).selectAll("#D3viz")
							.call(scale.getZoom())
							.on("dblclick.zoom", null)
							.on("mousedown", null);

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
			
		// Define zoomListener
		vis.svg = d3.select("#"+panel).select("#D3viz")
				.call(metExploreD3.GraphNetwork.zoomListener)
				// Remove zoom on double click
				.on("dblclick.zoom", null)
				.attr("pointer-events", "all")
				.append('svg:g')
				.attr("class","graphComponent").attr("id","graphComponent");
		
		// If a graph is already loaded
		var session = _metExploreViz.getSessionById(panel);
		
		if(session!=undefined)  
		{
			// We stop the previous animation
			var force = session.getForce();
			if(force!=undefined)  
			{		
				force.stop();
				metExploreD3.GraphNetwork.setAnimated(panel, false);
			}

			if(session.isResizable()!=undefined)
				metExploreD3.GraphNetwork.task.cancel();

			// Launch the task to resize the graph at the beginning ->tick function
			session.setResizable(true);
			metExploreD3.GraphNetwork.task = metExploreD3.createDelayedTask(
				function(){
					session.setResizable(false);
				}
			);
		}

		var animated = false;
		// Define play and stop button ->play function
		d3
			.select("#"+panel)
			.select("#D3viz")
        	.attr("animation", function(){
        		if(animated)
					return "true";
				else
					return "false";
			})
			.append("svg:g")
			.attr("class","buttonAnim").attr("id","buttonAnim")
			.on("click", metExploreD3.GraphNetwork.play)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", function(){
				if(animated)
					return document.location.href.split("index.html")[0] + "resources/icons/pause.svg";
				else
					return document.location.href.split("index.html")[0] + "resources/icons/play.svg";
			})
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate(10,10) scale(.5)");

		d3
			.select("#"+panel)
			.select("#D3viz")
        	.append("svg:g")
			.attr("class","buttonRescale").attr("id","buttonRescale")
			.on("click", function(){
				metExploreD3.GraphNetwork.rescale(panel);
			})
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", function(){
					return document.location.href.split("index.html")[0] + "resources/icons/rescale.png";
			})
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate(80,10) scale(.5)");

		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonZoomIn").attr("id","buttonZoomIn")
			.attr('x', (w-60))
			.attr('y', 10)
			.on("click", metExploreD3.GraphNetwork.zoomIn)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/zoomin.svg")
			.attr("width", "50")
			.attr("height", "50")
			.style("opacity", 0.2)
			.attr("transform", "translate("+(w-60)+",10) scale(1)")
			.on("mouseover", function(d) {  
				d3.select(this).transition().duration(500).style("opacity", 1);
		    })
	        .on("mouseout", function(d) {   
		    	d3.select(this).transition().duration(500).style("opacity", 0.2);
	        });


		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonZoomOut").attr("id","buttonZoomOut")
			.attr('x', (w-110))
			.attr('y', 10)
			.on("click", metExploreD3.GraphNetwork.zoomOut)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/zoomout.svg")
			.attr("width", "50")
			.attr("height", "50")
			.style("opacity", 0.2)
			.attr("transform", "translate("+(w-110)+",10) scale(1)")
			.on("mouseover", function(d) {  
				d3.select(this).transition().duration(500).style("opacity", 1);
		    })
	        .on("mouseout", function(d) {   
		    	d3.select(this).transition().duration(500).style("opacity", 0.2);
	        });

	    d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonHand").attr("id","buttonHand")
			.attr('x', (w-160))
			.attr('y', 10)
        	.attr("scrollable", "false")
			.on("click", metExploreD3.GraphNetwork.moveGraph)
			.style("opacity", 1)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/handcursor.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate("+(w-160)+",10) scale(1)");
		
		d3
			.select("#"+panel)
			.select("#D3viz")
			.select("buttonHand")
			.style("opacity", 0);

	    d3.select('#'+panel)
			.on("mouseover", function(){
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomOut")
					.transition().duration(500).style("opacity", 1);
					
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomIn")
					.transition().duration(500).style("opacity", 1);	
				
				var session = _metExploreViz.getSessionById(panel);
        		// if visualisation is actived we add item to menu
        		if(session.isActive()){
					var scrollable = d3.select("#"+panel).select("#buttonHand").attr("scrollable");
					if(scrollable == "false")
						d3.select("#"+panel)
							.select("#D3viz")
							.select("#buttonHand")
							.transition().duration(500).style("opacity", 0.2);
					else
						d3.select("#"+panel)
							.select("#D3viz")
							.select("#buttonHand")
							.transition().duration(500).style("opacity", 1);
				}
					
			})
			.on("mouseout", function(){
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomOut")
					.transition().duration(500).style("opacity", 0);

				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomIn")
					.transition().duration(500).style("opacity", 0);

				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonHand")
					.transition().duration(500).style("opacity", 0);
			})

    	// Refresh coresponding nodes and links 
    	var session = _metExploreViz.getSessionById(panel);
		var linkStyle = metExploreD3.getLinkStyle();
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		
		metExploreD3.GraphLink.loadLink(panel, session, linkStyle, metaboliteStyle);
		metExploreD3.GraphNode.loadNode(panel);
		
		var iDiv = document.createElement('div');
		iDiv.id = 'tooltip2';
		iDiv.className = 'tooltip2';
		
		
		metExploreD3.GraphNetwork.looksLinked();
		if(session.isLinked()){
			metExploreD3.GraphNetwork.graphAlignment(panel);
		}
		metExploreD3.GraphNetwork.tick(panel);
	},


	/*******************************************
    * Refresh the graph data, it generate graph visualization
    * @param {} panel : The panel to refresh
    */
    loadSvgFromJSON : function(panel) {	

		// Get height and witdh of panel		
		var h = parseInt(metExploreD3.GraphPanel.getHeight(panel));
		var w = parseInt(metExploreD3.GraphPanel.getWidth(panel));
		var linkStyle = metExploreD3.getLinkStyle();
				
		// Initiate the D3 force drawing algorithm
		var force = d3.layout.force().friction(0.90).gravity(0.06)
				.charge(-150).linkDistance(linkStyle.getSize()).size([ w, h ]);
		
		var session = metExploreD3.getSessionById(panel);
		session.setActivity(true);
		session.setForce(force);
		
		// Call GraphCaption to draw the caption
		if(panel=='viz')
			metExploreD3.GraphCaption.drawCaption();
		
		// var startall = new Date().getTime();
		// var start = new Date().getTime();
		// console.log("----Viz: START refresh/init Viz");
		
		// Define the zoomListener and put it in a store

		var xScale =
			  d3.scale.linear()
			    .domain([0, w])
			    .range([0, w]);

			var yScale =
			  d3.scale.linear()
			    .domain([h, 0])
			    .range([h, 0]);

		if(metExploreD3.getScaleById(panel)==undefined){
		
			// Define the zoomListener which calls the zoom function on the "zoom" event constrained within the scaleSents
			var that = metExploreD3.GraphNetwork;
			var scale = metExploreD3.getScaleById(panel);
			var zoomListener = scale.getZoom();
			zoomListener = d3.behavior
				.zoom()
				.x( xScale )
				.y( yScale )
				.scaleExtent([ 0.01, 30 ])
				.on("zoom", function(e){
						
						if(metExploreD3.GraphNetwork.zoomListener.scale()<0.8) d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", true);
						else d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", false);

					var session = metExploreD3.getSessionById(panel);
	        		
	        		if(d3.event.sourceEvent !=null)
							if(d3.event.sourceEvent.type=='wheel')
								session.setResizable(false);
		        	
		        	// if visualisation is actived we add item to menu
	        		if(session.isActive()){
					
						that.zoom(panel);
					}
				});
		
		
			scale.add({
				'graphName' : panel,
				'xScale' : xScale,
				'yScale' : yScale,
				'zoomScale' : 1,
				'xScaleCompare' : 1,
				'yScaleCompare' : 1,
				'zoomScaleCompare' : zoomListener.scale(),
				"zoom" : zoomListener
			});	
			
		}
		else
		{
			var that = metExploreD3.GraphNetwork;
			var scale = metExploreD3.getScaleById(panel);
			var zoomListener = scale.getZoom();
			zoomListener = d3.behavior
					.zoom()
					.x( xScale )
					.y( yScale )
					.scaleExtent([ 0.01, 30 ])
					.on("zoom", function(e){
						
						if(zoomListener.scale()<0.8) d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", true);
						else d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll('text').classed("hide", false);

									
						var session = metExploreD3.getSessionById(this.parentNode.id);
		        		
		        		if(d3.event.sourceEvent !=null)
							if(d3.event.sourceEvent.type=='wheel')
								session.setResizable(false);
		        	
		        		// if visualisation is actived we add item to menu
		        		if(session.isActive()){
							that.zoom(this.parentNode.id);
						}
					});
			scale
				.getStoreByGraphName(panel)
				.setScale(xScale, yScale, 1, 1, 1, zoomListener.scale(), zoomListener);			
		}

		// Remove all sub-elements in the SVG that corresponds to the D3Viz part --- tenth mss
		var vis = d3.select("#"+panel);
		vis.svg = vis.select("#D3viz").selectAll("*").remove();

		// Brush listener to multiple selection
		var nodeBrushed;
		var brushing = false;
		var brush = d3.select("#"+panel).select("#D3viz")
			.append("g")
			.datum(function() { return {selected: false, previouslySelected: false}; })
			.attr('id','brush')
			.attr("class", "brush")
			.call(d3.svg.brush()
				.x(xScale)
				.y(yScale)
				.on("brushstart", function(d) {
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
											var xScale=scale.getXScale();
											var yScale=scale.getYScale();

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

						d3.event.target.clear();
						d3.select(this).call(d3.event.target);
						var scale = metExploreD3.getScaleById(panel);

						d3.select("#"+panel).selectAll("#D3viz")
							.style("cursor", "default");

						d3.select("#"+panel).selectAll("#D3viz")
							.call(scale.getZoom())
							.on("dblclick.zoom", null)
							.on("mousedown", null);

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

		var scale = metExploreD3.getScaleById(panel);
		var zoomListener = scale.getZoom();

		// Define zoomListener
		vis.svg = d3.select("#"+panel).select("#D3viz")
				.call(zoomListener)
				// Remove zoom on double click
				.on("dblclick.zoom", null)
				.attr("pointer-events", "all")
				.append('svg:g')
				.attr("class","graphComponent").attr("id","graphComponent");
		
		// If a graph is already loaded
		var session = _metExploreViz.getSessionById(panel);
		if(session!=undefined)  
		{
			// We stop the previous animation
			var force = session.getForce();
			if(force!=undefined)  
			{		
				force.stop();
				metExploreD3.GraphNetwork.setAnimated(panel, false);
			}

			if(session.isResizable()!=undefined && session.isResizable()!=false)
				metExploreD3.GraphNetwork.task.cancel();

			// Launch the task to resize the graph at the beginning ->tick function
			session.setResizable(true);
			metExploreD3.GraphNetwork.task = metExploreD3.createDelayedTask(
				function(){
					session.setResizable(false);
				}
			);
		}

		// Define play and stop button ->play function
		d3
			.select("#"+panel)
			.select("#D3viz")
        	.attr("animation", "true")
			.append("svg:g")
			.attr("class","buttonAnim").attr("id","buttonAnim")
			.on("click", metExploreD3.GraphNetwork.play)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/pause.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate(10,10) scale(.5)");

		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","whiteBlack").attr("id","whiteBlack")
			.attr('x', (w-100))
			.attr('y', 100)
			.on("click", function(){
				if(d3.select("#"+panel).style("-webkit-filter").search('grayscale') == -1
					&& d3.select("#"+panel).style("filter").search('grayscale') == -1)
					d3.select("#"+panel).style("filter", "grayscale(100%)").style("-webkit-filter", "grayscale(100%)");
				else
					d3.select("#"+panel).style("filter", "").style("-webkit-filter", "");
			})
			.style("cursor", "hand")
			.style("visibility", "hidden")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/blackWhite.png")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate("+(w-100)+",100) scale(0.5)");

		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","invertColor").attr("id","invertColor")
			.attr('x', (w-100))
			.attr('y', 150)
			.on("click", function(){
				if(d3.select("#"+panel).style("-webkit-filter").search('invert') == -1
					&& d3.select("#"+panel).style("filter").search('invert') == -1)
					d3.select("#"+panel).style("filter", "invert(100%)").style("-webkit-filter", "invert(100%)");
				else
					d3.select("#"+panel).style("filter", "").style("-webkit-filter", "");
			})
			.style("cursor", "hand")
			.style("visibility", "hidden")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/invertColor.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate("+(w-100)+",150) scale(0.5)");

		
		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonZoomIn").attr("id","buttonZoomIn")
			.attr('x', (w-60))
			.attr('y', 10)
			.on("click", metExploreD3.GraphNetwork.zoomIn)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/zoomin.svg")
			.attr("width", "50")
			.attr("height", "50")
			.style("opacity", 0.2)
			.attr("transform", "translate("+(w-60)+",10) scale(1)")
			.on("mouseover", function(d) {  
				d3.select(this).transition().duration(500).style("opacity", 1);
		    })
	        .on("mouseout", function(d) {   
		    	d3.select(this).transition().duration(500).style("opacity", 0.2);
	        });


		d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonZoomOut").attr("id","buttonZoomOut")
			.attr('x', (w-110))
			.attr('y', 10)
			.on("click", metExploreD3.GraphNetwork.zoomOut)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/zoomout.svg")
			.attr("width", "50")
			.attr("height", "50")
			.style("opacity", 0.2)
			.attr("transform", "translate("+(w-110)+",10) scale(1)")
			.on("mouseover", function(d) {  
				d3.select(this).transition().duration(500).style("opacity", 1);
		    })
	        .on("mouseout", function(d) {   
		    	d3.select(this).transition().duration(500).style("opacity", 0.2);
	        });

	    d3
			.select("#"+panel)
			.select("#D3viz")
			.append("svg:g")
			.attr("class","buttonHand").attr("id","buttonHand")
			.attr('x', (w-160))
			.attr('y', 10)
        	.attr("scrollable", "false")
			.on("click", metExploreD3.GraphNetwork.moveGraph)
			.style("opacity", 1)
			.style("cursor", "hand")
			.append("image")
			.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/handcursor.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform", "translate("+(w-160)+",10) scale(1)");
		
		d3
			.select("#"+panel)
			.select("#D3viz")
			.select("buttonHand")
			.style("opacity", 0);

	    d3.select('#'+panel)
			.on("mouseover", function(){
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomOut")
					.transition().duration(500).style("opacity", 1);
					
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomIn")
					.transition().duration(500).style("opacity", 1);	
				
				var session = _metExploreViz.getSessionById(panel);
        		// if visualisation is actived we add item to menu
        		if(session.isActive()){
					var scrollable = d3.select("#"+panel).select("#buttonHand").attr("scrollable");
					if(scrollable == "false")
						d3.select("#"+panel)
							.select("#D3viz")
							.select("#buttonHand")
							.transition().duration(500).style("opacity", 0.2);
					else
						d3.select("#"+panel)
							.select("#D3viz")
							.select("#buttonHand")
							.transition().duration(500).style("opacity", 1);
				}
					
			})
			.on("mouseout", function(){
				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomOut")
					.transition().duration(500).style("opacity", 0);

				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonZoomIn")
					.transition().duration(500).style("opacity", 0);

				d3.select("#"+panel)
					.select("#D3viz")
					.select("#buttonHand")
					.transition().duration(500).style("opacity", 0);
			})

		// Start the animation
    	metExploreD3.GraphNetwork.setAnimated(panel, true);

    	// Refresh coresponding nodes and links 
    	var session = _metExploreViz.getSessionById(panel);
		var linkStyle = metExploreD3.getLinkStyle();
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		
		metExploreD3.GraphLink.refreshLink(panel, session, linkStyle, metaboliteStyle);
		metExploreD3.GraphNode.refreshNode(panel);
		var iDiv = document.createElement('div');
		iDiv.id = 'tooltip2';
		iDiv.className = 'tooltip2';
		document.getElementById("viz").appendChild(iDiv);  

		var linked = d3.select(that).attr("isLink");
		d3.select(that).select("image").remove();
		d3.select(that).append("image")
			.attr("xlink:href",document.location.href.split("index.html")[0] + "resources/icons/link.svg")
			.attr("width", "50")
			.attr("height", "50")
			.attr("transform","translate(10,50) scale(.5)");
		
		session.setLinked(false);
		// Define play and stop button ->play function
		if(panel!="viz"){
			d3
				.select("#"+panel)
				.select("#D3viz")
				.append("svg:g")
				.attr("class","buttonLink").attr("id","buttonLink")
	        	.attr("isLink", "false")
				.on("click", metExploreD3.GraphNetwork.setLink)
				.style("cursor", "hand")
				.append("image")
				.attr("xlink:href", document.location.href.split("index.html")[0] + "resources/icons/unlink.svg")
				.attr("width", "50")
				.attr("height", "50")
				.attr("transform", "translate(10,50) scale(.5)");

		}
		else
		{
			metExploreD3.GraphNetwork.looksLinked();
			if(session.isLinked()){
				metExploreD3.GraphNetwork.graphAlignment(panel);
			}
		}
		
		// 62771 ms for recon before refactoring
		// 41465 ms now
		// var endall = new Date().getTime();
		// var timeall = endall - startall;
		// console.log("----Viz: FINISH refresh/ all "+timeall);
		var session = metExploreD3.getSessionById(panel);
		var networkData = session.getD3Data();	
		var force = session.getForce();
		
		/*var stringJSON="{\"nodes\":";	
		stringJSON+=Ext.encode(networkData.getNodes());	
		stringJSON+=",\n\"link\":";
		stringJSON+=Ext.encode(networkData.getLinks());
		stringJSON+='}\n';	
		console.log(stringJSON);*/
		

		force
			.nodes(networkData.getNodes())
			.links(networkData.getLinks())
			.on("tick", function(){
				//if(force.alpha() < .08){
					if(force.alpha() >= .005){
					        setTimeout(metExploreD3.GraphNetwork.tick(panel), 0);
					}
				// }
			})
			.start();
        
		session.setForce(force);
	}
}
