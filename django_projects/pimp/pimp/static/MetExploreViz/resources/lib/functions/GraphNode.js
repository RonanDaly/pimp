
/**
 * @author MC
 * @description : Nodes drawing
 */

metExploreD3.GraphNode = {
	
	node :"",
	_MyThisGraphNode :"",
	panelParent :"",
	activePanel :"",
	taskClick :"",
	charKey :"",
	ctrlKey :"",
	groups:"",
	groupPath:"",
	groupFill:"",
	dblClickable:false,

	/*******************************************
    * Initialization of variables  
    * @param {} parent : The panel where are the node
    */
    delayedInitialisation : function(parent) {

		metExploreD3.GraphNode.panelParent = parent;
		_MyThisGraphNode = metExploreD3.GraphNode;
		activePanel = metExploreD3.GraphNode;
	},


	/*******************************************
    * Permit to select neighbour of a node
    * @param {} d : a node
    */
	selectNeighbours : function(d, panel) {
		d3.select("#viz").select("#D3viz").select("#graphComponent")
			.selectAll("path.link")
			.filter(function(link){
				return link.getSource()==d || link.getTarget()==d;
			})
			.each(function(link){
				if(link.getSource()==d){
					if(!link.getTarget().isSelected()) 
						_MyThisGraphNode.selection(link.getTarget(), panel);
				}
				else{
					if(!link.getSource().isSelected()) 
						_MyThisGraphNode.selection(link.getSource(), panel);
				}
			});
	},

	/*******************************************
    * Permit to start drag and drop of nodes
    * @param {} d : Color in byte
    */
	dragstart : function(d, i) {
		// Get the panel where brush is used
		_MyThisGraphNode.activePanel = d3.event.sourceEvent.target.viewportElement.parentNode.id;
		if(_MyThisGraphNode.activePanel=="" || _MyThisGraphNode.activePanel.search("node")!=-1)
			_MyThisGraphNode.activePanel = d3.event.sourceEvent.target.parentNode.viewportElement.parentNode.id;
		
		// Stop the propagation of the event to bypass moving graph
		d3.event.sourceEvent.stopPropagation();

		var session = _metExploreViz.getSessionById(_MyThisGraphNode.activePanel);
			
		if(session!=undefined)  
		{	
			// For the right click you can't deselectionate the node
			if(d3.event.sourceEvent.button==2){
				if(!d.isSelected()){
					_MyThisGraphNode.selection(d, _MyThisGraphNode.activePanel);

					// 78 = N like neighbour
					if(_MyThisGraphNode.charKey==78 && d.isSelected())
						_MyThisGraphNode.selectNeighbours(d, _MyThisGraphNode.activePanel);
				}
			}
			else
			{
				_MyThisGraphNode.selection(d, _MyThisGraphNode.activePanel);

				// 78 = N like neighbour
				if(_MyThisGraphNode.charKey==78 && d.isSelected())
					_MyThisGraphNode.selectNeighbours(d, _MyThisGraphNode.activePanel);
			}

			d3.selectAll("#D3viz")
				.style("cursor", "move");
		
			var force = session.getForce();
			force.stop(); // stops the force auto positioning

			// If graphs are linked we move the same nodes
			if(session.isLinked()){

				var sessionsStore = _metExploreViz.getSessionsSet();
				
				for (var key in sessionsStore) {
					if(sessionsStore[key].isLinked() && _MyThisGraphNode.activePanel!=sessionsStore[key].getId())
					{
						var linkedForce = sessionsStore[key].getForce();
						linkedForce.stop();
					}
				}
			}
		}
	},

	/*******************************************
	* Change the style of reaction 
	*/
	refreshStyleOfReaction : function(){
		var reactionStyle = metExploreD3.getReactionStyle();
		
		var reactions = d3.select("#viz").select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.filter(function(node){
				return node.getBiologicalType()=="reaction";
			});

		reactions
			.select("text")
			.remove();

		reactions
			.setNodeForm(
				reactionStyle.getWidth(),
				reactionStyle.getHeight(),
				reactionStyle.getRX(),
				reactionStyle.getRY(),
				reactionStyle.getStrokeColor(),
				reactionStyle.getStrokeWidth()
			);


		reactions.each(function(node){
			metExploreD3.GraphNode.addText(node, "viz");
		});

	},

	/*******************************************
	* Change the style of reaction 
	*/
	refreshStyleOfMetabolite : function(){
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		
		var metabolites = d3.select("#viz").select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.filter(function(node){
				return node.getBiologicalType()=="metabolite";
			});

		metabolites
			.select("text")
			.remove();

		metabolites
			.filter(function(d) {
				return !d.getIsSideCompound();
			})
			.setNodeForm(
				metaboliteStyle.getWidth(),
				metaboliteStyle.getHeight(),
				metaboliteStyle.getRX(),
				metaboliteStyle.getRY(),
				undefined,
				metaboliteStyle.getStrokeWidth()
			);

		metabolites
			.filter(function(d) {
					return d.getIsSideCompound();
				})
			.setNodeForm(
				metaboliteStyle.getWidth()/2,
				metaboliteStyle.getHeight()/2,
				metaboliteStyle.getRX()/2,
				metaboliteStyle.getRY()/2,
				undefined,
				metaboliteStyle.getStrokeWidth()/2
			);
		var minDim = Math.min(metaboliteStyle.getWidth(), metaboliteStyle.getHeight());

		metabolites.each(function(node){
			metExploreD3.GraphNode.addText(node, "viz");
		});
		
		metabolites.select('.structure_metabolite')
			.attr(
				"viewBox",
				function(d) { 
					console.log(minDim);
					return "0 0 " + minDim
							+ " " + minDim;
				}
			)
			.attr("width", minDim *8/10 + "px")
			.attr("height", minDim *8/10+ "px")
			.attr("x", (-minDim/2)+(minDim*1/10))
			.attr("preserveAspectRatio", "xMinYMin")
			.attr("y", (-minDim/2)+(minDim*1/10));

		var session = _metExploreViz.getSessionById("viz");
		
		var force = session.getForce();
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
	* Change the node position
	* @param {} d : The node to move
	* @param {} parent : The panel where the action is launched
	*/
	moveNode : function(d, panel){
		d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.filter(function(node){
				if(_MyThisGraphNode.ctrlKey)
					return node.isSelected();
				else
					return d.getId()==node.getId();
			})
			.each(function(node){
				
					node.px += d3.event.dx;
					node.py += d3.event.dy;
					node.x += d3.event.dx;
					node.y += d3.event.dy;
			});
	},

	/*******************************************
	* Updating both px,py,x,y on d
	* @param {} d : The node to move
	*/
	dragmove : function(d, i) {
			

		if(!d.isSelected()){
			_MyThisGraphNode.selection(d, _MyThisGraphNode.activePanel);
			// 78 = N like neighbour
			if(_MyThisGraphNode.charKey==78)
				_MyThisGraphNode.selectNeighbours(d, _MyThisGraphNode.activePanel);
		}

		// with updating both px,py,x,y on d !
		_MyThisGraphNode.moveNode(d,_MyThisGraphNode.activePanel);
		
		_MyThisGraphNode.tick(_MyThisGraphNode.activePanel); // this is the key to make it work together
		
		var scaleactivePanel = metExploreD3.getScaleById(_MyThisGraphNode.activePanel);
    
		metExploreD3.GraphLink.tick(_MyThisGraphNode.activePanel, scaleactivePanel);
	
		var session = _metExploreViz.getSessionById(_MyThisGraphNode.activePanel);
		
		// If graphs are linked we move the same nodes
		if(session.isLinked()){

			var sessionsStore = _metExploreViz.getSessionsSet();

			for (var key in sessionsStore) {
				if(sessionsStore[key].isLinked()  && _MyThisGraphNode.activePanel!=sessionsStore[key].getId())
				{
					var scalesess = metExploreD3.getScaleById(sessionsStore[key].getId());
    
					_MyThisGraphNode.moveNode(d,sessionsStore[key].getId());
					_MyThisGraphNode.tick(sessionsStore[key].getId()); // this is the key to make it work together
					// with updating both px,py,x,y on d !
					metExploreD3.GraphLink.tick(sessionsStore[key].getId(), scalesess);
				}
			}
		}
	},

	/*******************************************
	* Stop dragging
	* @param {} d : The node to move
	*/
	dragend : function(d, i) {
		var session = _metExploreViz.getSessionById(_MyThisGraphNode.activePanel);
		var mainSession = _metExploreViz.getSessionById("viz");
		
		if(session!=undefined)  
		{
			if(session.isLinked()){

				var sessionsStore = _metExploreViz.getSessionsSet();
				
				for (var key in sessionsStore) {
					if(sessionsStore[key].isLinked() && _MyThisGraphNode.activePanel!=sessionsStore[key].getId())
					{
						var animLinked = metExploreD3.GraphNetwork.isAnimated(mainSession.getId());
						if (animLinked=='true') {
							var mainforce = mainSession.getForce();// of course set the node to fixed so the force doesn't include the node in its auto positioning stuff
			        				
							if ((metExploreD3.GraphNetwork.isAnimated(_MyThisGraphNode.panelParent) == 'true') 
								|| (metExploreD3.GraphNetwork.isAnimated(_MyThisGraphNode.panelParent) == null)) {
								mainforce.resume();
							}
						}
						_MyThisGraphNode.tick(sessionsStore[key].getId()); // this is the key to make it work together
						// with updating both px,py,x,y on d !
						var scalesess = metExploreD3.getScaleById(sessionsStore[key].getId());
   						metExploreD3.GraphLink.tick(sessionsStore[key].getId(), scalesess);
					}
				}
			}
			else
			{
				var anim=metExploreD3.GraphNetwork.isAnimated(_MyThisGraphNode.activePanel);
				if (anim=='true') {
					var force = session.getForce();// of course set the node to fixed so the force doesn't include the node in its auto positioning stuff
	        				
					if ((metExploreD3.GraphNetwork.isAnimated(_MyThisGraphNode.activePanel) == 'true') 
						|| (metExploreD3.GraphNetwork.isAnimated(_MyThisGraphNode.activePanel) == null)) {
							force.resume();
					}
				}

				_MyThisGraphNode.tick(_MyThisGraphNode.activePanel);
				var scaleactivePanel = metExploreD3.getScaleById(_MyThisGraphNode.activePanel);
    
				metExploreD3.GraphLink.tick(_MyThisGraphNode.activePanel, scaleactivePanel);
				
			}

			d3.selectAll("#D3viz").style("cursor", "default");
		}
	},

	/*******************************************
	* To Select a node
	* @param {} d : The node to move
	* @param {} parent : The panel where the action is launched
	*/
	fixNodeOnRefresh : function(d, panel) {
		var session = _metExploreViz.getSessionById(panel);
		if(session!=undefined)  
		{
			// Change the node visualization
			if(d.isSelected()) 
			{ 
				_MyThisGraphNode.selectNode(d, panel);
			}
			else 
			{ 
				_MyThisGraphNode.unSelectNode(d, panel);
			}

			// Time out to avoid lag
			setTimeout(
			function() {
				if(session.isLinked()){

					var sessionsStore = _metExploreViz.getSessionsSet();

					for (var key in sessionsStore) {
						if(sessionsStore[key].isLinked() && panel!=sessionsStore[key].getId())
						{
							d3.select("#"+sessionsStore[key].getId()).select("#D3viz").select("#graphComponent")
								.selectAll("g.node")
								.filter(function(node){return d.getId()==node.getId();})
								// .attr("selected", function(node){return node.selected=!node.selected;})
								.each(function(node){node.setIsSelected(!node.isSelected())});

							if(d.isSelected()) 
							{ 
								_MyThisGraphNode.selectNode(d, sessionsStore[key].getId());	
							}
							else
							{
								_MyThisGraphNode.unSelectNode(d, sessionsStore[key].getId());
							}				
						}
					}
				}
			}
		, 200);
		}
	},

	/*******************************************
	* To Select a node
	* @param {} d : The node to move
	* @param {} parent : The panel where the action is launched
	*/
	selection : function(d, panel) {
		var session = _metExploreViz.getSessionById(panel);
		if(session!=undefined)  
		{
			// Chage the node statute
			d3.select("#"+panel).select("#D3viz").select("#graphComponent")
				.selectAll("g.node")
				.filter(function(node){return d.getId()==node.getId();})
				.each(function(node){node.setIsSelected(!node.isSelected())});
			
			// Change the node visualization
			if(d.isSelected()) 
			{ 
				_MyThisGraphNode.selectNode(d, panel);
			}
			else 
			{ 
				_MyThisGraphNode.unSelectNode(d, panel);
			}

			// Time out to avoid lag
			setTimeout(
			function() {
				if(session.isLinked()){

					var sessionsStore = _metExploreViz.getSessionsSet();

					for (var key in sessionsStore) {
						if(sessionsStore[key].isLinked() && panel!=sessionsStore[key].getId())
						{
							d3.select("#"+sessionsStore[key].getId()).select("#D3viz").select("#graphComponent")
								.selectAll("g.node")
								.filter(function(node){return d.getId()==node.getId();})
								// .attr("selected", function(node){return node.selected=!node.selected;})
								.each(function(node){node.setIsSelected(!node.isSelected())});

							if(d.isSelected()) 
							{ 
								_MyThisGraphNode.selectNode(d, sessionsStore[key].getId());	
							}
							else
							{
								_MyThisGraphNode.unSelectNode(d, sessionsStore[key].getId());
							}				
						}
					}
				}
			}
		, 200);
		}
	},

	/*******************************************
	* To Select a node in visualization
	* @param {} d : The node to move
	* @param {} parent : The panel where the action is launched
	*/
	selectNode : function(d, panel){
		var reactionStyle = metExploreD3.getReactionStyle();
		var session = _metExploreViz.getSessionById(panel);
			
		var metabolite_Store = metExploreD3.getMetabolitesSet();
		var reaction_Store = metExploreD3.getReactionsSet();


		var content = 
			"<b>Name:</b> " + d.getName() 
			+"<br/><b>Biological type:</b> " + d.getBiologicalType() +
			((d.getCompartment()!=undefined) ? "<br/><b>Compartment:</b> " + d.getCompartment() : "" )+
			((d.getDbIdentifier()!=undefined) ? "<br/><b>Database identifier:</b> " + d.getDbIdentifier() : "" )+
			((d.getEC()!=undefined) ? "<br/><b>EC number:</b> " + d.getEC() : "" )+
			((d.getReactionReversibility()!=undefined) ? "<br/><b>Reaction reversibility:</b> " + d.getReactionReversibility() : "" )+
			((d.getIsSideCompound()!=undefined) ? "<br/><b>SideCompound:</b> " + d.getIsSideCompound() : "" )+
			((d.getMappingDatasLength()!=0) ? ((d.getMappingDatasLength()==1) ? "<br/><b>Mapping:</b><br/><table style='width:100%; margin-left: 30px; padding-right: 30px;'>" : "<br/><b>Mappings:</b><br/><table style='width:100%; margin-left: 30px; padding-right: 30px;'>"): "");

		d.getMappingDatas().forEach(function(map){
			content+="<tr><td>" + map.getMappingName() +"</td><td>"+ map.getConditionName() +"</td><td>"+ map.getMapValue() +"</td></tr>";
		});

		content+="</table>";
		
		if(d.getSvg()!="" && d.getSvg()!=undefined && d.getSvg()!="undefined"){
			content+='<br/><img src="resources/images/structure_metabolite/'+d.getSvg()+'"/>';
		}

   		document.getElementById("tooltip2").innerHTML = content;
   		document.getElementById("tooltip2").classList.remove("hide");
		// Fix the tooltip of node
		document.getElementById("tooltip2").classList.add("fixed");

		// Fix the node
		// Add  node in the list of selected nodes
	  	d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.filter(function(node){return d.getId()==node.getId();})
			.each(function(node){ 
				node.fixed = true; 
				session.addSelectedNode(node.getId()); 
				if(node.getBiologicalType()=="reaction")
					d3.select(this).select('text').style("fill","white");
			});	
		
		// We define the text for a metabolie WITHOUT the coresponding SVG image 
		var node = d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.filter(function(node){return d.getId()==node.getId();})
			.select('.fontSelected').style("fill-opacity", '0.4');

		_MyThisGraphNode.addText(d, panel);
	},

	/*******************************************
	* To Unselect a node in visualization
	* @param {} d : The node to move
	* @param {} parent : The panel where the action is launched
	*/
	unSelectNode : function(d, panel){
		var session = _metExploreViz.getSessionById(panel);
	
		var metabolite_Store = metExploreD3.getMetabolitesSet();
		var reaction_Store = metExploreD3.getReactionsSet();

		d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.filter(function(node){return d.getId()==node.getId();})
			.select('.fontSelected').style("fill-opacity", '0');
		
		d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.filter(function(node){return d.getId()==node.getId();})
			.each(function(node){ 
				session.removeSelectedNode(node.getId()); 
				node.fixed = false;
				if(node.getBiologicalType()=="reaction"){
					var rgb;
					var color = metExploreD3.GraphUtils.chooseTextColor(this.style.getPropertyValue("fill"));
					d3.select(this).select('text').style("fill", color);
				}
			});
	},

	/*******************************************
	* To add text on node in visualization
	* @param {} d : The node to move
	* @param {} parent : The panel where the action is launched
	*/
	addText : function(d, panel){
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var reactionStyle = metExploreD3.getReactionStyle();
		var sessionMain = _metExploreViz.getSessionById('viz');

		if(d.getBiologicalType() =='metabolite'){
			var minDim = Math.min(metaboliteStyle.getWidth(),metaboliteStyle.getHeight());
  		 	
	 		// if there is no text we define it for a metabolie WITHOUT the coresponding SVG image 
			if(d3.select("#"+panel).select("#D3viz").select("#graphComponent")
				.selectAll("g.node")
				.filter(function(node){return d.getId()==node.getId();}).select("text")=="")
            {
            	d3.select("#"+panel).select("#D3viz").select("#graphComponent")
					.selectAll("g.node")
					.filter(function(node){return d.getId()==node.getId();})
		            .append("svg:text")
	            	.attr("fill", "black")
		            .attr("class", function(d) {
							return d.getBiologicalType();
						})
					.each(function(d) { 
						var el = d3.select(this);
					    var name = metaboliteStyle.getDisplayLabel(d, metaboliteStyle.getLabel());
						name = name.split(' ');
						el.text('');
						for (var i = 0; i < name.length; i++) {
					        var nameDOMFormat = $("<div/>").html(name[i]).text();
			        var tspan = el.append('tspan').text(nameDOMFormat);
					        if (i > 0)
					            tspan.attr('x', 0).attr('dy', '5');
					    }
					})
					.style("font-size",metaboliteStyle.getFontSize())
					.style("paint-order","stroke")
					.style("stroke-width",  1)
					.style("stroke", "white")
					.style("stroke-opacity", "0.7")
					// 	function(d) {
					// 		return Math.min(
					// 			(minDim) / 2,
					// 			((minDim - 3)/ this.getComputedTextLength() * 10) / 2
					// 		)+ "px";
					// })
					.attr("dy", ".4em")
					//.attr("y",+(3 / 4 * (minDim/2) ));
					.style("font-weight", 'bold')
					.style("pointer-events", 'none')
					.attr("y",minDim/2+3);


			}

  		 	if( d.getSvg()!="undefined" && d.getSvg()!=undefined && d.getSvg()!=""){ 
	            if(d3.select("#"+panel).select("#D3viz").select("#graphComponent")
						.selectAll("g.node")
						.filter(function(node){return d.getId()==node.getId();}).select("image").empty())
	            {
					// Image definition
		             d3.select("#"+panel).select("#D3viz").select("#graphComponent")
						.selectAll("g.node")
						.filter(function(node){return d.getId()==node.getId();})
						.append("svg")
						.attr("viewBox",function(d) {return "0 0 "+minDim+" "+minDim;})
						.attr("width", minDim *8/10 + "px")
						.attr("height", minDim *8/10+ "px")
						.attr("x", (-minDim/2)+(minDim*1/10))
						.attr("preserveAspectRatio", "xMinYMin")
						.attr("y", (-minDim/2)+(minDim*1/10))
						.attr("class", "structure_metabolite")
						.append("image")
						.attr("xlink:href",
							function(d) {
								return "resources/images/structure_metabolite/"
										+ d.getSvg();
							}
						)
						.attr("width", "100%").attr("height", "100%");
				}
			}
	        
	    }
	    
	    // Same thing for a reaction
	    if(d.getLabelVisible() ==true && d.getBiologicalType() =='reaction'){
  		 		
			if(d3.select("#"+panel).select("#D3viz").select("#graphComponent")
					.selectAll("g.node")
					.filter(function(node){return d.getId()==node.getId();}).text()=="")
	        {
	        	d3.select("#"+panel).select("#D3viz").select("#graphComponent")
					.selectAll("g.node")
					.filter(function(node){return d.getId()==node.getId();})
		            .append("svg:text")
		            .attr("fill", "black")
					.attr("class", function(d) {
						return d.getBiologicalType();
					})
					// .text(function(d) { return d.getName(); })
					.text(function(d) {
						var text=$("<div/>").html(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())).text();
						if(text=="")
							var text=$("<div/>").html(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())).text();
							// var text=$("<div/>").html(d.get(sessionMain.getDisplayNodeName())).text();

						//text=text.replace(" ","<br>");
						//console.log(text);
						return text;
					})
					.style(
						"font-size",//reactionStyle.getFontSize())
						 function(d) {

						 	if(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())=='NA')
						 		return 6;
						 	return Math.min(reactionStyle.getWidth(),(reactionStyle.getWidth() - reactionStyle.getWidth()/10)/ this.getComputedTextLength()* 10)+ "px";
					})
					.style("font-weight", 'bold')
					.attr("dy", ".3em");
			}
		} 
	},

	/*******************************************
	* To add text on node in visualization
	* @param {} parent : The panel where the action is launched
	*/
	addTextAllPanels : function(){
 		var sessions = _metExploreViz.getSessionsSet();
				
		for (var key in sessions) {	
			d3.select("#"+sessions[key].getId()).select("#D3viz").select("#graphComponent")
				.selectAll("g.node")
				.each(function(node){
					metExploreD3.GraphNode.addText(node, sessions[key].getId());
				});
		}	
	},

	/*******************************************
	* To remove text on node in visualization
	* @param {} parent : The panel where the action is launched
	*/
	removeText : function(panel){
 		// if there is no text we define it for a metabolie WITHOUT the coresponding SVG image 
		d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.select("text")
			.remove();
	},

	/*******************************************
	* To remove text on node in visualization
	* @param {} parent : The panel where the action is launched
	*/
	removeTextAllPanels : function(panel){
 		var sessions = _metExploreViz.getSessionsSet();
				
		for (var key in sessions) {						
			metExploreD3.GraphNode.removeText(sessions[key].getId());
		}
	},

	/*******************************************
	* To Search nodes in visualization
	* @param {} selectedVal : The value of search field text
	*/
	searchNode : function(selectedVal) {
	    //find the node
		var upperCaseSelectedVal = selectedVal.toUpperCase();
	   			
	    var svg = d3.select('#viz').select('#D3viz').select('#graphComponent');
	    
        var selected = svg.selectAll("g.node").filter(function (d, i) {  

        	var equalName = false;
        	if(d.getName()!=undefined) 
        		equalName = d.getName().toUpperCase().indexOf(upperCaseSelectedVal) > -1;

        	var equalEc = false;
        	if(d.getEC()!=undefined) 
        		equalEc = d.getEC().toUpperCase().indexOf(upperCaseSelectedVal) > -1;

        	var equalDbId = false;
        	if(d.getDbIdentifier()!=undefined) 
        		equalDbId = d.getDbIdentifier().toUpperCase().indexOf(upperCaseSelectedVal) > -1;

        	var equalCompartment = false;
        	if(d.getCompartment()!=undefined) 
        		equalCompartment = d.getCompartment().toUpperCase().indexOf(upperCaseSelectedVal) > -1;

        	var equalBiologicalType = false;
        	if(d.getBiologicalType()!=undefined) 
        		equalBiologicalType = d.getBiologicalType().toUpperCase().indexOf(upperCaseSelectedVal) > -1;

            return equalName || equalEc || equalDbId || equalCompartment || equalBiologicalType;
        });

		if(selected.size()==0)
			metExploreD3.displayMessage("Warning", 'The node "' + selectedVal + '" doesn\'t exist.')
        else
        	selected.each(
             	function(aSelectedNode){
        			if(!aSelectedNode.isSelected())
        				_MyThisGraphNode.selection(aSelectedNode, 'viz');
        		});
	},

	/*******************************************
	* To add nodes in visualization
	* @param {} panel : The panel where the action is launched
	*/
	refreshNode : function(parent) {
		d3.select("body")
		    .on("keydown", function() {
		    	_MyThisGraphNode.charKey = d3.event.keyCode;
              	_MyThisGraphNode.ctrlKey = d3.event.ctrlKey;
		    })
		    .on("keyup", function(e) {
		    	_MyThisGraphNode.charKey = 'none';
              	_MyThisGraphNode.ctrlKey = d3.event.ctrlKey;
		    });

		metExploreD3.GraphNode.panelParent = parent;

		_MyThisGraphNode = metExploreD3.GraphNode;

		/***************************/
		// Var which permit to drag
		/***************************/
		var node_drag = d3.behavior.drag()
			.on("dragstart",_MyThisGraphNode.dragstart)
			.on("drag", _MyThisGraphNode.dragmove)
			.on("dragend", _MyThisGraphNode.dragend);


		// Load user's preferences
		var reactionStyle = metExploreD3.getReactionStyle();
		
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var generalStyle = metExploreD3.getGeneralStyle();

		var session = _metExploreViz.getSessionById(parent);
		var sessionMain = _metExploreViz.getSessionById('viz');

		var networkData=session.getD3Data();
	    var h = parseInt(d3.select("#"+_MyThisGraphNode.panelParent).select("#D3viz")
			.style("height"));
	    var w = parseInt(d3.select("#"+_MyThisGraphNode.panelParent).select("#D3viz")
			.style("width"));

	    // Create function to manage double click
	    d3.selectAll("#D3viz")
			.on("mouseup", this.unselectIfDBClick);
		        
	 
	 	var scale = metExploreD3.getScaleById(parent);


		// For each node we append a division of the class "node"
		metExploreD3.GraphNode.node = d3.select("#"+metExploreD3.GraphNode.panelParent).select("#D3viz").select("#graphComponent").selectAll("g.node")
			.data(networkData.getNodes()).enter()
				.append("svg:g").attr("class", "node")
				.attr("id", function(node){ return "node"+node.getId(); })
				.call(node_drag)
				.style("fill", "white");
				// Here it's the position by default for the beginning of force algorithm
				// .on("click", selection)
				// .style(
				// 	"stroke-dasharray", function(d) {
				// 		if (d.getReactionReversibility()) {
				// 			return "2,2";
				// 		} else {
				// 			return "";
				// 		}
				// 	}
				// );

		metExploreD3.GraphNode.node
			.filter(function(d){ return !d.isDuplicated(); })
			.on("mouseenter", function(d) { 
					
				var transform = d3.select(this).attr("transform");
				var scale=transform.substring(transform.indexOf("scale"),transform.length);
				var scaleVal=scale.substring(6, scale.indexOf(')'));		

				if(isNaN(scaleVal))
					scaleVal=1;

				var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
				d3.select(this).attr("transform", "translate("+d.x+", "+d.y+") scale("+scaleVal*2+")");
				
				var links = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("path.link");

				if(d.getBiologicalType()=="reaction"){
						
					links.filter(function(link){return d.getId()==link.getSource().getId();})
						.style("stroke", "green")
						// .each(function(link){
						// 	var last = links[0][links.size()-1];
						// 	this.parentNode.insertBefore(this, last);
						// }); 	
					 
					 links.filter(function(link){return d.getId()==link.getTarget().getId();})
						.style("stroke", "red")
						// .each(function(link){
						// 	var last = links[0][links.size()-1];
						// 	this.parentNode.insertBefore(this, last);
						// });  	
				}
				else
				{
					links.filter(function(link){return d.getId()==link.getSource().getId();})
						.style("stroke", "red")
						// .each(function(link){
						// 	var last = links[0][links.size()-1];
						// 	this.parentNode.insertBefore(this, last);
						// }); 	
					 
					links.filter(function(link){return d.getId()==link.getTarget().getId();})
						.style("stroke", "green")
						// .each(function(link){
						// 	var last = links[0][links.size()-1];
						// 	this.parentNode.insertBefore(this, last);
						// }); 
				} 
			})
			.on("mouseover", function(d) { 
	        	var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
			
	        	d3.select(this)
				.each(function(node){
					var last = nodes[0][nodes.size()-1];
					this.parentNode.insertBefore(this, last);
				});
					
				d.fixed = true;
				// console.log(d);
				
				 
				var xScale=scale.getXScale();
				var yScale=scale.getYScale();
				
				if(!document.getElementById("tooltip2").classList.contains("fixed"))
				{
					var content = 
						"<b>Name:</b> " + d.getName() 
						+"<br/><b>Biological type:</b> " + d.getBiologicalType() +
						((d.getCompartment()!=undefined) ? "<br/><b>Compartment:</b> " + d.getCompartment(): "" )+
						((d.getDbIdentifier()!=undefined) ? "<br/><b>Database identifier:</b> " + d.getDbIdentifier() : "" )+
						((d.getEC()!=undefined) ? "<br/><b>EC number: </b>" + d.getEC() : "" )+
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

				// d3.select("#"+parent).select("#D3viz").select('#tooltip')
		    })
	        .on("mouseleave", function(d) { 

	        	var transform = d3.select(this).attr("transform");
				var scale=transform.substring(transform.indexOf("scale"),transform.length);
				var scaleVal=scale.substring(6, scale.indexOf(')'));
				if(isNaN(scaleVal))
						scaleVal=1;
							
				var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
				d3.select(this).attr("transform", "translate("+d.x+", "+d.y+") scale("+scaleVal/2+")");

				if(!d.isSelected())
					d.fixed = false;
				var linkStyle = metExploreD3.getLinkStyle();  

		   		document.getElementById("tooltip2").classList.add("hide");
		    	// d3.select("#"+parent).select("#D3viz").select('#tooltip')
		    	// 	.classed("hide", true); 
	    		d3.select("#"+parent).select("#D3viz").select("#graphComponent")
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
					
					d3.select(this).selectAll("rect").selectAll(".metabolite, .fontSelected").transition()
						 .duration(750)
	                     .attr("width", metaboliteStyle.getWidth())
	                     .attr("height", metaboliteStyle.getHeight())
						 .attr("transform", "translate(-" + metaboliteStyle.getWidth() / 2 + ",-"
												+ metaboliteStyle.getHeight() / 2
												+ ")");
				}
	        });

		metExploreD3.GraphNode.node
			.filter(function(d){ return d.isDuplicated(); })
			.on("mouseenter", function(d) {
					
				var transform = d3.select(this).attr("transform");
				var scale=transform.substring(transform.indexOf("scale"),transform.length);
				var scaleVal=scale.substring(6, scale.indexOf(')'));		
				
				if(isNaN(scaleVal))
					scaleVal=1;
			
				var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
				d3.select(this).attr("transform", "translate("+d.x+", "+d.y+") scale("+scaleVal*2+")");
			})
			.on("mouseover", function(d) { 
		        var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
			
	        	d3.select(this)
				.each(function(node){
					var last = nodes[0][nodes.size()-1];
					this.parentNode.insertBefore(this, last);
				});
					
				d.fixed = true;
				
				if(d.getBiologicalType()=="reaction"){
					d3.select("#"+parent).select("#D3viz").select("#graphComponent")
						.selectAll("path.link")
						.filter(function(link){return d.getId()==link.getSource().getId();})
						.style("stroke", "green"); 	
					 
					d3.select("#"+parent).select("#D3viz").select("#graphComponent")
						.selectAll("path.link")
						.filter(function(link){return d.getId()==link.getTarget().getId();})
						.style("stroke", "red"); 	
				}
				else
				{
					d3.select("#"+parent).select("#D3viz").select("#graphComponent")
						.selectAll("path.link")
						.filter(function(link){return d.getId()==link.getSource().getId();})
						.style("stroke", "red"); 	
					 
					d3.select("#"+parent).select("#D3viz").select("#graphComponent")
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
		    // .on("mouseout", function(d) {   
		    // 	d3.select("#"+parent).select("#D3viz").select('#tooltip')
		    // 		.classed("hide", true); 
	     //    })
	        .on("mouseleave", function(d) {  
		        
	        	var transform = d3.select(this).attr("transform");
				var scale=transform.substring(transform.indexOf("scale"),transform.length);
				var scaleVal=scale.substring(6, scale.indexOf(')'));		
				if(isNaN(scaleVal))
						scaleVal=1;
					
				var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
				d3.select(this).attr("transform", "translate("+d.x+", "+d.y+") scale("+scaleVal/2+")");

				if(!d.isSelected())
					d.fixed = false;
				var linkStyle = metExploreD3.getLinkStyle();  

		   		document.getElementById("tooltip2").classList.add("hide");
		    	// d3.select("#"+parent).select("#D3viz").select('#tooltip')
		    	// 	.classed("hide", true); 
	    		d3.select("#"+parent).select("#D3viz").select("#graphComponent")
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

		// d3.selection.prototype.test = function() {
		//     this.append("rect")
		// 	.attr("class", function(d) { return d.getBiologicalType(); })
		// 	.attr("id", function(d) { return d.getId(); })
		// 	.attr("identifier", function(d) { return d.getId(); })
		// 	.attr("width", metaboliteStyle.getWidth())
		// 	.attr("height", metaboliteStyle.getHeight())
		// 	.attr("rx", metaboliteStyle.getRX())
		// 	.attr("ry", metaboliteStyle.getRY())
		// 	.attr("transform", "translate(-" + metaboliteStyle.getWidth() / 2 + ",-"
		// 							+ metaboliteStyle.getHeight() / 2
		// 							+ ")")
		// 	.style("stroke", metaboliteStyle.getStrokeColor())
		// 	.style("stroke-width", metaboliteStyle.getStrokeWidth());
		// };

		// For each metabolite we append a division of the class "rect" with the metabolite style by default or create by the user
		metExploreD3.GraphNode.node.filter(function(d) { return d.getBiologicalType() == 'metabolite' })
			.filter(function(d){ return !d.isDuplicated(); })
			.addNodeForm(
				metaboliteStyle.getWidth(),
				metaboliteStyle.getHeight(),
				metaboliteStyle.getRX(),
				metaboliteStyle.getRY(),
				metaboliteStyle.getStrokeColor(),
				metaboliteStyle.getStrokeWidth()
			);

		// Duplicated metabolites
		metExploreD3.GraphNode.node.filter(function(d) { return d.getBiologicalType() == 'metabolite' })
			.filter(function(d){ 
				return d.isDuplicated(); })
			.style("stroke-opacity",0.5)
			.addNodeForm(
				metaboliteStyle.getWidth()/2,
				metaboliteStyle.getHeight()/2,
				metaboliteStyle.getRX()/2,
				metaboliteStyle.getRY()/2,
				metaboliteStyle.getStrokeColor(),
				metaboliteStyle.getStrokeWidth()/2
			);
			

		// For each reaction we append a division of the class "rect" with the reaction style by default or create by the user
		// For each reaction we append a division of the class "rect" with the reaction style by default or create by the user
		metExploreD3.GraphNode.node
			.filter(function(d) { return d.getBiologicalType() == 'reaction' })
			.addNodeForm(
				reactionStyle.getWidth(),
				reactionStyle.getHeight(),
				reactionStyle.getRX(),
				reactionStyle.getRY(),
				reactionStyle.getStrokeColor(),
				reactionStyle.getStrokeWidth()
			);

		// Sort compartiments store
		metExploreD3.sortCompartmentInBiosource();
 		
 		
 		metExploreD3.GraphNode.colorStoreByCompartment(metExploreD3.GraphNode.node);
 			
		
		if (networkData.getNodes().length < generalStyle.getReactionThreshold() || !generalStyle.isDisplayedLabelsForOpt()) {
			var minDim = Math.min(metaboliteStyle.getWidth(),metaboliteStyle.getHeight());
			// We define the text for a metabolie WITHOUT the coresponding SVG image 
			metExploreD3.GraphNode.node
				.filter(function(d) { return d.getLabelVisible() == true; })
				.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
				.filter(function(d) { return d.getSvg() == "undefined" || d.getSvg()==undefined || d.getSvg()==""; })
				.append("svg:text")
		        .attr("fill", "black")
		        .attr("class", function(d) { return d.getBiologicalType(); })
				// .text(function(d) { return $("<div/>").html(d.get(sessionMain.getDisplayNodeName())).text(); })
				.each(function(d) { 
					var el = d3.select(this);
				    var name = metaboliteStyle.getDisplayLabel(d, metaboliteStyle.getLabel());
					name = name.split(' ');
					el.text('');
					for (var i = 0; i < name.length; i++) {
						var nameDOMFormat = $("<div/>").html(name[i]).text();
				        var tspan = el.append('tspan').text(nameDOMFormat);
				        if (i > 0)
				            tspan.attr('x', 0).attr('dy', '5');
				    }
				})
				.style("font-size",metaboliteStyle.getFontSize())
				.style("paint-order","stroke")
				.style("stroke-width", 1)
				.style("stroke", "white")
				.style("stroke-opacity", "0.7")
				// 	function(d) {
				// 		return Math.min(
				// 			(minDim) / 2,
				// 			((minDim - 3)/ this.getComputedTextLength() * 10) / 2
				// 		)+ "px";
				// })
				.attr("dy", ".4em")
				.style("font-weight", 'bold')
				.style("pointer-events", 'none')
				.attr("y",minDim/2+3);

			// We define the text for a metabolie WITH the coresponding SVG image 
			// Text definition
			metExploreD3.GraphNode.node
				.filter(function(d) { return d.getLabelVisible() == true; })
				.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
				.filter(function(d) { return d.getSvg() != "undefined" && d.getSvg()!=undefined && d.getSvg()!=""; })
				.append("svg:text")
		        .attr("fill", "black")
				.attr("class", function(d) { return d.getBiologicalType(); })
				.each(function(d) { 
					var el = d3.select(this);
				    var name = metaboliteStyle.getDisplayLabel(d, metaboliteStyle.getLabel());
					name = name.split(' ');
					el.text('');
					for (var i = 0; i < name.length; i++) {
				        var nameDOMFormat = $("<div/>").html(name[i]).text();
				        var tspan = el.append('tspan').text(nameDOMFormat);
				        if (i > 0)
				            tspan.attr('x', 0).attr('dy', '7');
				    }
				})
				.style("font-size",metaboliteStyle.getFontSize())
				.style("paint-order","stroke")
				.style("stroke-width",1)
				.style("stroke", "white")
				.style("stroke-opacity", "0.7")
				// 	function(d) {
				// 		return Math.min(
				// 			(minDim) / 2,
				// 			((minDim - 3)/ this.getComputedTextLength() * 10) / 2
				// 		)+ "px";
				// })
				.attr("dy", ".4em")
				//.attr("y",+(3 / 4 * (minDim/2) ));
				.style("font-weight", 'bold')
				.style("pointer-events", 'none')
				.attr("y",minDim/2+3);

			// Image definition
			metExploreD3.GraphNode.node
				.filter(
					function(d) {
						return (d.getBiologicalType() == 'metabolite' && d.getSvg() != "undefined" && d.getSvg()!=undefined && d.getSvg()!="");
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
				.attr(
					"xlink:href",
					function(d) {
						//return "resources/images/structure_metabolite/"
						return "resources/images/structure_metabolite/"
								+ d.getSvg();
					})
				.attr("width", "100%")
				.attr("height", "100%");
			
			// We define the text for a reaction
			metExploreD3.GraphNode.node
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
					.text(function(d) {
						var text=$("<div/>").html(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())).text();
						if(text=="")
							var text=$("<div/>").html(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())).text();
							// var text=$("<div/>").html(d.get(sessionMain.getDisplayNodeName())).text();

						//text=text.replace(" ","<br>");
						//console.log(text);
						return text;
					})
					.style(
						"font-size",//reactionStyle.getFontSize())
						 function(d) {
						 	if(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())=='NA')
						 		return 6;
						 	return Math.min(reactionStyle.getWidth(),(reactionStyle.getWidth() - reactionStyle.getWidth()/10)/ this.getComputedTextLength()* 10)+ "px";
					})
					.style("font-weight", 'bold')
					.attr("dy", ".3em");
			
		}

		metExploreD3.GraphNode.node
				.filter(function(d) { return d.isSelected(); })
				.each( function(aSelectedNode){
					_MyThisGraphNode.fixNodeOnRefresh(aSelectedNode, 'viz');
        		});


		metExploreD3.GraphNode.node
	        .filter(function(node){
	        	return node.getMappingDatasLength()>0 && session.getActiveMapping()!=""; 
	        })
	        .filter(function(node){
	        	var mappingData = node.getMappingDataByNameAndCond(session.getActiveMapping(), session.isMapped());
	        	return mappingData!=null; 
	        })
			.attr("mapped",function(node){
				var mappingData = node.getMappingDataByNameAndCond(session.getActiveMapping(), session.isMapped());
	        	
				if(session.getMappingDataType()=="Continuous"){
					if(session.getColorMappingsSet()[0]<session.getColorMappingsSet()[1]){
						maxValue = session.getColorMappingsSet()[1];
						minValue = session.getColorMappingsSet()[0];
					}
					else
					{
						maxValue = session.getColorMappingsSet()[0];
						minValue = session.getColorMappingsSet()[1];
					}
					
					var generalStyle = _metExploreViz.getGeneralStyle();
					var colorMin=generalStyle.getColorMinMappingContinuous();
					var colorMax=generalStyle.getColorMaxMappingContinuous();

					var colorScale = d3.scale.linear()
					    .domain([parseFloat(minValue), parseFloat(maxValue)])
					    .range([colorMin, colorMax]);
					
					return colorScale(parseFloat(mappingData.getMapValue()));
				}
				var color = session.getColorMappingById(mappingData.getMapValue()).getValue();
				return color;
			})
			.style("fill",function(node){
				var mappingData = node.getMappingDataByNameAndCond(session.getActiveMapping(), session.isMapped());
	        	d3.select(this)
					.insert("rect", ":first-child")
					.attr("class", "stroke")
					.attr("width", parseInt(d3.select(this).select("."+node.getBiologicalType()).attr("width"))+10)
					.attr("height", parseInt(d3.select(this).select("."+node.getBiologicalType()).attr("height"))+10)
					.attr("rx", parseInt(d3.select(this).select("."+node.getBiologicalType()).attr("rx"))+5)
					.attr("ry",parseInt(d3.select(this).select("."+node.getBiologicalType()).attr("ry"))+5)
					.attr("transform", "translate(-" + parseInt(parseInt(d3.select(this).select("."+node.getBiologicalType()).attr("width"))+10) / 2 + ",-"
											+ parseInt(parseInt(d3.select(this).select("."+node.getBiologicalType()).attr("height"))+10) / 2
											+ ")")
					.style("opacity", '0.5')
					.style("fill", 'red');
				if(session.getMappingDataType()=="Continuous"){
					if(parseFloat(session.getColorMappingsSet()[0].getName())<parseFloat(session.getColorMappingsSet()[1].getName())){
						maxValue = parseFloat(session.getColorMappingsSet()[1].getName());
						minValue = parseFloat(session.getColorMappingsSet()[0].getName());
					}
					else
					{
						maxValue = parseFloat(session.getColorMappingsSet()[0].getName());
						minValue = parseFloat(session.getColorMappingsSet()[1].getName());
					}
					
					var generalStyle = _metExploreViz.getGeneralStyle();
					var colorMin=generalStyle.getColorMinMappingContinuous();
					var colorMax=generalStyle.getColorMaxMappingContinuous();

					var colorScale = d3.scale.linear()
						    .domain([parseFloat(minValue), parseFloat(maxValue)])
						    .range([colorMin, colorMax]);
						   
					return colorScale(parseFloat(mappingData.getMapValue()));

				}
				var color = session.getColorMappingById(mappingData.getMapValue()).getValue();
				return color;
			});


		// Sort compartiments store
		/*	
		metExploreD3.sortCompartmentInBiosource();
 		
 		// Change reactions stroke color by compartment
 		for(var i=0 ; i<metExploreD3.getCompartmentInBiosourceLength() ; i++){
 		
 			metExploreD3.GraphNode.node
 			.filter(function(d) {
 				return (d.getBiologicalType() =='metabolite' && d.getCompartment()==metExploreD3.getCompartmentInBiosourceSet()[i].getIdentifier() );
 			})
            .selectAll("rect")
            .style("stroke",metExploreD3.getCompartmentInBiosource()[i].getColor()); 
        }*/


		// metExploreD3.GraphNode.groupFill = function(d, i) { 
		// 	// Sort compartiments store
		// 	console.log(d.key);
		// 	console.log(i);
		// 	console.log(metExploreD3.getCompartmentInBiosourceSet()[i]);
		// 	metExploreD3.sortCompartmentInBiosource();
	 // 		var color;
	 // 		// Change reactions stroke color by compartment
	 // 		for(var j=0 ; j<metExploreD3.getCompartmentInBiosourceLength() ; j++){
	 // 			if(d.key==metExploreD3.getCompartmentInBiosourceSet()[j].getIdentifier() )
	 // 				color = metExploreD3.getCompartmentInBiosource()[j].getColor();
	 //        return color;
		// };
		// 62771 ms for recon before refactoring
		// 41465 ms now
		// var endall = new Date().getTime();
		// var timeall = endall - startall;
		// console.log("----Viz: FINISH refresh/ all "+timeall);
	},

	/*******************************************
	* Fonction call for each update
	* @param {} panel : The panel where the action is launched
	*/
	tick :function(panel) {
		d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("g.node")
			.attr("cx", function(d) {
				return d.x;
			})
			.attr("cy", function(d) {
				return d.y;
			})
			.attr("transform", function(d) {
				//  scale("+ +")
				var scale = 1;
				if(d3.select(this)!=null){
					var transformString = d3.select(this).attr("transform");
					if(d3.select(this).attr("transform")!=null){
						var indexOfScale = transformString.indexOf("scale(");
						if(indexOfScale!=-1)
							scale = parseInt(transformString.substring(indexOfScale+6, transformString.length-1));
					}
				}
				return "translate(" + d.x + "," + d.y + ") scale("+scale+")";
			});

		if(panel=="viz"){
			var sessionsStore = _metExploreViz.getSessionsSet();
			var session = _metExploreViz.getSessionById(panel);
			if(session.isLinked()){
				for (var key in sessionsStore) {
					if(sessionsStore[key].isLinked() && panel!=sessionsStore[key].getId() && d3.select("#"+sessionsStore[key].getId()).select("#D3viz").select("#graphComponent")[0][0]!=null)
					{
						d3.select("#"+sessionsStore[key].getId()).select("#D3viz").select("#graphComponent")
							.selectAll("g.node")
							.each(function(node){
								d3.select("#viz").select("#D3viz").select("#graphComponent")
									.selectAll("g.node")
									.each(function(d){
										if(d.getId() == node.getId())
										{
											// Align nodes with the main graph
											node.x= d.x;
											node.y = d.y;
										}
									});
							});

						var scaleSess = metExploreD3.getScaleById(sessionsStore[key].getId());
    
						metExploreD3.GraphLink.tick(sessionsStore[key].getId(), scaleSess);
						_MyThisGraphNode.tick(sessionsStore[key].getId());
					}
				}
			}
		}	
	},

	/*******************************************
	* Return data corresponding to the node
	* @param {} panel : The panel where the action is launched
	*/
	selectNodeData : function(node){
		return d3.select(node).datum();
	}, 

	/*******************************************
    * Function to select node (front-end)  
    * @param {} node : a set of nodes 
    */
    selectNodeFromGrid: function(id){
		d3.select("#viz").select("#D3viz")
            .selectAll("g.node")
            .filter(function(d){
                return d.getId()==id;
            })
            .each(function(d){
                if(!d.isSelected())
                    _MyThisGraphNode.selection(d, "viz")
            });
	},

	/*******************************************
	* Assign color according to metabolite compartment
	* @param {} selection : The selection of
	*/
	colorStoreByCompartment: function(selection){
		for(var i=0 ; i<metExploreD3.getCompartmentInBiosourceLength() ; i++){
	 		
 			selection
	 			.filter(function(d) {
	 				return (d.getBiologicalType() =='metabolite' 
	 					&& d.getCompartment()==metExploreD3.getCompartmentInBiosourceSet()[i].getIdentifier() );
	 			})
	            .selectAll("rect")
	            .style("stroke",metExploreD3.getCompartmentInBiosourceSet()[i].getColor()); 
        }
	},

	unselectIfDBClick : function() { 
		if(d3.event.target==d3.select("#D3viz")[0][0])
			document.getElementById("tooltip2").classList.remove("fixed");
		
		if(_MyThisGraphNode.dblClickable && d3.event.button==0){
			_MyThisGraphNode.activePanel = this.parentNode.id;
         	d3.select(this).select("#graphComponent")
				.selectAll("g.node")
		        .filter(function(d) { return d.isSelected(); })
		        .each(function(d) { _MyThisGraphNode.selection(d, _MyThisGraphNode.activePanel); });
		}
		else
		{
			if(d3.event.button==0){
				_MyThisGraphNode.dblClickable = true;

				_MyThisGraphNode.taskClick = metExploreD3.createDelayedTask(
					function(){
                        _MyThisGraphNode.dblClickable=false;
                	}
                );

				metExploreD3.fixDelay(_MyThisGraphNode.taskClick, 400); 
			}
		}	 
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
							if(metExploreD3.GraphNetwork.isAnimated(sessionMain.getId()) == 'true' 
								|| metExploreD3.GraphNetwork.isAnimated(sessionMain.getId()) == null) {
									force.start();
							}
						}
					}
				}
			}
			else
			{	
				
				var force = session.getForce();
				var animLinked=metExploreD3.GraphNetwork.isAnimated(session.getId());
				if (animLinked=='true') {
					var force = session.getForce();
					if(force!=undefined)  
					{		
						if((metExploreD3.GraphNetwork.isAnimated(session.getId()) == 'true') 
							|| (metExploreD3.GraphNetwork.isAnimated(session.getId())  == null)) {
								force.start();
						}
					}
				}
			}
		}
	},

	/*******************************************
	* To load nodes in visualization
	* @param {} panel : The panel where the action is launched
	*/
	loadNode : function(parent) {
		d3.select("body")
		    .on("keydown", function() {
		    	_MyThisGraphNode.charKey = d3.event.keyCode;
              	_MyThisGraphNode.ctrlKey = d3.event.ctrlKey;
		    })
		    .on("keyup", function(e) {
		    	_MyThisGraphNode.charKey = 'none';
              	_MyThisGraphNode.ctrlKey = d3.event.ctrlKey;
		    });

		metExploreD3.GraphNode.panelParent = parent;

		_MyThisGraphNode = metExploreD3.GraphNode;

		// Load user's preferences
		var reactionStyle = metExploreD3.getReactionStyle();
		
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();
		var generalStyle = metExploreD3.getGeneralStyle();

		var session = _metExploreViz.getSessionById(parent);
		var sessionMain = _metExploreViz.getSessionById('viz');

		var networkData=session.getD3Data();
	    var h = parseInt(d3.select("#"+_MyThisGraphNode.panelParent).select("#D3viz")
			.style("height"));
	    var w = parseInt(d3.select("#"+_MyThisGraphNode.panelParent).select("#D3viz")
			.style("width"));

	    // Create function to manage double click
	    d3.selectAll("#D3viz")
			.on("mouseup", this.unselectIfDBClick)
	 
	 	var scale = metExploreD3.getScaleById(parent);

	 	/***************************/
		// Var which permit to drag
		/***************************/
		var node_drag = d3.behavior.drag()
			.on("dragstart",_MyThisGraphNode.dragstart)
			.on("drag", _MyThisGraphNode.dragmove)
			.on("dragend", _MyThisGraphNode.dragend);

		// For each node we append a division of the class "node"
		metExploreD3.GraphNode.node = d3.select("#"+metExploreD3.GraphNode.panelParent).select("#D3viz").select("#graphComponent").selectAll("g.node")
			.data(networkData.getNodes()).enter()
				.append("svg:g").attr("class", "node")
				.attr("id", function(node){ return "node"+node.getId(); })
				.call(node_drag)
				.style("fill", function(d) { // Here we choose the color of the node if it's selected or not
					if (d.isSelected() == false) {
						return 'white';
					} else {
						return "grey";
					}
				})
				// Here it's the position by default for the beginning of force algorithm
				// .on("click", selection)
				// .style(
				// 	"stroke-dasharray", function(d) {
				// 		if (d.getReactionReversibility()) {
				// 			return "2,2";
				// 		} else {
				// 			return "";
				// 		}
				// 	}
				// )
				.on("mouseenter", function(d) { 

		        	var transform = d3.select(this).attr("transform");
					var scale=transform.substring(transform.indexOf("scale"),transform.length);
					var scaleVal=scale.substring(6, scale.indexOf(')'));		
					if(isNaN(scaleVal))
						scaleVal=1;
					
					var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
					d3.select(this).attr("transform", "translate("+d.x+", "+d.y+") scale("+scaleVal/2+")");
					
					var links = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("path.link");

					if(d.getBiologicalType()=="reaction"){
							
						links.filter(function(link){return d.getId()==link.getSource().getId();})
							.style("stroke", "green")
							// .each(function(link){
							// 	var last = links[0][links.size()-1];
							// 	this.parentNode.insertBefore(this, last);
							// }); 	
						 
						 links.filter(function(link){return d.getId()==link.getTarget().getId();})
							.style("stroke", "red")
							// .each(function(link){
							// 	var last = links[0][links.size()-1];
							// 	this.parentNode.insertBefore(this, last);
							// });  	
					}
					else
					{
						links.filter(function(link){return d.getId()==link.getSource().getId();})
							.style("stroke", "red")
							// .each(function(link){
							// 	var last = links[0][links.size()-1];
							// 	this.parentNode.insertBefore(this, last);
							// }); 	
						 
						links.filter(function(link){return d.getId()==link.getTarget().getId();})
							.style("stroke", "green")
							// .each(function(link){
							// 	var last = links[0][links.size()-1];
							// 	this.parentNode.insertBefore(this, last);
							// }); 
					} 

				})
				.on("mouseover", function(d) { 

		        	var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
			
		        	d3.select(this)
						.each(function(node){
							var last = nodes[0][nodes.size()-1];
							this.parentNode.insertBefore(this, last);
						});

					d.fixed = true;
					// console.log(d);
					
					 
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
		        	var transform = d3.select(this).attr("transform");
					var scale=transform.substring(transform.indexOf("scale"),transform.length);
					var scaleVal=scale.substring(6, scale.indexOf(')'));		
					
					if(isNaN(scaleVal))
						scaleVal=1;
			
					var nodes = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node");
					d3.select(this).attr("transform", "translate("+d.x+", "+d.y+") scale("+scaleVal/2+")");
		        	
					if(!d.isSelected())
						d.fixed = false;
					var linkStyle = metExploreD3.getLinkStyle();  

			   		document.getElementById("tooltip2").classList.add("hide");
			    	// d3.select("#"+parent).select("#D3viz").select('#tooltip')
			    	// 	.classed("hide", true); 
		    		d3.select("#"+parent).select("#D3viz").select("#graphComponent")
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
		        })
		        .filter(function(node){
		        	return node.getMappingDatasLength()>0 && session.getActiveMapping()!=""; 
		        })
				.attr("mapped",function(node){
					var mappingData = node.getMappingDataByNameAndCond(session.getActiveMapping(), session.isMapped());
					return session.getColorMappingById(mappingData.getMapValue());
				})
				.style("fill",function(node){
					var mappingData = node.getMappingDataByNameAndCond(session.getActiveMapping(), session.isMapped());
					return session.getColorMappingById(mappingData.getMapValue());
				});


		// For each metabolite we append a division of the class "rect" with the metabolite style by default or create by the user
		metExploreD3.GraphNode.node.filter(function(d) { return d.getBiologicalType() == 'metabolite' })
			.append("rect")
			.attr("class", function(d) {
							return d.getBiologicalType();
							})
			.attr("id", function(d) {
							return d.getId();
							})
			.attr("identifier", function(d) {
							return d.getId();
							})
			.attr("width", metaboliteStyle.getWidth())
			.attr("height", metaboliteStyle.getHeight())
			.attr("rx", metaboliteStyle.getRX())
			.attr("ry", metaboliteStyle.getRY())
			.attr("transform", "translate(-" + metaboliteStyle.getWidth() / 2 + ",-"
									+ metaboliteStyle.getHeight() / 2
									+ ")")
			.style("stroke", metaboliteStyle.getStrokeColor())
			.style("stroke-width", metaboliteStyle.getStrokeWidth());
		
		// to manage the selection visualization
		metExploreD3.GraphNode.node.filter(function(d) { return d.getBiologicalType() == 'metabolite' ;})
			.append("rect").attr("class","fontSelected")
			.attr("width", metaboliteStyle.getWidth())
			.attr("height", metaboliteStyle.getHeight())
			.attr("rx", metaboliteStyle.getRX())
			.attr("ry", metaboliteStyle.getRY())
			.attr( "transform", "translate(-" + metaboliteStyle.getWidth() / 2 + ",-" + metaboliteStyle.getHeight() / 2 + ")")
			.style("fill-opacity", '0')
			.style("fill", '#000');

		// For each reaction we append a division of the class "rect" with the reaction style by default or create by the user
		metExploreD3.GraphNode.node.filter(function(d) {
						return d.getBiologicalType() == 'reaction';
					})
			.append("rect").attr("class", function(d) {
						return d.getBiologicalType();
					})
			.attr("id", function(d) {
						return d.getId();
					})
			.attr("width", reactionStyle.getWidth())
			.attr("height", reactionStyle.getHeight())
			.attr("rx", reactionStyle.getRX())
			.attr("ry", reactionStyle.getRY())
			.attr( "transform", "translate(-" + reactionStyle.getWidth() / 2 + ",-" + reactionStyle.getHeight() / 2 + ")")
			.style("stroke", reactionStyle.getStrokeColor())
			.style("stroke-width", reactionStyle.getStrokeWidth())
			
		metExploreD3.GraphNode.node.filter(function(d) {
						return d.getBiologicalType() == 'reaction';
					})
			.append("rect").attr("class","fontSelected")
			.attr("width", reactionStyle.getWidth())
			.attr("height", reactionStyle.getHeight())
			.attr("rx", reactionStyle.getRX())
			.attr("ry", reactionStyle.getRY())
			.attr( "transform", "translate(-" + reactionStyle.getWidth() / 2 + ",-" + reactionStyle.getHeight() / 2 + ")")
			.style("fill-opacity", '0')
			.style("fill", '#000');

		
		// Sort compartiments store
		metExploreD3.sortCompartmentInBiosource();
 		
 		// Change reactions stroke color by compartment
 		for(var i=0 ; i<metExploreD3.getCompartmentInBiosourceLength() ; i++){
 		
 			metExploreD3.GraphNode.node
 			.filter(function(d) {
 				return (d.getBiologicalType() =='metabolite' && d.getCompartment()==metExploreD3.getCompartmentInBiosourceSet()[i].getIdentifier() );
 			})
            .selectAll("rect")
            .style("stroke",metExploreD3.getCompartmentInBiosourceSet()[i].getColor()); 
        }
		
		if (networkData.getNodes().length < generalStyle.getReactionThreshold() || !generalStyle.isDisplayedLabelsForOpt()) {
			var minDim = Math.min(metaboliteStyle.getWidth(),metaboliteStyle.getHeight());
			// We define the text for a metabolie WITHOUT the coresponding SVG image 
			metExploreD3.GraphNode.node.filter(function(d) { return d.getLabelVisible() == true; })
				.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
				.filter(function(d) { return d.getSvg() == "undefined" || d.getSvg()==undefined || d.getSvg()==""; })
				.append("svg:text")
		        .attr("fill", "black")
		        .attr("class", function(d) { return d.getBiologicalType(); })
				// .text(function(d) { return $("<div/>").html(d.get(sessionMain.getDisplayNodeName())).text(); })
				.each(function(d) { 
					var el = d3.select(this);
				    var name = metaboliteStyle.getDisplayLabel(d, metaboliteStyle.getLabel());
					name = name.split(' ');
					el.text('');
					for (var i = 0; i < name.length; i++) {
						var nameDOMFormat = $("<div/>").html(name[i]).text();
				        var tspan = el.append('tspan').text(nameDOMFormat);
				        if (i > 0)
				            tspan.attr('x', 0).attr('dy', '5');
				    }
				})
				.style("font-size",metaboliteStyle.getFontSize())
				.style("paint-order","stroke")
				.style("stroke-width", 1)
				.style("stroke", "white")
				.style("stroke-opacity", "0.7")
				// 	function(d) {
				// 		return Math.min(
				// 			(minDim) / 2,
				// 			((minDim - 3)/ this.getComputedTextLength() * 10) / 2
				// 		)+ "px";
				// })
				.attr("dy", ".4em")
				.style("font-weight", 'bold')
				.style("pointer-events", 'none')
				.attr("y",minDim/2+3);

			// We define the text for a metabolie WITH the coresponding SVG image 
			// Text definition
			metExploreD3.GraphNode.node
				.filter(function(d) { return d.getLabelVisible() == true; })
				.filter(function(d) { return d.getBiologicalType() == 'metabolite'; })
				.filter(function(d) { return d.getSvg() != "undefined" && d.getSvg()!=undefined && d.getSvg()!=""; })
				.append("svg:text")
		        .attr("fill", "black")
				.attr("class", function(d) { return d.getBiologicalType(); })
				.each(function(d) { 
					var el = d3.select(this);
				    var name = metaboliteStyle.getDisplayLabel(d, metaboliteStyle.getLabel());
					name = name.split(' ');
					el.text('');
					for (var i = 0; i < name.length; i++) {
				        var nameDOMFormat = $("<div/>").html(name[i]).text();
				        var tspan = el.append('tspan').text(nameDOMFormat);
				        if (i > 0)
				            tspan.attr('x', 0).attr('dy', '7');
				    }
				})
				.style("font-size",metaboliteStyle.getFontSize())
				.style("paint-order","stroke")
				.style("stroke-width", 1)
				.style("stroke", "white")
				.style("stroke-opacity", "0.7")

				// 	function(d) {
				// 		return Math.min(
				// 			(minDim) / 2,
				// 			((minDim - 3)/ this.getComputedTextLength() * 10) / 2
				// 		)+ "px";
				// })
				.attr("dy", ".4em")
				//.attr("y",+(3 / 4 * (minDim/2) ));
				.style("font-weight", 'bold')
				.style("pointer-events", 'none')
				.attr("y",minDim/2+3);

			// Image definition
			metExploreD3.GraphNode.node
				.filter(
					function(d) {
						return (d.getBiologicalType() == 'metabolite' && d.getSvg() != "undefined" && d.getSvg()!=undefined && d.getSvg()!="");
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
				.attr(
						"xlink:href",
						function(d) {
							return "resources/images/structure_metabolite/"
									+ d.getSvg();
						})
				.attr("width", "100%").attr(
						"height", "100%");

			// We define the text for a reaction
			metExploreD3.GraphNode.node
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
					.text(function(d) {
						var text=$("<div/>").html(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())).text();
						if(text=="")
							var text=$("<div/>").html(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())).text();
							// var text=$("<div/>").html(d.get(sessionMain.getDisplayNodeName())).text();

						//text=text.replace(" ","<br>");
						//console.log(text);
						return text;
					})
					.style(
						"font-size",//reactionStyle.getFontSize())
						 function(d) {
						 	if(reactionStyle.getDisplayLabel(d, reactionStyle.getLabel())=='NA')
						 		return 6;
						 	return Math.min(reactionStyle.getWidth(),(reactionStyle.getWidth() - reactionStyle.getWidth()/10)/ this.getComputedTextLength()* 10)+ "px";
					})
					.style("font-weight", 'bold')
					.attr("dy", ".3em");
			
		}

		// Sort compartiments store
		/*	
		metExploreD3.sortCompartmentInBiosource();
 		
 		// Change reactions stroke color by compartment
 		for(var i=0 ; i<metExploreD3.getCompartmentInBiosourceLength() ; i++){
 		
 			metExploreD3.GraphNode.node
 			.filter(function(d) {
 				return (d.getBiologicalType() =='metabolite' && d.getCompartment()==metExploreD3.getCompartmentInBiosourceSet()[i].getIdentifier() );
 			})
            .selectAll("rect")
            .style("stroke",metExploreD3.getCompartmentInBiosource()[i].getColor()); 
        }*/
		metExploreD3.GraphNode.loadPath(metExploreD3.GraphNode.panelParent);

		// metExploreD3.GraphNode.groupFill = function(d, i) { 
		// 	// Sort compartiments store
		// 	console.log(d.key);
		// 	console.log(i);
		// 	console.log(metExploreD3.getCompartmentInBiosourceSet()[i]);
		// 	metExploreD3.sortCompartmentInBiosource();
	 // 		var color;
	 // 		// Change reactions stroke color by compartment
	 // 		for(var j=0 ; j<metExploreD3.getCompartmentInBiosourceLength() ; j++){
	 // 			if(d.key==metExploreD3.getCompartmentInBiosourceSet()[j].getIdentifier() )
	 // 				color = metExploreD3.getCompartmentInBiosource()[j].getColor();
	 //        return color;
		// };
		// 62771 ms for recon before refactoring
		// 41465 ms now
		// var endall = new Date().getTime();
		// var timeall = endall - startall;
		// console.log("----Viz: FINISH refresh/ all "+timeall);
	},

	/*****************************************************
	* Set side compounds from array of nodes
	* @param {} sideCompounds : An array of id
	* @return {} bool : true if at less one is find
	*/
	loadSideCompounds : function(sideCompounds, func) {
	    var array = [];
	  	sideCompounds.forEach(function(sideCompound){
	    	var node = _metExploreViz.getSessionById("viz").getD3Data().getNodeByDbIdentifier(sideCompound);

			if(node!=null){
				if(metExploreD3.getMetabolitesSet()!=undefined){
					var theMeta = metExploreD3.getMetaboliteById(metExploreD3.getMetabolitesSet(), node.getId());
					if(theMeta!= null)
						theMeta.set("sideCompound", true);
				}	
				node.setIsSideCompound(true);	
				array.push(node);
			}	
	    });
	    if (func!=undefined) {func()};
	    return array.length > 0;
	},

	/*******************************************
	* To load nodes in visualization
	* @param {} panel : The panel where the action is launched
	*/
	setIsSideCompoundById : function(idM, val) { 
        var networkData = _metExploreViz.getSessionById("viz").getD3Data();
		var nodes = networkData.getNodes();
       	if(nodes!=undefined)
        {
            var node=networkData.getNodeById(idM);
            if(node!=undefined)
                node.setIsSideCompound(val);
            
            var sessions =  _metExploreViz.getSessionsSet();
            for (var key in sessions) {                     
                if(sessions[key].getId()!='viz')
                {
                    var nodeLinked = sessions[key].getD3Data().getNodeById(idM)
                    nodeLinked.setIsSideCompound(val);
                    if(nodeLinked!=undefined)
                        nodeLinked.setIsSideCompound(val);
                }
            }    
        }
    },

	/*******************************************
	* Init the visualization of links
	* @param {} parent : The panel where the action is launched
	* @param {} component : pathway or compartment
	*/
	loadPath : function(parent, component) {
		var session = _metExploreViz.getSessionById(parent);
		
		if(component=="Compartments"){
			var metabolites = d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("g.node").filter(function(d) { return d.getBiologicalType() == 'metabolite'; });
		
			session.groups = metExploreD3.getCompartmentsGroup();
			metExploreD3.GraphNetwork.initCentroids();
		}
		else
		{
			session.groups = metExploreD3.getPathwaysGroup();
			metExploreD3.GraphNetwork.initCentroids();
		}

		
        metExploreD3.GraphNode.groupPath = function(d) {
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

		metExploreD3.GraphNode.groupFill = function(d, i) { 

			// Sort compartiments store
			// metExploreD3.sortCompartmentInBiosource();
	 		var color;
	 		// Change reactions stroke color by compartment
	 		if(component=="Compartments"){
				// Change reactions stroke color by compartment
		 		for(var j=0 ; j<metExploreD3.getCompartmentInBiosourceLength() ; j++){
		 			if(d.key==metExploreD3.getCompartmentInBiosourceSet()[j].getName()) 
		 				color = metExploreD3.getCompartmentInBiosourceSet()[j].getColor();
		 		}
		        return color;
			}
			else
			{

				var phase = metExploreD3.getPathwaysLength();
		        if (phase == undefined) phase = 0;
		        center = 128;
		        width = 127;
		        frequency = Math.PI*2*0.95/phase;


				var red   = Math.sin(frequency*i+2+phase) * width + center;
				var green = Math.sin(frequency*i+0+phase) * width + center;
				var blue  = Math.sin(frequency*i+4+phase) * width + center;
		 
				var color = metExploreD3.GraphUtils.RGB2Color(red,green,blue);
				d.color = color;
				return color;
				/*var color = d3.scale.linear()
				    .domain([0, metExploreD3.getPathwaysLength()/2, metExploreD3.getPathwaysLength()-1])
				    .range(["red", "black", "green"]);
		        return color(i);*/
			}
		};

		var pathTab = "M0,0L10,10Z";

		// If you want to use selection on compartments path
		// d3.select("#"+metExploreD3.GraphNode.panelParent).select("#D3viz").select("graphComponent").selectAll("path")
		// 	.enter().insert("path", "g.node")

		d3.select("#"+parent).select("#D3viz").selectAll("path")
		    .filter(function(d){return $(this).attr('class')!="linkCaptionRev" && $(this).attr('class')!="link"})
		    .data(session.groups)
		    .attr("d", function(d){ return pathTab; })
		    .enter().insert("path", ":first-child")
				.attr("class", function(d){ return d.key; })
				.attr("id", function(d){ return d.key; })
				.style("fill", metExploreD3.GraphNode.groupFill)
				.style("stroke", metExploreD3.GraphNode.groupFill)
				.style("stroke-width", 40)
				.style("stroke-linejoin", "round")
				.style("opacity", .15)
				
	}
}