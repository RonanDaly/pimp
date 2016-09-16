/**
 * @author MC
 * controller of graph comparison panel
 */
Ext.define( 'metExploreViz.view.panel.comparePanel.ComparePanelController',{
	extend: 'Ext.app.ViewController',
	alias: 'controller.panel-comparePanel-comparePanel',


	/**
	 * Aplies event linsteners to the view
	 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();
		/*
		view.on({
			afterrender : me.initiateViz('D3'),
			scope:me
		});*/

		view.on({
			initiateviz : this.initiateViz,
			scope:me
		});

		view.on({
			copyNetwork : this.saveNetwork,
			scope:me
		});

		view.on({
			add : function(panel){
				panel.expand(true);
			},
			scope:me
		});

		view.on({
			remove : function(panel, ownerCt){
				if(panel.items.length==0)
					panel.collapse(true);
			},
			scope:me
		});

		view.on({
			beforeremove : function(d,component){
				// If a graph is already loaded
				session = _metExploreViz.getSessionById(component.id+'-body');
				
				if(session!=undefined)  
				{
					// We stop the previous animation
					metExploreD3.GraphNetwork.stopForce(session);
				
					var comparedPanel = _metExploreViz.getComparedPanelById(component.id+'-body');
					if(comparedPanel!=undefined){
						comparedPanel.setVisible(false);
						_metExploreViz.removeComparedPanel(comparedPanel);
					}
					_metExploreViz.removeSession(component.id+'-body');
					metExploreD3.GraphNetwork.looksLinked();
				}
			},
			scope:me
		});		
	},

	/*****************************************************
	* Init global parameters on visualization session
    * @param {} panelId : panel to init
	*/
	onSessionStart : function(panelId) {
		var session = _metExploreViz.cloneSession();
		session.setId(panelId);
    	_metExploreViz.addSession(session);
	},

	/*****************************************************
	* Create the visualization
    * @param {} panelId : panel to init
	*/
	initiateViz : function(panelId) {

		var ctrl= this;
		var networkVizSessionStore = _metExploreViz.getSessionById(panelId);	
		var cmp = panelId.substring(0, panelId.length-5);
		var panelCmp = Ext.getCmp(cmp);
		
		if(panelCmp!=undefined){
			panelCmp.on('resize',function(){
				metExploreD3.GraphPanel.resizeViz(panelId);
				var session = _metExploreViz.getSessionById('viz');
	    		// if visualisation is actived we add item to menu
	    		if(session.isActive()){
					metExploreD3.GraphPanel.resizePanels(panelId);
				}
			})
		}
		
		$("#"+panelId).on('contextmenu', function(e) {							        
			// Devalide le menu contextuel du navigateur
			e.preventDefault();
			
			// Define the right click to remove elements and display information
			var viz = Ext.getCmp("comparePanel");
			if(e.target.parentNode.parentNode.id=="D3viz") 
			{
				if(networkVizSessionStore.getSelectedNodes()!=undefined)
				{
					if(networkVizSessionStore.getSelectedNodes().length!=0)
					{
						viz.CtxMenu = new Ext.menu.Menu({
							items : [{
								text : 'Remove selected nodes',
								hidden : false,
								handler :function(){ metExploreD3.GraphNetwork.removeSelectedNode(panelId) }
							}]
						});
					}
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
						handler : function(){ metExploreD3.GraphNetwork.removeSelectedNode(panelId) }
					},{
							text : 'Select neighbour',
							hidden : false,
							handler : function(){ metExploreD3.GraphNode.selectNeighbours(_metExploreViz.getSessionById(panelId).getD3Data().getNodeById(target.id), panelId); }
						},{
						text : 'See more information',
						hidden : false,
						handler : function() {
							
							var id = target.id;
							if(target.getAttribute('class')=="metabolite")
							{
								var storesMetabolites = Ext.getStore('S_Metabolite');
								var record= storesMetabolites.getMetaboliteById(id);
								var win_InfoMetabolite= Ext.create('MetExplore.view.window.V_WindowInfoMetabolite',
								{
									rec: record
								});
								win_InfoMetabolite.show();
								win_InfoMetabolite.focus();
							}
							else
							{
								var storesReactions = Ext.getStore('S_Reaction');
								var record= storesReactions.getReactionById(id);
								var win_InfoReaction= Ext.create('MetExplore.view.window.V_WindowInfoReaction',
								{
									rec: record
								});
								win_InfoReaction.show();
								win_InfoReaction.focus();
							}
						}
					}
					]
				});
			}
			// positionner le menu au niveau de la souris
			if(viz.CtxMenu!=undefined)
				viz.CtxMenu.showAt(e.clientX, e.clientY);
		}); // Remove the context menu
		
		metExploreD3.GraphNetwork.delayedInitialisation(panelId);
	},


	/*****************************************************
	* Function to draw networks which are saved
    * @param {} panelId : panel to init
	*/
	drawSavedNetwork : function(panelId) {
		
		var vizComp = Ext.getCmp(panelId.substring(0, panelId.length-5));
		if(vizComp!=undefined){
			var myMask = new Ext.LoadMask({
				target:vizComp,
				msg:"Copy in process...", 
				msgCls:'msgClsCustomLoadMask'});
			myMask.show();

			var that = this;
	        setTimeout(
				function() {
					that.onSessionStart(panelId);
					that.initiateViz(panelId);
					metExploreD3.GraphNetwork.setAnimated(panelId, true);
					metExploreD3.GraphNetwork.refreshSvg(panelId);
					
					myMask.hide();
		    }, 100);
		}
	},

	/*****************************************************
	* Function to extract a network
	*/
	saveNetwork : function() {
		if(_metExploreViz.getSessionById('viz').getD3Data() == undefined)
			console.log("Any network to save.");
		else
		{
			console.log("Save the network.");
			// Prompt for user data and process the result using a callback:
			var me 		= this,
			view      	= me.getView();
			view.show();	
			function myPrompt(that){
				Ext.Msg.prompt('Title', 'Please enter the title of network:', 
					function(btn, text){
					    if (btn == 'ok'){
					    	var accord = Ext.getCmp("comparePanel");
								
					    	if(text!="" && accord!=undefined)
					        {
					        	var idPanel = "graph"+_metExploreViz.getComparedPanelsLength();
					        	
								var item = [
					        		{
					        			id:idPanel,
					        			title:text, 
					        			html:"<div id=\""+idPanel+"\" height=\"100%\" width=\"100%\"></div>", 
					        			flex: 1,			
    									cls: 'comparedPanel', 
					        			closable: true, 
					        			collapsible: true, 
					        			collapseDirection: "left" 
					        		}
					        	];
								
								accord.add(item);
								accord.expand();

								newComparedPanel = new ComparedPanel(idPanel+'-body',
																	 true, 
																	 accord.items.keys[accord.items.length-1], text);
								_metExploreViz.addComparedPanel(newComparedPanel);	
								that.drawSavedNetwork(idPanel+'-body');
							}
							else
							{
								alert("Please enter a valid name");
			                    myPrompt(that);
							}
					    }
					}, this, false);
			}	
			myPrompt(this);
		}
	}
});