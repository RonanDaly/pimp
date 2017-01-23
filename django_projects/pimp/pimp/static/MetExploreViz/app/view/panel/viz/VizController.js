Ext.define('metExploreViz.view.panel.viz.VizController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.panel-viz-viz',

	// requires:['metexplore.model.d3.Network','metexplore.global.Graph'],


/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();

		view.on({
			initiateViz : me.initiateViz,
			scope:me
		});

		view.on({
			resize : function() {
				metExploreD3.GraphPanel.resizeViz("viz");
				var session = _metExploreViz.getSessionById("viz");
	    		// if visualisation is actived we add item to menu
	    		if(session.isActive()){
				
					metExploreD3.GraphPanel.resizePanels('viz');
				}
			},
			scope:me
		});
	},
	/*****************************************************
	* Initialization of visualization
    * @param {} vizEngine : library used to make the visualization
	*/
	initiateViz : function() {
		
		$("#viz").on('contextmenu', function(e) {		
			// devalide le menu contextuel du navigateur
			e.preventDefault();
			var networkVizSessionStore = _metExploreViz.getSessionById("viz");
			// Define the right click to remove elements and display information
			var viz = Ext.getCmp('viz');
			if(viz!= undefined){
				if(e.target.id=="D3viz" 
					|| e.target.parentNode.parentNode.id=="D3viz" 
					|| e.target.parentNode.id=="graphComponent") 
				{
					if(networkVizSessionStore.getSelectedNodes().length!=0)
					{
						viz.CtxMenu = new Ext.menu.Menu({
							items : [{
								text : 'Remove selected nodes',
								hidden : false,
								iconCls:"removeNode",
								handler :function(){ metExploreD3.GraphNetwork.removeSelectedNode("viz") }
							},{
								text : 'Fix selected nodes',
								hidden : false,
								iconCls:"lock_font_awesome",
								handler :function(){ metExploreD3.GraphNode.fixSelectedNode("viz") }
							},{
								text : 'Side compounds (duplicate)',
								hidden : false,
								iconCls:"duplicate-sideCompounds",
								handler : function(){ 
									var sessio = _metExploreViz.getSessionById('viz');
									metExploreD3.GraphNetwork.duplicateSideCompoundsSelected("viz"); 
								}
							}]
						});
					}
				}
				else
				{

					if(e.target.id=='')
					{	
						if(e.target.parentNode.textContent!=""){
							if(e.target.previousSibling.previousSibling==null) 
								var target = e.target.previousSibling;
							else
								var target = e.target.previousSibling.previousSibling;
								
						}
						else
							var target = e.target.parentNode.parentNode.firstChild;


					}
					else
						var target = e.target;


					var theNode = metExploreD3.GraphNode.selectNodeData(e.target);
					var isMetabolite = (theNode.getBiologicalType()=="metabolite");
					
					viz.CtxMenu = new Ext.menu.Menu({
						items : [
						{
							text : 'Remove the node',
							hidden : false,
							iconCls:"removeNode",
							handler : function(){
							 	metExploreD3.GraphNetwork.removeOnlyClickedNode(theNode, "viz"); 
							}	
						},{
							text : 'Side compound (duplicate)',
							hidden : !isMetabolite,
							iconCls:"duplicate-sideCompounds",
							handler : function(){ 
								metExploreD3.GraphNetwork.duplicateASideCompoundSelected(theNode, "viz"); 
							}
						},{
							text : 'Change name',
							hidden : false,
							iconCls:"edit",
							handler : function(){ 
								metExploreD3.GraphNode.changeName(theNode); 
							}
						},{
							text : 'Select neighbours (N+select)',
							hidden : false,
							iconCls:"neighbours",
							handler : function(){ 
								metExploreD3.GraphNode.selectNeighbours(theNode, "viz"); 
							}
						}
						,{
							text : 'See more information',
							hidden : !metExploreD3.getGeneralStyle().hasEventForNodeInfo(),
							iconCls:"info",
							handler : function() {
								metExploreD3.fireEventParentWebSite("seeMoreInformation", theNode);
							}
						}
						]
					});
				}
			}
			
			// positionner le menu au niveau de la souris
			if(viz.CtxMenu!=undefined)
				viz.CtxMenu.showAt(e.clientX, e.clientY);
		});	
	}

});