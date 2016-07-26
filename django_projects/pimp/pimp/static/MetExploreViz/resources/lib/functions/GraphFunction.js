/**
 * @author MC
 * @description : Basic functions
 */
metExploreD3.GraphFunction = {
    
    /*******************************************
    * Convert hexa in rgb  
    * @param {} r : Red  
    * @param {} g : green  
    * @param {} b : Bleu
    */
    // Hierarchical drawing of the current cytoscape network
	// It uses the default algorithm provided by Cytoscape
	// Should be better to used Sugyiama algorithm
	// !!!!!!!!!------- For the progress bar, event is catched
	// but nothing displayed.....???????
	hierarchicalDrawing : function() {
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