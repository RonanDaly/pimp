/**
 * @author MC
 * @description : Drawing links
 */
metExploreD3.GraphPath = {
	panelParent:"",

	/**********************************************/
	// INIT FUNCTIONS
	/**********************************************/
	delayedInitialisation : function(parent) {
		metExploreD3.GraphLink.panelParent = parent;
	},

	/*******************************************
	* Init the visualization of links
	* @param {} parent : The panel where the action is launched
	* @param {} session : Store which contains global characteristics of session
	* @param {} linkStyle : Store which contains links style
	* @param {} metaboliteStyle : Store which contains metabolites style
	*/
	refreshLink : function(parent, session, linkStyle, metaboliteStyle) {
		metExploreD3.GraphLink.panelParent = "#"+parent; 
		var networkData=session.getD3Data();

		var size=20;
		// The y-axis coordinate of the reference point which is to be aligned exactly at the marker position.
		var refY = linkStyle.getMarkerWidth() / 2;
		// The x-axis coordinate of the reference point which is to be aligned exactly at the marker position.
		// var refX = linkStyle.getMarkerHeight / 2;

	  // Adding arrow on links
		d3.select("#"+parent).select("#D3viz").select("#graphComponent").append("svg:defs").selectAll("marker")
			.data(["in", "out"])
			.enter().append("svg:marker")
			.attr("id", String)
			.attr("viewBox", "0 0 "+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight())
			.attr("refY", refY)
			.attr("markerWidth", linkStyle.getMarkerWidth())
			.attr("markerHeight", linkStyle.getMarkerHeight())
			.attr("orient", "auto")
			.append("svg:path")
			.attr("class", String)
			.attr("d", "M0,0L"+linkStyle.getMarkerWidth()+","+linkStyle.getMarkerHeight()/2+"L0,"+linkStyle.getMarkerWidth()+"Z")
			.style("visibility", "hidden");

			// .attr("d", "M"+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight()/2+" L"+linkStyle.getMarkerWidth()/2+" "+(3*linkStyle.getMarkerHeight()/4)+" A"+linkStyle.getMarkerHeight()+" "+linkStyle.getMarkerHeight()+" 0 0 0 "+linkStyle.getMarkerWidth()/2+" "+(1*linkStyle.getMarkerHeight()/4)+" L"+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight()/2+"Z")
		
	   
		// Append link on panel
		metExploreD3.GraphLink.link=d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("line")
			.data(networkData.getLinks())
			.enter()
			.append("line")
			.attr("class", "link")//it comes from resources/css/networkViz.css
			.attr("marker-end", function (d) {
				if (d.interaction=="out")
				{
				   d3.select("#"+parent).select("#D3viz").select("#graphComponent").select("#" + d.interaction)
					.attr("refX", (metaboliteStyle.getWidth()+metaboliteStyle.getHeight())/2/2  + (linkStyle.getMarkerWidth() ))
					.style("fill", linkStyle.getMarkerOutColor())
						.style("stroke",linkStyle.getMarkerStrokeColor())
						.style("stroke-width",linkStyle.getMarkerStrokeWidth());

				   return "url(#" + d.interaction + ")";
				}
				else
				{
				  return "none";             
				}
				
				})
			 .attr("marker-start", function (d) {
				if (d.interaction=="out")
				{
				   return "none";
				}
				else
				{
				  d3.select("#"+parent).select("#D3viz").select("#graphComponent").select("#" + d.interaction)
					.attr("refX",-((metaboliteStyle.getWidth()+metaboliteStyle.getHeight())/2/2 ))
					.style("fill", linkStyle.getMarkerInColor())
					.style("stroke",linkStyle.getMarkerStrokeColor())
						.style("stroke-width",linkStyle.getMarkerStrokeWidth());

				  return "url(#" + d.interaction + ")";              
				}  
			  })
			 .style("stroke",linkStyle.getStrokeColor());
			 
	},

	/*******************************************
	* Tick function of links
	* @param {} panel : The panel where the action is launched
	* @param {} scale = Ext.getStore('S_Scale').getStoreByGraphName(panel);
	*/
	tick : function(panel, scale) {
	  // If you want to use selection on compartments path
	  // d3.select("#"+metExploreD3.GraphNode.panelParent).select("#D3viz").select("graphComponent").selectAll("path")
	  d3.select("#"+panel).select("#D3viz").selectAll("path")
		  .filter(function(d){return d!="linkCaptionRev"})
		  .attr("d", metExploreD3.GraphPath.groupPath)
		  .attr("transform", d3.select("#"+panel).select("#D3viz").select("#graphComponent").attr("transform")); 
	},

	/*******************************************
	* Init the visualization of links
	* @param {} parent : The panel where the action is launched
	* @param {} session : Store which contains global characteristics of session
	* @param {} linkStyle : Store which contains links style
	* @param {} metaboliteStyle : Store which contains metabolites style
	*/
	loadPath : function(parent) {
		 d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node")
		var metabolites = metExploreD3.GraphPath.node.filter(function(d){return d.getBiologicalType()=='metabolite'});

		session.groups = d3.nest().key(function(d) { return d.getCompartment(); }).entries(metabolites.data());
        
        metExploreD3.GraphPath.groupPath = function(d) {
        	var scale = metExploreD3.getScaleById("viz");
			if(d.values.length>0)
			{				
				if(d.values.length>2)
				{
				
					return "M" + 
				      d3.geom.hull(d.values.map(function(i) { return [i.x, i.y]; }))
				        .join("L")
				    + "Z";
				}
				else
				{			
					var fakeNodes = [];
					d.values.forEach(function(val){
						fakeNodes.push([val.x,val.y]);
					});
					var dx, dy;
					for (var i = d.values.length ; i < 3; i++) {
						dx = d.values[0].x*(1+0.00001*i);
						dy = d.values[0].y*(1+0.000011*i);
						fakeNodes.push([dx, dy]);
					};
					
					return "M" + 
				      d3.geom.hull(fakeNodes)
				        .join("L")
				    + "Z";
				}
			}
		};

		metExploreD3.GraphPath.groupFill = function(d, i) { 
			// Sort compartiments store
			metExploreD3.sortCompartmentInBiosource();
	 		var color;
	 		// Change reactions stroke color by compartment
	 		for(var j=0 ; j<metExploreD3.getCompartmentInBiosourceLength() ; j++){
	 			if(d.key==metExploreD3.getCompartmentInBiosourceSet()[j].getIdentifier() )
	 				color = metExploreD3.getCompartmentInBiosourceSet()[j].getColor();
	 		}
	        return color;
		};

		var pathTab = "M0,0L10,10Z";

		// If you want to use selection on compartments path
		// d3.select("#"+metExploreD3.GraphNode.panelParent).select("#D3viz").select("graphComponent").selectAll("path")
		// 	.enter().insert("path", "g.node")

		d3.select("#"+parent).select("#D3viz").selectAll("path")
		    .filter(function(d){return d!="linkCaptionRev"})
		    .data(session.groups)
		    .attr("d", function(d){ return pathTab; })
		    .enter().insert("path", ":first-child")
				.attr("class", function(d){ return d.key; })
				.attr("id", function(d){ return d.key; })
				.style("fill", metExploreD3.GraphPath.groupFill)
				.style("stroke", metExploreD3.GraphPath.groupFill)
				.style("stroke-width", 40)
				.style("stroke-linejoin", "round")
				.style("opacity", .15);	
	}
}