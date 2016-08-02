/*
 *
 *  (c) 2013 Philipp Strathausen <strathausen@gmail.com>, http://strathausen.eu
 *  Contributions by Jake Stothard <stothardj@gmail.com>.
 *
 *  based on Dracula Graph Layout and Drawing Framework 0.0.3alpha
 *  (c) 2010 Philipp Strathausen <strathausen@gmail.com>, http://strathausen.eu
 *  Contributions by Jake Stothard <stothardj@gmail.com>.
 *
 *  based on the Graph JavaScript framework, version 0.0.1
 *  (c) 2006 Aslak Hellesoy <aslak.hellesoy@gmail.com>
 *  (c) 2006 Dave Hoover <dave.hoover@gmail.com>
 *
 *  Ported from Graph::Layouter::Spring in
 *    http://search.cpan.org/~pasky/Graph-Layderer-0.02/
 *  The algorithm is based on a spring-style layouter of a Java-based social
 *  network tracker PieSpy written by Paul Mutton <paul@jibble.org>.
 *
 *  This code is freely distributable under the MIT license. Commercial use is
 *  hereby granted without any cost or restriction.
 *
 *  Links:
 *
 *  Graph Dracula JavaScript Framework:
 *      http://graphdracula.net
 *
 /*--------------------------------------------------------------------------*/
 
/**
	A node is defined by its id. The id is unique.
**/

var AbstractEdge = function() {
}
 AbstractEdge.prototype = {
    hide: function() {
        this.connection.fg.hide();
        this.connection.bg && this.bg.connection.hide();
    }
};
var EdgeFactory = function() {
    this.template = new AbstractEdge();
    this.template.style = new Object();
    this.template.style.directed = false;
    this.template.weight = 1;
};
EdgeFactory.prototype = {
    build: function(source, target) {
        var e = jQuery.extend(true, {}, this.template);
        e.source = source;
        e.target = target;
        return e;
    }
};





/*
 * Graph
 */
var Graph = function() {
    this.nodes = {};
    //this.nodes =new Array();
    this.edges = [];
    //this.edges = new Array();
    this.edgeFactory = new EdgeFactory();
};


