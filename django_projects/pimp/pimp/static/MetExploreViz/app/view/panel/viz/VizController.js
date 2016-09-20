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
								handler :function(){ metExploreD3.GraphNetwork.removeSelectedNode("viz") }
							},{
								text : 'Side compounds (duplicate)',
								hidden : false,
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


					viz.CtxMenu = new Ext.menu.Menu({
						items : [
						{
							text : 'Remove the node',
							hidden : false,
							handler : function(){ metExploreD3.GraphNetwork.removeOnlyClickedNode(metExploreD3.GraphNode.selectNodeData(target.parentNode), "viz"); }	
						},{
							text : 'Side compound (duplicate)',
							hidden : false,
							handler : function(){ metExploreD3.GraphNetwork.duplicateASideCompoundSelected(target.parentNode, "viz"); }
						},{
							text : 'Select neighbour',
							hidden : false,
							handler : function(){ metExploreD3.GraphNode.selectNeighbours(_metExploreViz.getSessionById('viz').getD3Data().getNodeById(target.id), "viz"); }
						}
						,{
							text : 'See more information',
							hidden : !metExploreD3.getGeneralStyle().hasEventForNodeInfo(),
							handler : function() {

								var id = target.id;
								var theNode = _metExploreViz.getSessionById('viz').getD3Data().getNodeById(id);
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