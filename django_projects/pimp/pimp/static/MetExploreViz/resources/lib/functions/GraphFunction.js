/**
 * @author MC
 * @description : Basic functions
 */
    
metExploreD3.GraphFunction = {
    bfs : function (node){
	    var graph = metExploreD3.GraphFunction.getGraphNotDirected();

    	var root = graph.getNode(node.getId());
  
  		for (var key in graph.nodes) {	
	          graph.nodes[key].distance = "INFINITY";        
	          graph.nodes[key].parent = null;
	    }            
  
      	var queue = [];     
  
      	root.distance = 0;
     	queue.push(root);                      
 
     	while(queue.length!=0){         
     	     
			var current = queue.pop();

			current.getAdjacents().forEach(function(n){

				if(n.distance == 'INFINITY')
			    {
			    	n.distance = current.distance + 1;
				    n.parent = current;
				    queue.push(n); 
			    }
			});
		}  
		return graph;          
	},

    colorDistanceOnNode : function(graph, func){
		var networkData = _metExploreViz.getSessionById('viz').getD3Data();
		var maxDistance = 0; 
		for (var key in graph.nodes) {	
	        var dist = graph.nodes[key].distance;   
	        if(maxDistance<dist)
	        	maxDistance=dist;    
	        networkData.getNodeById(key).distance = dist;
	    }

    	var color = d3.scale.category20();
		var color = d3.scale.linear()
			.domain([0, 4])
			.range(["blue", "yellow"]);


		d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
			.style("fill", function(node) { return color(node.distance); });

		if(func!=undefined){
			func();
		}
    },

    test3 : function(){
		
		var networkData = _metExploreViz.getSessionById('viz').getD3Data();	
		
		d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
			.on("click", function(node){
				
				var array = []; 
				
				_metExploreViz.getSessionById('viz').getSelectedNodes().forEach(function(anodeid){
					var theNode = networkData.getNodeById(anodeid);
					var graph = metExploreD3.GraphFunction.bfs(theNode);
					array.push(graph);
				});
				
				var finalGraph = array[0];
				for (var key in finalGraph.nodes) {	

				    var arrayVal = 
					    array
					    	.filter(function(graph){
					    		return graph.nodes[key].distance !="INFINITY";
					    	})
						    .map(function(graph){
					        	return graph.nodes[key].distance; 
					        });

			        finalGraph.nodes[key].distance = Math.min.apply(Math, arrayVal) ;   			    
			       	if(finalGraph.nodes[key].distance=="Infinity") finalGraph.nodes[key].distance=10000;
			       	
				};
				metExploreD3.GraphFunction.colorDistanceOnNode(finalGraph, setCharge);
		});
		function setCharge(){
			var color = d3.scale.linear()
				.domain([0, 1, 2, 3])
				.range([-600, -500, -400, -30]);

			metExploreD3.getGlobals().getSessionById('viz').getForce().charge(function(node){
				var value = node.distance;
				if(node.distance>3) 
					value = 3;
				var val = color(value);
				return val;
			});	
		};
    },
    testFlux : function(){
		
		var networkData = _metExploreViz.getSessionById('viz').getD3Data();	
		
			var color = d3.scale.linear()
				.domain([0, 0.1, 0.2, 0.5, 1])
				.range([-30, -50, -60,-500 -600]);

			metExploreD3.getGlobals().getSessionById('viz').getForce().charge(function(node){
				var value = d3.select('g#node'+node.getId()+'.node').attr('opacity');
				var val = color(value);
				return val;
			});	
		
    },
    test : function(){
		
		var networkData = _metExploreViz.getSessionById('viz').getD3Data();	
		
		d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
			.on("click", function(node){
				metExploreD3.GraphFunction.colorDistanceOnNode(metExploreD3.GraphFunction.bfs(node), setCharge);
		});
		function setCharge(){
			var color = d3.scale.linear()
				.domain([0, 1, 2, 3])
				.range([-600, -500, -400, -30]);

			metExploreD3.getGlobals().getSessionById('viz').getForce().charge(function(node){
				var value = node.distance;
				if(node.distance>3) 
					value = 3;
				var val = color(value);
				return val;
			});	
		};
    },
    test2 : function(){
		
		var networkData = _metExploreViz.getSessionById('viz').getD3Data();	
		
		d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
			.on("click", function(node){
				metExploreD3.GraphFunction.colorDistanceOnNode(metExploreD3.GraphFunction.bfs(node), setLinkDistance);
		});
		function setLinkDistance(){
			var linkStyle = metExploreD3.getLinkStyle();
			var color = d3.scale.linear()
				.domain([0, 1, 2, 3])
				.range([5*linkStyle.getSize(), 4*linkStyle.getSize(), 3*linkStyle.getSize(), linkStyle.getSize()]);
				
				// d3.layout.force().friction(0.90).gravity(0.06)
				// 	.charge(-150)

				// d3.layout.force().friction(0.90).gravity(0.08).charge(-4000).theta(0.2)
    
			var color2 = d3.scale.linear()
				.domain([0, 1, 2, 3])
				.range([-600, -500, -400, -30]);

			metExploreD3.getGlobals().getSessionById('viz').getForce()
				.linkDistance(function(link){

					var value = Math.max(link.getSource().distance, link.getTarget().distance);
					if(value>3) 
						value = 3;
					var val = color(value);
					return val;
				})
				.gravity(0.04)
				.charge(function(node){
					var value = node.distance;
					if(node.distance>3) 
						value = 3;
					var val = color2(value);
					return val;
				});
		};
    },

    /*******************************************
    * Hierarchical drawing of the current tulip network
    * It uses the default algorithm provided by Tulip.js
    */
    hierarchicalDrawing : function(){
    	var algo = "Hierarchical Tree (R-T Extended)";
		var params = [];
		params.push({"name":"node spacing", "value":50});
		metExploreD3.GraphFunction.applyTulipLayoutAlgorithmInWorker(algo, params);
    },

    /*******************************************
    * Sugiyama (OGDF) drawing of the current tulip network
    * It uses the default algorithm provided by Tulip.js
    */
    sugiyamaDrawing : function(){
    	var algo = "Sugiyama (OGDF)";
		var params = [];
		params.push({"name":"node spacing", "value":50});
		params.push({"name":"node distance", "value":50});
		params.push({"name":"layer distance", "value":50});
		metExploreD3.GraphFunction.applyTulipLayoutAlgorithmInWorker(algo, params);
    },

    /*******************************************
    * Betweenness Centrality of the current tulip network
    * It uses the default algorithm provided by Tulip.js
    */
    betweennessCentrality : function(){
    	var algo = "Betweenness Centrality";
		var params = [];
		params.push({"name":"directed", "value":true});
		// params.push({"name":"node distance", "value":50});
		// params.push({"name":"layer distance", "value":50});
		metExploreD3.GraphFunction.applyTulipDoubleAlgorithmInWorker(algo, params);
    },

    /*******************************************
    * Layout drawing application provided by the tulip.js library
    */
	applyTulipLayoutAlgorithmInWorker : function(algo, parameters) {

		var panel = "viz";
		var myMask = metExploreD3.createLoadMask("Selection in progress...", panel);
		if(myMask!= undefined){
			
			metExploreD3.showMask(myMask);

	        metExploreD3.deferFunction(function() {
				var sessions = _metExploreViz.getSessionsSet();
				
				var session = _metExploreViz.getSessionById(panel);

				var networkData = session.getD3Data();
				
				if(session!=undefined)  
				{
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
				var graph = null;
				var tulipView = null;

				var size = 100;
				var correspondNodeId = {};

				function processGraph() {
					tulip.holdObservers();
					var viewLayout = graph.getLayoutProperty('viewLayout');
					var viewColor = graph.getColorProperty('viewColor');
					var viewLabel = graph.getStringProperty("viewLabel");
					//   viewLayout.setAllEdgeValue(new Array());
					//   var n = graph.addNode();
					//   viewColor.setNodeValue(n, randomColor());
					//   viewLabel.setNodeValue(n, 'node ' + graph.numberOfNodes());
					//   var nodes = graph.getNodes();
					   

					 //  var i = Math.random() * graph.numberOfNodes() | 0;
					 //  var j = Math.random() * graph.numberOfNodes() | 0;

					 //  graph.addEdge(nodes[i], nodes[j]);
					tulip.unholdObservers();
					// graph.applyLayoutAlgorithm('FM^3 (OGDF)', graph.getLayoutProperty('viewLayout'));
					var params = tulip.getDefaultAlgorithmParameters(algo, graph);
					console.log(params);
					if(parameters!=undefined) {
						parameters.forEach(function(param){
							params[param.name]=param.value;
						});
					}
					graph.applyLayoutAlgorithmInWorker(algo, graph.getLocalLayoutProperty('viewLayout'), params,
				    	function(){
				    		
							d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
					        	.each(function(node){
									node.px = viewLayout.getNodeValue(correspondNodeId[node.getId()]).x ;
									node.py = viewLayout.getNodeValue(correspondNodeId[node.getId()]).y ;
									node.x = viewLayout.getNodeValue(correspondNodeId[node.getId()]).x ;
									node.y = viewLayout.getNodeValue(correspondNodeId[node.getId()]).y ;
								});
				        
				         	metExploreD3.GraphNetwork.tick("viz");
				        	metExploreD3.hideMask(myMask);
				    	}
				    );
				}

				function initTulip(func) {

					if (typeof tulip == 'undefined' || !tulip.isLoaded()) {
						setTimeout(initTulip, 1000);
					} else {

						graph = new tulip.Graph();

						console.log("tulip.getLayoutAlgorithmPluginsList() ", tulip.getLayoutAlgorithmPluginsList());
						console.log("tulip.getAlgorithmPluginsList() ", tulip.getAlgorithmPluginsList());
						console.log("tulip.getDoubleAlgorithmPluginsList() ", tulip.getDoubleAlgorithmPluginsList());

						tulip.holdObservers();

						graph.setName("Test Javascript Graph");

						var viewLabel = graph.getStringProperty("viewLabel");
						networkData.getNodes().forEach(function(node){
							var n = graph.addNode();
							var viewLayout = graph.getLayoutProperty('viewLayout');
							viewLayout.setNodeValue(n, new tulip.Coord(node.x, node.y, 0));

							viewLabel.setNodeValue(n, "node 1");

							correspondNodeId[node.getId()] = n;
						});

						var viewLayout = graph.getLayoutProperty('viewLayout');
						networkData.getLinks().forEach(function(link){
							graph.addEdge(correspondNodeId[link.getSource()], correspondNodeId[link.getTarget()]);
						});


						var bends = new Array();
						bends.push(new tulip.Coord(0,0,0));

						viewLayout.setAllEdgeValue(bends);

						tulip.unholdObservers();
					}
					if (func!=undefined) {func()};
				}

				initTulip(processGraph);

			}, 100);
		}
	},

    /*******************************************
    * Algorithms provided by the tulip.js library
    */
	applyTulipDoubleAlgorithmInWorker : function(algo, parameters) {

		var panel = "viz";
		var myMask = metExploreD3.createLoadMask("Selection in progress...", panel);
		if(myMask!= undefined){
			
			metExploreD3.showMask(myMask);

	        metExploreD3.deferFunction(function() {
				var sessions = _metExploreViz.getSessionsSet();
				
				var session = _metExploreViz.getSessionById(panel);

				var networkData = session.getD3Data();
				
				if(session!=undefined)  
				{
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
				var graph = null;
				var tulipView = null;

				var size = 100;
				var correspondNodeId = {};

				function processGraph() {
					tulip.holdObservers();
					var viewLayout = graph.getLayoutProperty('viewLayout');
					var viewColor = graph.getColorProperty('viewColor');
					var viewLabel = graph.getStringProperty("viewLabel");
					var viewMetric = graph.getDoubleProperty('viewMetric');
					//   viewLayout.setAllEdgeValue(new Array());
					//   var n = graph.addNode();
					//   viewColor.setNodeValue(n, randomColor());
					//   viewLabel.setNodeValue(n, 'node ' + graph.numberOfNodes());
					//   var nodes = graph.getNodes();
					   

					 //  var i = Math.random() * graph.numberOfNodes() | 0;
					 //  var j = Math.random() * graph.numberOfNodes() | 0;

					 //  graph.addEdge(nodes[i], nodes[j]);
					tulip.unholdObservers();
					// graph.applyLayoutAlgorithm('FM^3 (OGDF)', graph.getLayoutProperty('viewLayout'));
					var params = tulip.getDefaultAlgorithmParameters(algo, graph);
					if(parameters!=undefined) {
						parameters.forEach(function(param){
							params[param.name]=param.value;
						});
					}
					console.log("params :", params);
			
					graph.applyDoubleAlgorithmInWorker(algo, graph.getDoubleProperty('viewMetric'), params,
				    	function(){

					   		var arrayVal = [];

							d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
					        	.each(function(node){
									arrayVal.push(viewMetric.getNodeValue(correspondNodeId[node.getId()]));
								});

							var colorNode = d3.scale.linear()
								.domain([Math.min.apply(null, arrayVal), Math.max.apply(null, arrayVal)])
					    		.range(["yellow", "blue"]);

							var sizeNode = d3.scale.linear()
								.domain([Math.min.apply(null, arrayVal), Math.max.apply(null, arrayVal)])
					    		.range([1, 3]);

							d3.select("#viz").select("#D3viz").select("#graphComponent").selectAll("g.node")
					        	.style('fill', function(node){
									return colorNode(viewMetric.getNodeValue(correspondNodeId[node.getId()]));
								})
								.attr("transform", function(node){
									return "translate("+node.x+", "+node.y+") scale("+sizeNode(viewMetric.getNodeValue(correspondNodeId[node.getId()]))+")";
								}).transition().duration(2000);

					        metExploreD3.hideMask(myMask);
				        }
				    );
				}

				function initTulip(func) {

					if (typeof tulip == 'undefined' || !tulip.isLoaded()) {
						setTimeout(initTulip, 1000);
					} else {

						graph = new tulip.Graph();

						console.log("tulip.getLayoutAlgorithmPluginsList() ", tulip.getLayoutAlgorithmPluginsList());
						console.log("tulip.getAlgorithmPluginsList() ", tulip.getAlgorithmPluginsList());
						console.log("tulip.getDoubleAlgorithmPluginsList() ", tulip.getDoubleAlgorithmPluginsList());

						tulip.holdObservers();

						graph.setName("Test Javascript Graph");

						var viewLabel = graph.getStringProperty("viewLabel");
						networkData.getNodes().forEach(function(node){
							var n = graph.addNode();
							var viewLayout = graph.getLayoutProperty('viewLayout');
							viewLayout.setNodeValue(n, new tulip.Coord(node.x, node.y, 0));

							viewLabel.setNodeValue(n, "node 1");

							correspondNodeId[node.getId()] = n;
						});

						var viewLayout = graph.getLayoutProperty('viewLayout');
						networkData.getLinks().forEach(function(link){
							graph.addEdge(correspondNodeId[link.getSource()], correspondNodeId[link.getTarget()]);
						});


						var bends = new Array();
						bends.push(new tulip.Coord(0,0,0));

						viewLayout.setAllEdgeValue(bends);

						tulip.unholdObservers();
					}
					if (func!=undefined) {func()};
				}

				initTulip(processGraph);

			}, 100);
		}
	},

	drawNetwork : function() {
	},

	randomDrawing : function() {
	},

	// Force based drawing
	// Use the arbor version of the algorithm provided by
	// Cytoscape
	// If there are more than maxDisplayedLabels,then the
	// animation is not used
	stopSpringDrawing : function() {
	},
	
	/**
	 * Extract a subnetwork based on lightest path length
	 * between each pair of selected nodes it returns a graph
	 * where nodes have a subnet attribute telling wether they
	 * are in subnet or not
	 */
	extractSubNetwork : function(graph) {
		var session = _metExploreViz.getSessionById('viz');
		// Should be a parameter
		var nodeSelection = [];
		// create the graph structure based on the displayed
		// network
		// This graph will contain also backward reactions

		if (session.getVizEngine() == 'D3') {
			// console.log("Subnetwork extraction using D3");
			var vis = d3.select("#viz").select("#D3viz");
			nodeSelection = session.getSelectedNodes();
						
			if (nodeSelection.length < 2){
				metExploreD3.displayMessage("Warning", "At least two nodes have to be selected or mapped.");
				return null;
			}
			else {
				// Map containing nodes,index values
				var selectedNodesIndex = {};
				for (i = 0; i < nodeSelection.length; i++) {
					selectedNodesIndex[nodeSelection[i]] = i;
				}
				// Create a matrix containing all the paths
				var paths = [];
				// for each pair of selected nodes, create an
				// entry in the path matrix
				for (i = 0; i < nodeSelection.length; i++) {
					paths[i] = [];
					for (j = 0; j < nodeSelection.length; j++)
						paths[i][j] = null;
				}

				for (var n in graph.nodes) {
					graph.nodes[n].inSubNet = false;
				}
				for (var i = 0; i < graph.edges.length; i++) {
					graph.edges[i].inSubNet = false;
				}
				// For each node in the selection
				// Compute its lightest path to other nodes
				for (var i = 0; i < nodeSelection.length; i++) {
					// var nodeI = nodeSelection[i];
					var selectedNodeID = nodeSelection[i];
					// Since while searching for a path we may
					// find another one
					// We are going to keep the path already
					// found
					var jWithPath = new Array();
					for (var j = 0; j < nodeSelection.length; j++) {
						if (j != i) {
							// if the paths is not already
							// computed
							if (paths[i][j] == null) {
								// If we go through a reaction,
								// we want to avoid going
								// through its back version
								var reactionUsed = new Array();
								// if not, do the computation
								// var nodeJ=nodeSelection[j];
								var graphNodeJ = nodeSelection[j];
								for ( var n in graph.nodes) {
									graph.nodes[n].distance = Infinity;
									graph.nodes[n].predecessor = null;
									graph.nodes[n].optimized = false;
								}

								var source = graph.nodes[selectedNodeID];
								source.distance = 0;
								/*
								 * set of unoptimized nodes,
								 * sorted by their distance (but
								 * a Fibonacci heap would be
								 * better)
								 */
								var q = new BinaryMinHeap(
										graph.nodes, "distance");
								// pointer to the node in focus
								var node;
								/*
								 * get the node with the
								 * smallest distance as long as
								 * we have unoptimized nodes.
								 * q.min() can have O(log n).
								 */
								var targetReached = false;
								while ((q.min() != undefined)
										&& (!targetReached)) {
									/* remove the latest */
									node = q.extractMin();
									node.optimized = true;
									for (e in node.edges) {
										var other = node.edges[e].target;
										if (other.optimized)
											continue;
										/*
										 * look for an
										 * alternative route
										 */
										// var alt =
										// node.distance +
										// node.edges[e].weight;
										/*
										 * Implementation of the
										 * lightest path
										 */
										/*
										 * will penalize high
										 * degree nodes
										 */
										var alt = node.distance
												+ (node.edges.length)
												* (node.edges.length);
										/*
										 * update distance and
										 * route if a better one
										 * has been found
										 */
										if ((alt < other.distance)
												&& reactionUsed.indexOf(metExploreD3.GraphFunction
																.getReactionIdWithoutBack(other.id)) == -1) {
											/*
											 * Add the reaction
											 * to the visited
											 * ones
											 */
											reactionUsed
													.push(metExploreD3.GraphFunction
															.getReactionIdWithoutBack(other.id));
											/*
											 * update distance
											 * of neighbour
											 */
											other.distance = alt;
											/*
											 * update priority
											 * queue
											 */
											q.heapify();
											/* update path */
											other.predecessor = node;
										}
										if (other.id == graphNodeJ) {
											// if the target is
											// reached then we
											// will stop
											targetReached = true;
											paths[i][j] = metExploreD3.GraphFunction
													.getPathBasedOnPredecessors(
															graph,
															graphNodeJ);
										}
										// if the node is a node
										// in the selection list
										// if there is no
										// corresponding path
										// we add the paths from
										// i to it!
										else {
											var nodeIndex = selectedNodesIndex[other.id];
											if ((nodeIndex != undefined)
													&& (paths[i][nodeIndex] == null)) {
												paths[i][nodeIndex] = metExploreD3.GraphFunction
														.getPathBasedOnPredecessors(
																graph,
																other.id);
											}
										}
									}
								}

							}
						}
					}
				}
			}
			return graph;
		}
	},


	getGraph : function() {
		var session = _metExploreViz.getSessionById( 'viz');
		var graph = new Graph();
		var vis = d3.select("#viz").select("#D3viz");

		vis.selectAll("g.node")
			.each(function(node){
				// If reaction is reversible, create the
				// back version of the node
				if(node.getBiologicalType()=="reaction" && node.getReactionReversibility())
					graph.addNode(node.getId()+"_back");
				
				// Add node in the graph
				graph.addNode(node.getId());
			});

		vis.selectAll("path.link")
			.each(function(link){
				var source = link.source;
				var target = link.target;

				var sourceId = source.getId();
				var targetId = target.getId();
			

				if(source.getBiologicalType()=="reaction" && source.getReactionReversibility())
				{
					graph.addEdge(targetId, sourceId+"_back");
				}

				if(target.getBiologicalType()=="reaction" && target.getReactionReversibility())
				{	

					graph.addEdge(targetId+"_back", sourceId);
				}
				
				graph.addEdge(sourceId, targetId);
			});

			return graph;
	},

	getGraphNotDirected : function() {
		var session = _metExploreViz.getSessionById( 'viz');
		var graph = new Graph();
		var vis = d3.select("#viz").select("#D3viz");

		vis.selectAll("g.node")
			.each(function(node){
				graph.addNode(node.getId());
			});

		vis.selectAll("path.link")
			.each(function(link){
				var source = link.source;
				var target = link.target;

				var sourceId = source.getId();
				var targetId = target.getId();
			
				graph.addEdge(sourceId, targetId);
			});

			return graph;
	},

	// Once the shortest path is computed, we have, for each
	// node on the path its predecessor
	// It is necessary to go backward in order to get the right
	// path
	getPathBasedOnPredecessors : function(graph, nodeJid) {
		var path = new Array();
		// get the path from I to J
		var predecessor = graph.nodes[nodeJid].predecessor;
		if (predecessor == null)
			return path;
		else {
			var invertedPath = new Array();
			var nodeToAdd = graph.nodes[nodeJid];
			nodeToAdd.inSubNet = true;
			while (nodeToAdd != null) {
				invertedPath.push(nodeToAdd);
				nodeToAdd.inSubNet = true;
				for (e in nodeToAdd.edges) {
					var edge = nodeToAdd.edges[e];
					if (nodeToAdd.predecessor != null) {
						if (edge.source.id == nodeToAdd.predecessor.id)
							edge.inSubNet = true;
					}
				}
				nodeToAdd = nodeToAdd.predecessor;
			}
			for (var x = invertedPath.length - 1; x >= 0; x--) {
				path.push(invertedPath[x].id);
			}
			return path;
		}
	},

	/**
	 * Hihglight nodes and edges belonging to a subnetwork
	 */
	keepOnlySubnetwork : function() {
		var session = _metExploreViz.getSessionById('viz');
		//console.log("------keep only sub-network------")
		var force = session.getForce();
		var networkData = session.getD3Data();
		
		var graphSession = metExploreD3.GraphFunction.getGraph();

		var myMask = metExploreD3.createLoadMask("Remove elements not in path...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
			metExploreD3.deferFunction(function() {			         
				
		        
	        	var vis = d3.select("#"+'viz').select("#D3viz");
				
				if(session!=undefined) 
				{
					// We stop the previous animation
					var force = session.getForce();
					if(force!=undefined)  
					{
						if(metExploreD3.GraphNetwork.isAnimated('viz')== "true")
							force.stop();
												
					}
				}


				var graph = metExploreD3.GraphFunction.extractSubNetwork(graphSession);
				console.log("graph after extraction ",graph);
				if(graph!=null)
				{
					var subEmpty = true;
					for ( var i in session.getSelectedNodes()) {
						var nodeID = session.getSelectedNodes()[i];
						if (graph.nodes[nodeID].inSubNet)
							subEmpty = false;
					}

					if (subEmpty)
						metExploreD3.displayMessage("Warning", "There is no path between the selected nodes !!");
					else {
						var vis = d3.select("#viz").select("#D3viz");

						vis.selectAll("g.node")
							.filter(function(d) {
								if( d.getBiologicalType() == 'metabolite' )
								{
									var id = d.getId();
									return !graph.nodes[id].inSubNet ;
										
								}
								else
								{
									if(d.getBiologicalType() == 'reaction')
									{
										var id = d.getId();
										var backID = d.getId() + "_back";
										if (graph.nodes[backID] == undefined)
											return !graph.nodes[id].inSubNet
										else
											return !(graph.nodes[id].inSubNet || graph.nodes[backID].inSubNet)
									}
								}
							})
							.each(function(node){
								metExploreD3.GraphNetwork.removeANode(node,"viz");
							});
					}
				}

				if(session!=undefined)  
				{
					if(force!=undefined)  
					{		
						if(metExploreD3.GraphNetwork.isAnimated("viz")== "true")
							force.start();
					}	
				}
		    	metExploreD3.hideMask(myMask);
	    	}, 10);
	    }
	},

	/**
	 * Hihglight nodes and edges belonging to a subnetwork
	 */
	highlightSubnetwork : function() {
		var session = _metExploreViz.getSessionById('viz');
		var myMask = metExploreD3.createLoadMask("Highlight Subnetwork...", 'viz');
		if(myMask!= undefined){

			metExploreD3.showMask(myMask);
			metExploreD3.deferFunction(function() {			         
				
		        
	        	var vis = d3.select("#"+'viz').select("#D3viz");
				
				if(session!=undefined) 
				{
					// We stop the previous animation
					var force = session.getForce();
					if(force!=undefined)  
					{
						if(metExploreD3.GraphNetwork.isAnimated('viz')== "true")
							force.stop();
												
					}
				}
		
				var graphSession = metExploreD3.GraphFunction.getGraph();

				var graph = metExploreD3.GraphFunction.extractSubNetwork(graphSession);
				
				console.log("graph after extraction in highlight subnetwork ",graph);
				if(graph!=null)
				{
					var subEmpty = true;
					for ( var i in session
							.getSelectedNodes()) {
						var nodeID = session
								.getSelectedNodes()[i];
						if (graph.nodes[nodeID].inSubNet)
							subEmpty = false;
					}

					if (subEmpty)
						metExploreD3.displayMessage("Warning", "There is no path between the selected nodes !!");
					else {
						var vis = d3.select("#viz").select("#D3viz");
						// If the metabolite is in the subnetwork then
						// opacity is set to 1 and color to red
						vis.selectAll("g.node").filter(function(d) {
							return d.getBiologicalType() == 'metabolite'
						}).filter(function(d) {
							var id = d.getId();
							return graph.nodes[id].inSubNet
						}).selectAll(".metabolite").transition().duration(4000)
								.style("opacity", 1);// .style("stroke-width","2");

						// If the metabolite is NOT in the subnetwork then
						// opacity is set to 0.5 and color to black
						vis.selectAll("g.node").filter(function(d) {
							return d.getBiologicalType() == 'metabolite'
						}).filter(function(d) {
							var id = d.getId();
							return !graph.nodes[id].inSubNet
						}).selectAll(".metabolite").transition().duration(4000)
								.style("stroke", "gray").style("opacity",
										0.25);// .style("stroke-width","2");

						// If the metabolite is in the subnetwork then
						// opacity is set to 1 and color to red
						vis.selectAll("g.node").filter(function(d) {
							return d.getBiologicalType() == 'metabolite'
						}).filter(function(d) {
							var id = d.getId();
							return graph.nodes[id].inSubNet
						}).selectAll("text").transition().duration(4000)
								.style("opacity", 1);// .style("stroke-width","2");

						// If the metabolite is NOT in the subnetwork then
						// opacity is set to 0.5 and color to black
						vis.selectAll("g.node").filter(function(d) {
							return d.getBiologicalType() == 'metabolite'
						}).filter(function(d) {
							var id = d.getId();
							return !graph.nodes[id].inSubNet
						}).selectAll("text").transition().duration(4000)
								.style("opacity", 0.25);// .style("stroke-width","2");

						// vis.selectAll("g.node").filter(function(d) {var
						// id=d.getId(); return !graph.nodes[id].inSubNet})
						// .transition().duration(4000).style("opacity",0.5);//.style("stroke-width","2");

						vis
								.selectAll("g.node")
								.filter(function(d) {
									return d.getBiologicalType() == 'reaction'
								})
								.filter(
										function(d) {
											var id = d.getId();
											var backID = d.getId() + "_back";
											if (graph.nodes[backID] == undefined)
												return graph.nodes[id].inSubNet;
											else
												return (graph.nodes[id].inSubNet || graph.nodes[backID].inSubNet)
										}).selectAll(".reaction").transition()
								.duration(4000)
								.style("opacity", 1);// .style("stroke-width","2");

						vis
								.selectAll("g.node")
								.filter(function(d) {
									return d.getBiologicalType() == 'reaction'
								})
								.filter(
										function(d) {
											var id = d.getId();
											var backID = d.getId() + "_back";
											if (graph.nodes[backID] == undefined)
												return !graph.nodes[id].inSubNet;
											else
												return !(graph.nodes[id].inSubNet || graph.nodes[backID].inSubNet)
										}).selectAll('.reaction').transition()
								.duration(4000).style("stroke", "gray")
								.style("opacity", 0.25);// .style("stroke-width","2");

						vis
								.selectAll("g.node")
								.filter(function(d) {
									return d.getBiologicalType() == 'reaction'
								})
								.filter(
										function(d) {
											var id = d.getId();
											var backID = d.getId() + "_back";
											if (graph.nodes[backID] == undefined)
												return graph.nodes[id].inSubNet;
											else
												return (graph.nodes[id].inSubNet || graph.nodes[backID].inSubNet)
										}).selectAll("text").transition()
								.duration(4000).style("opacity", 1);// .style("stroke-width","2");

						vis
								.selectAll("g.node")
								.filter(function(d) {
									return d.getBiologicalType() == 'reaction'
								})
								.filter(
										function(d) {
											var id = d.getId();
											var backID = d.getId() + "_back";
											if (graph.nodes[backID] == undefined)
												return !graph.nodes[id].inSubNet;
											else
												return !(graph.nodes[id].inSubNet || graph.nodes[backID].inSubNet)
										}).selectAll("text").transition()
								.duration(4000).style("opacity", 0.25);// .style("stroke-width","2");

						vis
								.selectAll("path.link")
								.filter(
										function(d) {
											var source = d.source.getId();
											var target = d.target.getId();
											if (d.source.getBiologicalType() == 'reaction') {
												var back = source + "_back";
												if (graph.nodes[back] == undefined)
													return (graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
												else
													return (graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
															|| (graph.nodes[back].inSubNet && graph.nodes[target].inSubNet)
											} else {
												var back = target + "_back";
												if (graph.nodes[back] == undefined)
													return (graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
												else
													return (graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
															|| (graph.nodes[source].inSubNet && graph.nodes[back].inSubNet)
											}

										})

								.transition().duration(4000)
								.style("opacity", 1);// .style("stroke-width","2");

						vis
								.selectAll("path.link")
								.filter(
										function(d) {
											var source = d.source.getId();
											var target = d.target.getId();
											if (d.source.getBiologicalType() == 'reaction') {
												var back = source + "_back";
												if (graph.nodes[back] == undefined)
													return !(graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
												else
													return !(graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
															&& !(graph.nodes[back].inSubNet && graph.nodes[target].inSubNet)
											} else {
												var back = target + "_back";
												if (graph.nodes[back] == undefined)
													return !(graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
												else
													return !(graph.nodes[source].inSubNet && graph.nodes[target].inSubNet)
															&& !(graph.nodes[source].inSubNet && graph.nodes[back].inSubNet)
											}

										}).transition().duration(4000)
								.style("stroke", "gray").style("opacity",
										0.25);// .remove();//.style("stroke-width","2");
					}
				}
				if(session!=undefined)  
				{
					if(force!=undefined)  
					{		
						if(metExploreD3.GraphNetwork.isAnimated("viz")== "true")
							force.start();
					}	
				}
		    	metExploreD3.hideMask(myMask);
	    	}, 10);
		}
	},

	/** ******************************************* */
	/** *************************************** */
	// BINDING BETWEEN CYTOSCAPE AND GRAPH
	/** *************************************** */
	/** ******************************************* */
	// Tell if a node is the back version of a reaction
	isBackReaction : function(id) {
		if (id.indexOf("_back") != -1)
			return true;
		else
			return false;
	},
	// Based on the reaction id
	// return the reaction id without the _back mention
	getReactionIdWithoutBack : function(id) {
		// if it is a back version,
		if (metExploreD3.GraphFunction.isBackReaction(id))
			id = id.replace("_back", "");
		return id;
	},

	/** ******************************************************************************* */
	/** *************************************************************************** */
	// GRAPH STRUCTURE AND ALGORITHMS ---- SHOULD BE ADDED TO
	// THE GRAPH LIBRARY !
	/** *************************************************************************** */
	/** ******************************************************************************* */

	/***********************************************************
	 * / In order to speed up the computation a graph structure
	 * is used. / A graph is created corresponding to the
	 * metabolic network as displayed in Cytoscape / Algorithms
	 * are applied to this graph and then results are displayed
	 * in Cytoscape window
	 *  / For the graph objects we develop a set of graph
	 * algorithms: / - Get one of the minimal Feedback arc sets / -
	 * Get strongly connected components / - Get leaf nodes in a
	 * graph / - Test if the graph is acyclic or not
	 * /**********************
	 */
	// Returns the inDegree in the graph structure
	nodeInDegree : function(node) {
		var inDegree = 0;
		for (e in node.edges) {
			var other = node.edges[e].source;
			if (other.id != node.id)
				inDegree++;
		}
		return inDegree;
	},

	// Returns the outDegree in the graph structure
	nodeOutDegree : function(node) {

		var outDegree = 0;
		for (e in node.edges) {
			var other = node.edges[e].source;
			if (other.id == node.id)
				outDegree++;
		}
		return outDegree;
	},
	
	/** ********Get Leaf nodes in a graph*********** */
	getLeafs : function(graph) {
		var leafs = new Array();
		for ( var n in graph.nodes) {
			var node = graph.nodes[n];
			// "+this.nodeOutDegree(node));
			if (metExploreD3.GraphFunction.nodeOutDegree(node) == 0)
				leafs.push(node);
		}
		return leafs;
	},

	/** ********Test if the graph is acyclic or not*********** */
	// To test a graph for being acyclic:
	// 1. If the graph has no nodes, stop. The graph is acyclic.
	// 2. If the graph has no leaf, stop. The graph is cyclic.
	// 3. Choose a leaf of the graph. Remove this leaf and all
	// arcs going into the leaf to get a new graph.
	// 4. Go to 1.
	isAcyclic : function(originalGraph) {
		// Create a copy of the graph since we are going to
		// modify the structure by removing nodes
		var graph = new Graph();
		for ( var e in originalGraph.edges) {
			var edge = originalGraph.edges[e];
			graph.addEdge(edge.source.id, edge.target.id);
		}
		var leafs = metExploreD3.GraphFunction.getLeafs(graph);
		while (leafs.length != 0
				&& Object.keys(graph.nodes).length != 0) {
			var node = leafs.pop();
			graph.removeNode(node);
			leafs = metExploreD3.GraphFunction.getLeafs(graph);
		}
		if (Object.keys(graph.nodes).length == 0)
			return true;
		if (leafs.length == 0)
			return false;
	},
	
	/** ********Get one of the Minimal FAS*********** */
	// A set of edges whose removal makes the digraph acyclic is
	// commonly known as a feedback arc set (FAS)
	// The following algorithm returns T wich is a minimal FAS
	// S={}
	// Sg =new graph
	// T={}
	// for all edges e in the graph
	// add e to Sg
	// if Sg acyclic
	// add e to S
	// else
	// remove e from Sg
	// add e to T
	// return T
	getMinimalFAS : function(graph) {
		var S = new Array();
		var Sg = new Graph();
		var T = new Array();
		for (e in graph.edges) {
			var edge = graph.edges[e];
			Sg.addEdge(edge.source.id, edge.target.id);
			if (metExploreD3.GraphFunction.isAcyclic(Sg))
				S.push(edge);
			else {
				Sg.removeEdge(edge);
				T.push(edge);
			}
		}
		return T;
	},

	/*
		/** ********Get strongly connected components*********** */

		// Tarjan algorithm to detect all strongly connected
		// components in a graph.
		// The method will return an array of arrays containing all
		// the strongly connected component nodes.
		// algorithm tarjan is
		// input: graph G = (V, E)
		// output: set of strongly connected components (sets of
		// vertices)
		// index := 0
		// S := empty
		// for each v in V do
		// if (v.index is undefined) then
		// strongconnect(v)
		// end if
		// end for
		// function strongconnect(v)
		// // Set the depth index for v to the smallest unused index
		// v.index := index
		// v.lowlink := index
		// index := index + 1
		// S.push(v)
		// // Consider successors of v
		// for each (v, w) in E do
		// if (w.index is undefined) then
		// // Successor w has not yet been visited; recurse on it
		// strongconnect(w)
		// v.lowlink := min(v.lowlink, w.lowlink)
		// else if (w is in S) then
		// // Successor w is in stack S and hence in the current SCC
		// v.lowlink := min(v.lowlink, w.index)
		// end if
		// end for
		//     // If v is a root node, pop the stack and generate an SCC
		//     if (v.lowlink = v.index) then
		//       start a new strongly connected component
		//       repeat
		//         w := S.pop()
		//         add w to current strongly connected component
		//       until (w = v)
		//       output the current strongly connected component
		//     end if
		//   end function

	getStronglyConnectedComponents : function(graph) {
		if (graph == null)
			graph = this.createGraph(false);
		var S = new Array();
		var index = 0;
		var scc = new Array();
		for (n in graph.nodes) {
			var v = graph.nodes[n];
			v.index = undefined;
			v.lowlink = Number.MAX_VALUE;
		}
		for (n in graph.nodes) {
			var v = graph.nodes[n];
			if (v.index == undefined)
				metExploreD3.GraphFunction.strongconnect(v, graph, index, S, scc);
		}
		return scc;
	},

	strongconnect : function(v, graph, index, S, scc) {
		v.index = index;
		v.lowlink = index;
		index = index + 1;
		S.push(v);
		for (e in v.edges) {
			var w = v.edges[e].target;
			if (w.id != v.id) {
				if (w.index == undefined) {
					metExploreD3.GraphFunction.strongconnect(w, graph, index, S, scc);
					v.lowlink = Math.min(v.lowlink, w.lowlink);
				} else {
					if (S.indexOf(w) != undefined) {
						v.lowlink = Math.min(v.lowlink,
								w.lowlink);
					}
				}
			}
		}
		if (v.lowlink == v.index) {
			var comp = new Array();
			var w = S.pop();
			while (w.id != v.id) {
				comp.push(w);
				var w = S.pop();
			}
			comp.push(w);
			scc.push(comp);
		}
	},

	//IN PROGRESS !
	//Function to extract FAS with selected compounds as input and outputs
	getMinimalFASstory : function(graph, selectedNodesID) {
		//console.log("Graph is acyclic "+this.isAcyclic(graph));
		var S = new Array();
		var Sg = new Graph();
		var T = new Array();
		//Order the edge that can be removed
		//Edge connecting higly connected nodes first
		var maxValue = graph.edges.length;
		for (e in graph.edges) {
			var edge = graph.edges[e];
			var weight = 0;
			if (selectedNodesID.length > 0) {
				if (selectedNodesID.indexOf(edge.source.id) == -1)
					weight = weight + maxValue;
				if (selectedNodesID.indexOf(edge.target.id) == -1)
					weight = weight + maxValue;
			}
			weight = weight
					- Math.max(edge.source.edges.length, weight
							+ edge.target.edges.length);
			// weight=weight+edge.target.edges.length;
			edge.weight = weight;
		}

		graph.edges.sort(function(obj1, obj2) {
			return obj1.weight - obj2.weight;
		});

		for (e in graph.edges) {
			var edge = graph.edges[e];
			Sg.addEdge(edge.source.id, edge.target.id);
			if (metExploreD3.GraphFunction.isAcyclic(Sg))
				S.push(edge);
			else {
				Sg.removeEdge(edge);
				T.push(edge);
			}
		}
		return T;
	}	

	/**
	 * SUBNETWORK EXTRACTION Path-finding algorithm Dijkstra
	 * modified to provide a shortest path impelementation
	 * worst-case running time is O((|E| + |V|) · log |V| ) thus
	 * better than Bellman-Ford for sparse graphs (with less
	 * edges), but cannot handle negative edge weights
	 * 
	 * Based on Dracula graph library Various algorithms and
	 * data structures, licensed under the MIT-license. (c) 2010
	 * by Johann Philipp Strathausen <strathausen@gmail.com>
	 * http://strathausen.eu
	 */
	/*
		// subnetwork: function(){
		// var graph=this.extractSubNetwork();
		// var session=this.getNetworkVizSession();
		// console.log("Graph computation done");
		// var subEmpty=true;
		// for(var i in
		// this.getNetworkVizSession().getSelectedNodes()){
		// var
		// nodeID=this.getNetworkVizSession().getSelectedNodes()[i];
		// if (graph.nodes[nodeID].inSubNet)
		// subEmpty=false;
		// }
		// if(subEmpty)
		// Ext.Msg.alert("Warning","There is no path between the
		// selected nodes !!");
		// else
		// {
		// var vis = d3.select("body").select("#D3viz");
		// vis.selectAll("g.node").filter(function(d) {return
		// d.getBiologicalType() =='metabolite' }).filter(function(d)
		// {var id=d.getId(); return graph.nodes[id].inSubNet})
		// .selectAll("circle")
		// .transition().duration(4000).style("stroke","red").style("stroke-width","2");
		// vis.selectAll("g.node").filter(function(d) {return
		// d.getBiologicalType() =='reaction' })
		// .filter(function(d) {
		// var id=d.getId();
		// var backID=d.getId()+"_back";
		// if (graph.nodes[backID]==undefined)
		// return graph.nodes[id].inSubNet;
		// else
		// return
		// (graph.nodes[id].inSubNet||graph.nodes[backID].inSubNet)})
		// .selectAll("rect")
		// .transition().duration(4000).style("stroke","red").style("stroke-width","2");
		// vis.selectAll("path.link")
		// .filter(function(d){
		// var source=d.source.getId();
		// var target=d.target.getId();
		// console.log(d.source.getId());
		// if(d.source.getBiologicalType() =='reaction')
		// {
		// var back=source+"_back";
		// if(graph.nodes[back]==undefined)//The source is a
		// reaction and is not reversible then look for
		// source-target
		// return
		// (graph.nodes[source].inSubNet&&graph.nodes[target].inSubNet)
		// else//the source is reversible then look for source
		// target and source_back target
		// {
		// console.log("---"+graph.nodes[source].inSubNet&&graph.nodes[target].inSubNet)||(graph.nodes[back].inSubNet&&graph.nodes[target].inSubNet)
		// return
		// (graph.nodes[source].inSubNet&&graph.nodes[target].inSubNet)||(graph.nodes[back].inSubNet&&graph.nodes[target].inSubNet)
		// }
		// }
		// else
		// {
		// var back=target+"_back";
		// if(graph.nodes[back]==undefined)//The target is a
		// reaction and is not reversible
		// return
		// (graph.nodes[source].inSubNet&&graph.nodes[target].inSubNet)
		// else
		// {
		// console.log("---"+graph.nodes[source].inSubNet&&graph.nodes[target].inSubNet)||(graph.nodes[source].inSubNet&&graph.nodes[back].inSubNet);
		// return
		// (graph.nodes[source].inSubNet&&graph.nodes[target].inSubNet)||(graph.nodes[source].inSubNet&&graph.nodes[back].inSubNet)
		// }
		// }
		// })
		// .transition().duration(4000).style("stroke","red").style("stroke-width","2");
		// }
		// },
	*/
}