Graph.prototype = {
    /* 
     * add a node
     * @id          the node's ID (string or number)
     * @content     (optional, dictionary) can contain any information that is
     *              being interpreted by the layout algorithm or the graph
     *              representation
     */
    addNode: function(id, content) {
        /* testing if node is already existing in the graph */
        if(this.nodes[id] == undefined) {        	
        	this.nodes[id] = new Graph.Node(id, content);
        }
        var node=this.nodes[id];
        return node;
    },

    addEdge: function(source, target, style) {
        var s = this.addNode(source);
        var t = this.addNode(target);
        var edge = this.edgeFactory.build(s, t);
        jQuery.extend(edge.style,style);
        s.edges.push(edge);
        this.edges.push(edge);
        // NOTE: Even directed edges are added to both nodes.
        t.edges.push(edge);
    },
    
    //copy in a new graph the current one
    copy:function()
    {
    	var graph=new Graph();
		for(var e in this.edges)
		{
			var edge=this.edges[e];
			graph.addEdge(edge.source.id,edge.target.id);
		}
		for(var n in this.nodes)
		{
			if(this.nodes[n].layer!=undefined)
				graph.nodes[n].layer=this.nodes[n].layer;
		}
		return graph;
    },
  
    /**
    Under construction, to be checked !!!
    **/
    removeEdge:function(edge)
    {
        for(var n in this.nodes)
        {
            var node=this.nodes[n];
            for(var e in node.edges)
            {
            	var eToTest=node.edges[e];
            	if(eToTest.source.id==edge.source.id&&eToTest.target.id==edge.target.id)
               		node.edges.splice(e, 1);            	
            }
        }
        var edgeIndex=this.edges.indexOf(edge);
        this.edges.splice(edgeIndex, 1);
    },
    /**
    Given a set of edges, remove them from the graph
    **/
    removeEdges:function(edges)
    {
        for(e in edges)
        {
            this.removeEdge(edges[e]);
        }
    },

    getNode:function(nodeId)
    {
    	return this.nodes[nodeId];
    },

    removeNode: function(node) {
        var edgesToRemove=[];
       // console.log(node);
        //console.log("node.edges",node.edges);
        for(var x=0;x<node.edges.length;x++)
        {
            var edge=node.edges[x];
            edgesToRemove.push(edge);
        }
        for(e in edgesToRemove)
        {
            this.removeEdge(edgesToRemove[e]);
        }

        delete this.nodes[node.id];
    },

    /**
    Return the leafs of the graph
    **/
	getLeafs:function()
	{
		var leafs=new Array();
		for(var n in this.nodes)
		{
			var node=this.nodes[n];
			if(this.nodeOutDegree(node)==0)
				leafs.push(node);			
		}
		return leafs;
	},
	//Returns the inDegree in the graph structure
	nodeInDegree:function(node)
	{
		var inDegree=0;
		for(e in node.edges)
			{
				var other = node.edges[e].source;
				if (other.id!=node.id)
					inDegree++;
			}
		return inDegree;
	},

	//Returns the outDegree in the graph structure
	nodeOutDegree:function(node)
	{
		var outDegree=0;
		for(e in node.edges)
			{
				var other = node.edges[e].source;
				if (other.id==node.id)
					outDegree++;
			}
		return outDegree;
	},



		/***
		This method is based on the Sugiyama framework as described in Healy and Nikolov chapter published in 2013
		Hierarchical drawing steps:
		1 CYCLE REMOVAL: ok using getMinimalFAS edges and removing them.
		2 LAYER ASSIGNMENT ("note that section 13.3.4 Layer-Assignment with Long Vertices" describes how to work with different sizes of nodes, but it's hard then to use the following optimisations: step 3 4 and 5)
		3 Edge Concentration (mentioned to be optional) for the moment I skip this one
		4 Vertex Ordering
		5 x-Coordinate Assignment
		***/

	hierarchicalDrawing:function()
	{
		//1 CYCLE REMOVAL: ok using getMinimalFAS edges and removing them.
		var dag=this.extractDAG();
		//2 LAYER ASSIGNMENT
		dag.layerAssignment();
		//3 EDGE CONCENTRATION (mentioned to be optional) for the moment I skip this one

		//4 VERTEX ORDERING. Pb to fix: last (top) layer may not be welled ordered.
		dag.createGraphWithBends();
		dag.vertexOrdering();
		//5 X-COORDINATE ASSIGNMENT
		//dag.xOrderShift();

		//put the computed information into the graph
		for(n in this.nodes)
		{
			this.nodes[n].layer=dag.nodes[n].layer;
			this.nodes[n].xOrder=dag.nodes[n].xOrder;
		}
	},

	xOrderShift:function()
	{
		//layers are going from 0 to x
		var layers=[];
		for(var n in this.nodes)
		{
			var layer=this.nodes[n].layer;
			//console.log(layer);
			if (layers[layer]==undefined)
				layers[layer]=new Array();
			layers[layer].push(this.nodes[n]);
		}
		varMaxLayerSize=0;
		for(var l in layers)
		{
			if(varMaxLayerSize<layers[l].length)
				varMaxLayerSize=layers[l].length
		}

		for(var i=0;i<layers.length;i++)
		{
			var currentLayerSize=layers[i].length;
			for(n in layers[i])
			{
				var u=layers[i][n];
				u.xOrder=u.xOrder+Math.floor(varMaxLayerSize/currentLayerSize);
			}
		}
		// for(var i=1;i<layers.length;i++)
		// {
		// 	for(n in layers[i])
		// 	{
		// 		var u=layers[i][n];
		// 		var nEdges=0;
		// 		var sumPos=0;
		// 		for(e in u.edges)
		// 		{
		// 			if(u.edges[e].source.id==u.id)
		// 			{
		// 				var v=u.edges[e].target;
		// 			}
		// 			else
		// 			{
		// 				var v=u.edges[e].source;
		// 			}
		// 			if(v.layer==i-1)
		// 			{
		// 				nEdges++;
		// 				sumPos=sumPos+v.xOrder;
		// 			}
		// 		}
		// 		if(nEdges!=0)
		// 			u.xOrder=Math.floor(sumPos/nEdges);
		// 	}
		//}


	},

	///Add bend nodes to a layered graph
	// for each edge,if the layer of the source and the target have a difference more than 1
	// 		Then add bends
	//will return the new graph with bend nodes and corresponding edges
	createGraphWithBends:function()
	{
		//var cDag=this.copy();
		for(var e in this.edges)
		{
			if(Math.abs(this.edges[e].source.layer-this.edges[e].target.layer)>1)
			{
				//console.log("---- Add bend nodes for edge "+this.edges[e].source.id+","+this.edges[e].target);
				this.addBendNodes(this.edges[e]);
			}
		}
	},

	addBendNodes:function(edge)
	{
		console.log("---- Add bend nodes for edge "+edge.source.id+","+edge.target.id);
		//add the bend node and corresponding edges
		//for edge (u,v) (layer u is necesseraly before layer v)
		//	currentNode=u
		//	for (l=layer(u)-1 and l>layer(v); l--)
		//		add node b "b+u+v+l"
		//		set node.layer=l
		//		add edge (currentNode,b)
		//		currentNode=b
		//	add the final edge (currentNode,v)
		var u=edge.source;
		var v=edge.target;
		var currentNode=u;
		for(var l=u.layer-1;l>v.layer;l--)
		{
			//console.log("Add node "+"b_"+u.id+"-"+v.id+"_"+l);
			var b=this.addNode("b_"+u.id+"-"+v.id+"_"+l);
			b.layer=l;
			this.addEdge(currentNode.id,b.id);
			currentNode=b;
		}
		this.addEdge(currentNode.id,v.id);
	},

	//for each layer, will create an ordering of its nodes
	vertexOrdering:function()
	{
		//layers are going from 0 to x
		var layers=[];
		for(var n in this.nodes)
		{
			var layer=this.nodes[n].layer;
			//console.log(layer);
			if (layers[layer]==undefined)
				layers[layer]=new Array();
			layers[layer].push(this.nodes[n]);
		}
		//set a random xOrder for each node per layer
		for(l in layers)
		{
			var layer=layers[l];
			var xOrder=0;
			for (n in layer)
			{
				layer[n].xOrder=xOrder;
				xOrder++;
			}
		}
		//console.log("before "+this.getTotalCrossings());
		//Create he crossing matrix
		//Use a heuristic to improve the overall crossing
		//Use the median method to determine the initial ordering
		//Use an adjacent exchange method to refine
		for(l in layers)
		{
			var layer=layers[l];
			this.greedySwitch(layer);
		}
		///console.log("after "+this.getTotalCrossings());
	},

	greedySwitch:function(layer)
	{
		var numberOfCrossings=0;
		///console.log(layer.length);
		//console.log(layer);
		if (layer.length==1)
			return numberOfCrossings;
		else
		{
			for(var i=0;i<layer.length;i++)
			{
				for(var j=i+1;j<layer.length;j++)
					{
						numberOfCrossings=numberOfCrossings+this.getCrossingNumber(layer[i],layer[j]);
					}
			}
			var crossingBeforeRun=numberOfCrossings;
			var crossingAfterRun=0;
			//console.log("before "+crossingBeforeRun);
			while(crossingBeforeRun!=crossingAfterRun)
			{
				crossingBeforeRun=crossingAfterRun;
				crossingAfterRun=0;
				for(var i=0;i<layer.length;i++)
				{
					for(var j=i+1;j<layer.length;j++)
						{
							var u=layer[i];
							var v=layer[j];
							nbij=this.getCrossingNumber(u,v);
							u.xOrder=j;
							v.xOrder=i;
							nbji=this.getCrossingNumber(u,v);
							if(nbji<nbij)
							{
								layer[i]=v;
								layer[j]=u;
								crossingAfterRun=crossingAfterRun+nbji;
								console.log("swap "+u.id+" and "+v.id);
							}
							else
							{
								u.xOrder=i;
								v.xOrder=j;
								crossingAfterRun=crossingAfterRun+nbij;
							}
						}
				}
			}
			//console.log("--"+numberOfCrossings);
			return numberOfCrossings;			
		}
	},

	getTotalCrossings:function()
	{
		var total=0;
		for(n1 in this.nodes)
		{
			var u=this.nodes[n1];
			//console.log("u "+u.id);
			for (n2 in this.nodes)
			{
				var v=this.nodes[n2];
				//console.log("v "+v.id);
				//console.log(this.getCrossingNumber(u,v));
				total=total+this.getCrossingNumber(u,v);
			}
		}
		return total;
	},
	/**
	number of crossings that edges incident to u make with edges incident v, when x1(u)<x1(v)
	number of pairs (u,w) and (v,z) of edges with x2(z)<x2(w)
	**/
	getCrossingNumber:function(u,v)
	{
		var crossNumber=0;
		if((u.xOrder<v.xOrder)&&(u.layer==v.layer))
		{
			for(e1 in u.edges)
			{
				var w;
				if(u.edges[e1].source.id==u.id)
					w=u.edges[e1].target;
				else
					w=u.edges[e1].source;
				for(e2 in v.edges)
				{
					var z;
					if(v.edges[e2].source.id==v.id)
						z=v.edges[e2].target;
					else
						z=v.edges[e2].source;
					//if((w.layer==z.layer==u.layer+1)&&(z.xOrder<w.xOrder))
					if((w.layer>u.layer)&&(z.layer>u.layer)&&(z.xOrder<w.xOrder))
						crossNumber++;
				}
			}
		}
		return crossNumber;
	},


	/**********Test if the graph is acyclic or not************/
	// To test a graph for being acyclic:
	//     1. If the graph has no nodes, stop. The graph is acyclic.
	//     2. If the graph has no leaf, stop. The graph is cyclic.
	//     3. Choose a leaf of the graph. Remove this leaf and all arcs going into the leaf to get a new graph.
	//     4. Go to 1.
	isAcyclic:function()
	{
		//Create a copy of the graph since we are going to modify the structure by removing nodes
		var newGraph=this.copy();
		var leafs=newGraph.getLeafs();
		while(leafs.length!=0 && Object.keys(newGraph.nodes).length!=0)
		{
			var node=leafs.pop();
			newGraph.removeNode(node);
			leafs=newGraph.getLeafs();
		}
		if(Object.keys(newGraph.nodes).length==0)
			return true;
		if(leafs.length==0)
			return false;
	},
		/**********Get one of the Minimal FAS************/
	//A set of edges whose removal makes the digraph acyclic is commonly known as a feedback arc set (FAS)
	// The following algorithm returns T wich is a minimal FAS
	// S={}
	// Sg =new graph
	// T={}
	// for all edges e in the graph
	//		add e to Sg
	//		if Sg acyclic
	//			add e to S
	//		else
	//			remove e from Sg
	//			add e to T
	// return T
	getMinimalFAS:function()
		{
			var S=new Array();
			var Sg=new Graph();
			var T=new Array();
			for(e in this.edges)
			{
				var edge=this.edges[e];
				Sg.addEdge(edge.source.id,edge.target.id);
				if(Sg.isAcyclic())
					S.push(edge);				
				else
				{
					Sg.removeEdge(edge);
					T.push(edge);
				}
			}
			return T;
		},

	extractDAG:function()
	{
		//Create a copy of the graph since we are going to modify the structure by removing nodes
		var dag=this.copy();
		var edgesToRemove=dag.getMinimalFAS();
		dag.removeEdges(edgesToRemove);
		return dag;
	},

	/**
	This is the heuristic proposed by Tarassov et al. in 2004.
	It is creating a layering with a Minimum width based on DAG (if graph is not a DAG, extractDAG method has to be applied)
	This algorithm is linear.
	It is achieved through the min-width method with parameters W taking values {1,2,3,4} and c taking values {1,2} (as suggested by authors)
	Then the narrowest one is chosen.
	Finally, an improvement by promotion of vertices is applied.
	**/
	layerAssignment:function()
	{
		var minWidth=Number.MAX_VALUE;
		finalC=-1;
		finalW=-1;
		for(var c=1;c<=2;c++)
		{
			for(var W=1;W<=4;W++)
			{
				var testDAG=this.copy();
				var width=testDAG.minWidthLayerAssignment(W,c);
				if (width<minWidth)
				{
					finalC=c;
					finalW=W;
					minWidth=width;
				}

			}
		}
		//console.log(" width "+minWidth+" chosen w "+finalW+" chosen c "+finalC);
		this.minWidthLayerAssignment(finalW,finalC);
		//Finally, an improvement by promotion of vertices is applied.
		this.vertexPromotion();
		//If there is vertex promotion it may be that there is no first layer anymore then we have to shift the layers to start at one
		this.shiftLayers();
	},

	shiftLayers:function()
	{
		var minLayer=Number.MAX_VALUE;
		for(n in this.nodes)
		{
			var layer=this.nodes[n].layer;
			if (layer<minLayer)
				minLayer=layer;
		}
		// var shift =minLayer-1;
		// if (shift!=0)
		// {
			for(n in this.nodes)
			{
				this.nodes[n].layer=this.nodes[n].layer-minLayer;
			}
		// }
	},

	/**
	PromoteVertex(v) by Nikolov and Tarasov 2006
	Require: A layered DAG G = (V;E) with the layering information stored in a global
	vertex array of integers called layering; a vertex v in V .
	dummydiff=0
	for all u in N-G (v) do
		if layering[u] == layering[v] + 1 then
			dummydiff dummydiff+ PromoteVertex(u)
		end if
	end for
	layering[v]=layering[v] + 1
	dummydiff=dummydiff-N-G(v) + N+G(v)
	return dummydiff
	**/

	promoteVertex:function(v)
	{
		//console.log("Promote vertex "+v.id);
		var dummydiff=0;
		var neigh=this.getInNodesTo(v);
		for (x in neigh)
		{
			var u=neigh[x];
//			console.log("----"+u.id);
			if(u.layer==v.layer+1)
				dummydiff=dummydiff+this.promoteVertex(u);
		}
		v.layer=v.layer+1;
		dummydiff=dummydiff-this.getInNodesTo(v).length+this.getOutNodesFrom(v).length;
		//console.log("----for "+v.id+" dummydiff is "+dummydiff);
		return dummydiff;
	},

	/**
	Vertex-Promotion Heuristic by Nikolov and Tarasov 2006
	Require: G = (V;E) is a layered DAG; a valid layering of G is stored in a global vertex
	array called layering.
	layeringBackUp=layering
	repeat
		promotions=0
		for all v in V do
			if d-(v) > 0 then
				if PromoteVertex(v) < 0 then
					promotions=promotions + 1
					layeringBackUp=layering
				else
					layering=layeringBackUp
				end if
			end if
		end for
	until promotions = 0
	**/

	vertexPromotion:function()
	{

		var backUpDag=this.copy();
		var promotions=-1;
		while(promotions!=0)
		{
			promotions=0;
			for(x in this.nodes)
			{
				var v=this.nodes[x];
				//console.log("***for "+v.id);
				if(this.getInNodesTo(v).length>0)
				{
					// console.log("Promote for "+v.id+" is "+this.promoteVertex(v));
					// console.log("Promote for "+v.id+" is "+this.promoteVertex(v));
					// console.log(this.promoteVertex(v)<0);
					//console.log("Compute promotion for "+v.id);
					var promotionVal=this.promoteVertex(v);
					//console.log("Promote for "+v.id+" is "+promotionVal);
					var promotion=(promotionVal<0)
					//console.log("there is a promotion "+promotion);
					//if(this.promoteVertex(v)<0)
					if(promotion)
					{
						//console.log("******for "+v.id+" there is an improvement");
						promotions=promotions+1;
						backUpDag=this.copy();
					}
					else
					{
						for(n in backUpDag.nodes)
						{
							//console.log(this.nodes[n].layer+"---"+backUpDag.nodes[n].layer);
							this.nodes[n].layer=backUpDag.nodes[n].layer;
						}
					}
				}
				else
					console.log("--- in degree is below zero");
			}
		}
	},
	

	/**
	U={}; Z={}
	currentLayer=1; widthCurrent=0; widthUp=0
	while U != V do
		Select vertex v in V\U with N+G(v) C or equal to Z and ConditionSelect (node with the highest outdegree)
		if v has been selected then
			Assign v to the layer with a number currentLayer
			U=U union {v}
			widthCurrent=widthCurrent-d+(v) + 1
			widthUp=widthUp + d-(v)
		end if
		if no vertex has been selected OR ConditionGoUp then
			currentLayer=currentLayer + 1
			Z=Z union U
			widthCurrent=widthUp
			widthUp=0
		end if
	end while
	**/
	minWidthLayerAssignment:function(W,c)
	{
		var maxWidth=0;
		var V=new Array();
		for(var n in this.nodes)
		{V.push(this.nodes[n]);this.nodes[n].layer=-1;}
		var U=new Array();
		var Z=new Array();
		var currentLayer=1;
		var widthCurrent=0;
		var widthUp=0;

		while(!($(U).not(V).length == 0 && $(V).not(U).length == 0))//test if U!=V using JQuery
		{
			//Select vertex v in V\U with N+G(v) inclued or equal to Z and with maximum outdegree
			//build V\U
			var VminusU = $.grep(V,function(x) {return $.inArray(x, U) < 0});
			//get the nodes with N+G(v) inclued or equal to Z
			var candidates=new Array();
			for(n in VminusU)
			{
				var Nplusn=this.getOutNodesFrom(VminusU[n]);
				if($(Nplusn).not(Z).length==0)
					candidates.push(VminusU[n]);
			}
			var candidateFound=false;
			var vOutDegree=Number.MAX_VALUE;
			if(candidates.length!=0)
			{
				candidateFound=true;
				//select the highest degree node in V\U
				var v=this.quickDegreeSort(candidates).pop();
				v.layer=currentLayer;
				U.push(v);
				vOutDegree=this.getOutNodesFrom(v);
				widthCurrent=widthCurrent-this.getOutNodesFrom(v).length+1;
				widthUp=widthUp+this.getInNodesTo(v).length;		
			}
			if(!candidateFound || (widthCurrent>=W && vOutDegree<1) || widthUp>=c*W)
			{
				currentLayer=currentLayer+1;
				for(n in U)
				{
					Z.push(U[n]);
				}
				if (widthCurrent>maxWidth)
					maxWidth=widthCurrent;
				widthCurrent=widthUp;
				widthUp=0;
			}
		}
		return maxWidth;
	},

	getOutNodesFrom:function(node)
	{
		var out=new Array();
		for(var e in node.edges)
		{
			if(node.edges[e].target.id!=node.id)
				out.push(node.edges[e].target);
		}
		return out;
	},

	getInNodesTo:function(node)
	{
		var inNodes=new Array();
		for(var e in node.edges)
		{
			if(node.edges[e].source.id!=node.id)
				inNodes.push(node.edges[e].source);
		}
		return inNodes;
	},







	/**********Get strongly connected components************/

//Tarjan algorithm to detect all strongly connected components in a graph.
//The method will return an array of arrays containing all the strongly connected component nodes.

// algorithm tarjan is
//   input: graph G = (V, E)
//   output: set of strongly connected components (sets of vertices)
//   index := 0
//   S := empty
//   for each v in V do
//      if (v.index is undefined) then
//       strongconnect(v)
//     end if
//   end for
//   function strongconnect(v)
//     // Set the depth index for v to the smallest unused index
//     v.index := index
//     v.lowlink := index
//     index := index + 1
//     S.push(v)

//     // Consider successors of v
//      for each (v, w) in E do
//        if (w.index is undefined) then
//          // Successor w has not yet been visited; recurse on it
//         strongconnect(w)
//         v.lowlink  := min(v.lowlink, w.lowlink)
//       else if (w is in S) then
//          // Successor w is in stack S and hence in the current SCC
//          v.lowlink  := min(v.lowlink, w.index)
//       end if
//     end for

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
	getStronglyConnectedComponents:function()
	{
	// 	if(graph==null)
	// 		graph=this.createGraph(false);
		var S=new Array();
		var index=0;
		var scc=new Array();
		for(n in this.nodes)
		{
			var v=this.nodes[n];
			v.index=undefined;
			v.lowlink=Number.MAX_VALUE;
		}
		for(n in this.nodes)
		{
			var v=this.nodes[n];
			if(v.index==undefined)
				this.strongconnect(v,index,S,scc);
		}
		return scc;
	},
	strongconnect:function(v,index,S,scc)
	{
		v.index=index;
		v.lowlink=index;
		index=index+1;
		S.push(v);
		for(e in v.edges)
		{
			var w=v.edges[e].target;
			if(w.id!=v.id)
			{
				if(w.index==undefined)
				{
					this.strongconnect(w,index,S,scc);
					v.lowlink=Math.min(v.lowlink,w.lowlink);
				}
				else
				{
					if(S.indexOf(w)!=undefined)
					{
						v.lowlink=Math.min(v.lowlink,w.lowlink);
					}
				}
			}
		}
		if(v.lowlink==v.index)
		{
			var comp=new Array();
			var w=S.pop();
			while(w.id!=v.id)
			{
				comp.push(w);
				var w=S.pop();
			}
			comp.push(w);
			scc.push(comp);
		}
	},
	

		/*
	    Quick Sort:
	        1. Select some random value from the array, the median.
	        2. Divide the array in three smaller arrays according to the elements
	           being less, equal or greater than the median.
	        3. Recursively sort the array containg the elements less than the
	           median and the one containing elements greater than the median.
	        4. Concatenate the three arrays (less, equal and greater).
	        5. One or no element is always sorted.
	    TODO: This could be implemented more efficiently by using only one array object and several pointers.
	*/
	quickDegreeSort:function(nodes) {
	    /* recursion anchor: one element is always sorted */
	    if(nodes.length <= 1) return nodes;
	    /* randomly selecting some value */
	    var midIndex=Math.floor(nodes.length/2);
	    var median = nodes[midIndex];
	    var arr1 = [], arr2 = [], arr3 = [];
	    for(var i in nodes) {
	        this.nodeOutDegree(nodes[i]) < this.nodeOutDegree(median) && arr1.push(nodes[i]);
	        this.nodeOutDegree(nodes[i]) == this.nodeOutDegree(median) && arr2.push(nodes[i]);
	        this.nodeOutDegree(nodes[i]) > this.nodeOutDegree(median) && arr3.push(nodes[i]);
	    }
	    /* recursive sorting and assembling final result */
	    return this.quickDegreeSort(arr1).concat(arr2).concat(this.quickDegreeSort(arr3));
	}

};

/*
 * Node
 */
Graph.Node = function(id, node){
    node = node || {};
    node.id = id;
    node.edges = [];
    node.hide = function() {
        this.hidden = true;
        this.shape && this.shape.hide(); /* FIXME this is representation specific code and should be elsewhere */
        for(i in this.edges)
            (this.edges[i].source.id == id || this.edges[i].target == id) && this.edges[i].hide && this.edges[i].hide();
    };
    node.show = function() {
        this.hidden = false;
        this.shape && this.shape.show();
        for(i in this.edges)
            (this.edges[i].source.id == id || this.edges[i].target == id) && this.edges[i].show && this.edges[i].show();
    };
    node.getAdjacents = function(){
		return this.edges.map(function(edge){
			if(edge.source.id == node.id)
				return edge.target;
			else
				return edge.source;
		})
	};
    return node;
};
Graph.Node.prototype = {

};




/*
   A simple binary min-heap serving as a priority queue
   - takes an array as the input, with elements having a key property
   - elements will look like this:
        {
            key: "... key property ...", 
            value: "... element content ..."
        }
    - provides insert(), min(), extractMin() and heapify()
    - example usage (e.g. via the Firebug or Chromium console):
        var x = {foo: 20, hui: "bla"};
        var a = new BinaryMinHeap([x,{foo:3},{foo:10},{foo:20},{foo:30},{foo:6},{foo:1},{foo:3}],"foo");
        console.log(a.extractMin());
        console.log(a.extractMin());
        x.foo = 0; // update key
        a.heapify(); // call this always after having a key updated
        console.log(a.extractMin());
        console.log(a.extractMin());
    - can also be used on a simple array, like [9,7,8,5]
 */
function BinaryMinHeap(array, key) {
    
    /* Binary tree stored in an array, no need for a complicated data structure */
    var tree = [];
    
    var key = key || 'key';
    
    /* Calculate the index of the parent or a child */
    var parent = function(index) { return Math.floor((index - 1)/2); };
    var right = function(index) { return 2 * index + 2; };
    var left = function(index) { return 2 * index + 1; };

    /* Helper function to swap elements with their parent 
       as long as the parent is bigger */
    function bubble_up(i) {
        var p = parent(i);
        while((p >= 0) && (tree[i][key] < tree[p][key])) {
            /* swap with parent */
            tree[i] = tree.splice(p, 1, tree[i])[0];
            /* go up one level */
            i = p;
            p = parent(i);
        }
    }

    /* Helper function to swap elements with the smaller of their children
       as long as there is one */
    function bubble_down(i) {
        var l = left(i);
        var r = right(i);
        
        /* as long as there are smaller children */
        while(tree[l] && (tree[i][key] > tree[l][key]) || tree[r] && (tree[i][key] > tree[r][key])) {
            
            /* find smaller child */
            var child = tree[l] ? tree[r] ? tree[l][key] > tree[r][key] ? r : l : l : l;
            
            /* swap with smaller child with current element */
            tree[i] = tree.splice(child, 1, tree[i])[0];
            
            /* go up one level */
            i = child;
            l = left(i);
            r = right(i);
        }
    }
    
    /* Insert a new element with respect to the heap property
       1. Insert the element at the end
       2. Bubble it up until it is smaller than its parent */
    this.insert = function(element) {
    
        /* make sure there's a key property */
        (element[key] == undefined) && (element = {key:element});
        
        /* insert element at the end */
        tree.push(element);

        /* bubble up the element */
        bubble_up(tree.length - 1);
    }
    
    /* Only show us the minimum */
    this.min = function() {
        return tree.length == 1 ? undefined : tree[0];
    }
    
    /* Return and remove the minimum
       1. Take the root as the minimum that we are looking for
       2. Move the last element to the root (thereby deleting the root) 
       3. Compare the new root with both of its children, swap it with the
          smaller child and then check again from there (bubble down)
    */
    this.extractMin = function() {
        var result = this.min();
        
        /* move the last element to the root or empty the tree completely */
        /* bubble down the new root if necessary */
        (tree.length == 1) && (tree = []) || (tree[0] = tree.pop()) && bubble_down(0);
        
        return result;        
    }
    
    /* currently unused, TODO implement */
    this.changeKey = function(index, key) {
        throw "function not implemented";
    }

    this.heapify = function() {
        for(var start = Math.floor((tree.length - 2) / 2); start >= 0; start--) {
            bubble_down(start);
        }
    }
    
    /* insert the input elements one by one only when we don't have a key property (TODO can be done more elegant) */
    for(i in (array || []))
        this.insert(array[i]);
}







// 	/**
// 	Extract a subnetwork based on lightest path length between each pair of selected nodes
// 	it returns a graph where nodes have a subnet attribute telling wether they are in subnet or not
// 	**/
// 	extractSubNetwork: function(){

// 		var cy = $("#cy").cytoscape('get');
// 		// Should be a parameter
// 		var nodeSelection = cy.$('node:selected'); 
// 		if (nodeSelection.length<2)
// 			Ext.Msg.alert("Warning","At least two nodes have to be selected.");
// 		else
// 		{
// 			//Map containing nodes,index values
// 			var selectedNodesIndex={};
// 			for(i=0;i<nodeSelection.length;i++)
// 			{
// 				selectedNodesIndex[nodeSelection[i].data("id")]=i;
// 			}
// 			//Create a matrix containing all the paths
// 			var paths=[];
// 			//for each pair of selected nodes, create an entry in the path matrix
// 			for(i=0;i<nodeSelection.length;i++)
// 			{
// 				paths[i]=[];
// 				for(j=0;j<nodeSelection.length;j++)
// 					paths[i][j]=null;
// 			}
// 			//create the graph structure based on the displayed network
// 			//This graph will contain also backward reactions
// 			var graph=this.createGraph(true);
// 		  	for(var n in graph.nodes)
// 			{
// 		    	graph.nodes[n].inSubNet=false;
// 		    }
// 		    for (var i=0;i<graph.edges.length;i++)
// 		    {
// 		    	graph.edges[i].inSubNet=false;
// 		    }
// 			//For each node in the selection
// 			//	Compute its lightest path to other nodes
// 			for(var i = 0; i < nodeSelection.length; i++ )
// 				{
// 					var nodeI = nodeSelection[i];
// 					var selectedNodeID=nodeI.data("id");
// 					//Since while searching for a path we may find another one
// 	  				//We are going to keep the path already found
// 	  				var jWithPath=new Array();
// 					for(var j=0;j<nodeSelection.length;j++)
// 	  				{
// 	  					if(j!=i)
// 	  					{
// 	  						//if the paths is not already computed
// 	  						if(paths[i][j]==null)
// 	  						{		
// 	  							//If we go through a reaction, we want to avoid going through its back version
// 								var reactionUsed=new Array();
// 	  							//if not, do the computation
// 		  						var nodeJ=nodeSelection[j];
// 		  						var graphNodeJ=nodeJ.data("id");
// 		  						for(var n in graph.nodes)
// 				    			{
// 		    						graph.nodes[n].distance = Infinity;
// 		    						graph.nodes[n].predecessor = null;
// 		    						graph.nodes[n].optimized = false;
// 		    					}	
// 				    			var source=graph.nodes[selectedNodeID];
// 				    			source.distance = 0;
// 				   				/* set of unoptimized nodes, sorted by their distance (but a Fibonacci heap
// 				       			would be better) */
// 				    			var q = new BinaryMinHeap(graph.nodes, "distance");
// 								//pointer to the node in focus
// 							    var node;
// 							    /* get the node with the smallest distance
// 				       			as long as we have unoptimized nodes. q.min() can have O(log n). */
// 				       			var targetReached=false;
// 				       			while((q.min() != undefined) &&(!targetReached))
// 							    {
// 							        /* remove the latest */
// 							        node = q.extractMin();
// 				        			node.optimized = true;
// 							        for(e in node.edges)
// 							        {
// 								    	var other = node.edges[e].target;
// 							            if(other.optimized)
// 							                continue;
// 							            /* look for an alternative route */
// 							            //var alt = node.distance + node.edges[e].weight;
// 							            /*Implementation of the lightest path*/
// 							            /*will penalize high degree nodes*/
// 							            var alt = node.distance + (node.edges.length)*(node.edges.length);
// 							            /* update distance and route if a better one has been found */
// 							            if ((alt < other.distance) && reactionUsed.indexOf(this.getReactionIdWithoutBack(other.id))==-1)
// 							            {
// 							            	/*Add the reaction to the visited ones*/
// 							            	reactionUsed.push(this.getReactionIdWithoutBack(other.id));
// 							                /* update distance of neighbour */
// 							                other.distance = alt;
// 							                /* update priority queue */
// 							                q.heapify();
// 							                /* update path */
// 							                other.predecessor = node;
// 							            }
// 							            if (other.id==nodeJ.data("id"))
// 							            {
// 							            	//if the target is reached then we will stop
// 							            	targetReached=true;
// 							            	paths[i][j]=this.getPathBasedOnPredecessors(graph,nodeJ.data("id"));
// 							            }
// 							            //if the node is a node in the selection list 
// 							            //if there is no corresponding path
// 							            //we add the paths from i to it!
// 							            else
// 							            {
// 							            	var nodeIndex=selectedNodesIndex[other.id];
// 								            if ((nodeIndex!=undefined) && (paths[i][nodeIndex]==null))
// 								            {								            	
// 								            	paths[i][nodeIndex]=this.getPathBasedOnPredecessors(graph,other.id);
// 								            }
// 							            }								            	
// 									}
// 								}
								
// 							}
// 	  					}
// 	  				}
// 	  			}
// 	  		return graph;
// 		}
// 	},





// /**********************************************/
// 	/******************************************/
// 	//BINDING BETWEEN CYTOSCAPE AND GRAPH
// 	/******************************************/
// /**********************************************/

// 	*
// 	Function that will create the graph on which we are going to do the computation
// 	This function create the graph based on the displayed cytoscape network
// 	If reversible=true
// 		For each reversible reactions, we are going to add the backward version of the reaction
// 	else
// 		The graph structure fits the drawing.
// 	*
// 	// createGraph:function(reversible){
// 	// 	var cy = $("#cy").cytoscape('get');
// 	// 	//Graph object coming from the Dracula library
// 	// 	var graph=new Graph();
// 	// 	var eles=cy.elements("node[biologicalType='reaction']");
//  //      	for(var i=0;i<eles.length;i++)
//  //      		{
//  //      			var reaction=eles[i];
//  //      			//add the reaction
//  //      			graph.addNode(reaction.data("id"));
//  //      			//add the backward reaction if reversible
//  //      			var idBack=reaction.data("id")+"_back";
//  //      			if(reversible)
// 	//       			if(reaction.data("reversible"))
// 	// 	      			graph.addNode(idBack);
//  //      			//for each product, add the edge
//  //      			var products=this.getDirectedNeighborsOUT(reaction);     				
//  //      			for(var j=0;j<products.length;j++)
//  //      				{
//  //      					graph.addEdge(reaction.data("id"),products[j].data("id"));
//  //      					if(reaction.data("reversible"))
//  //      						if(reversible)
// 	//       						graph.addEdge(products[j].data("id"),idBack);
//  //      				}
//  //      			//for each substrate, add the edge
//  //      			var substrates=this.getDirectedNeighborsIN(reaction);
//  //      			for(var j=0;j<substrates.length;j++)
//  //      				{
//  //      					graph.addEdge(substrates[j].data("id"),reaction.data("id"));
//  //      					if(reversible)
// 	//       					if(reaction.data("reversible"))
//  //    	  						graph.addEdge(idBack,substrates[j].data("id"));
//  //      				}
      				
//  //      		}
// 	// 	return graph;
// 	// },




// /**********************************************************************************/
// 	/******************************************************************************/
// 	//GRAPH STRUCTURE AND ALGORITHMS ---- SHOULD BE ADDED TO THE GRAPH LIBRARY !
// 	/******************************************************************************/
// /**********************************************************************************/

// 	/*************************
// 	/ In order to speed up the computation a graph structure is used.
// 	/ A graph is created corresponding to the metabolic network as displayed in Cytoscape
// 	/ Algorithms are applied to this graph and then results are displayed in Cytoscape window

// 	/ For the graph objects we develop a set of graph algorithms:
// 	/ - Get one of the minimal Feedback arc sets
// 	/ - Get strongly connected components
// 	/ - Get leaf nodes in a graph
// 	/ - Test if the graph is acyclic or not
// 	/**********************
// 	*/









// //IN PROGRESS !
// //Function to extract FAS with selected compounds as input and outputs
// getMinimalFASstory:function(graph,selectedNodesID)
// 	{
// 		//console.log("Graph is acyclic "+this.isAcyclic(graph));
// 		var S=new Array();
// 		var Sg=new Graph();
// 		var T=new Array();
// 		//Order the edge that can be removed
// 		//Edge connecting higly connected nodes first
// 		var maxValue=graph.edges.length;
// 		for(e in graph.edges)
// 		{
// 			var edge=graph.edges[e];
// 			var weight=0;
// 			if(selectedNodesID.length>0)
// 			{
// 				if(selectedNodesID.indexOf(edge.source.id)==-1)
// 					weight=weight+maxValue;				
// 				if(selectedNodesID.indexOf(edge.target.id)==-1)
// 					weight=weight+maxValue;				
// 			}
// 			weight=weight-Math.max(edge.source.edges.length,weight+edge.target.edges.length);
// //			weight=weight+edge.target.edges.length;
// 			edge.weight=weight;
// 		}

// 		graph.edges.sort(function(obj1, obj2) {
// 			return obj1.weight - obj2.weight;
// 			});

// 		for(e in graph.edges)
// 		{
// 			var edge=graph.edges[e];
// 			Sg.addEdge(edge.source.id,edge.target.id);
// 			if(this.isAcyclic(Sg))
// 				S.push(edge);				
// 			else
// 			{
// 				Sg.removeEdge(edge);
// 				T.push(edge);
// 			}
// 		}
// 		return T;
// 	},
// });