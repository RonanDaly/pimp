Ext.define('metExploreViz.view.menu.viz_DrawingMenu.Viz_DrawingMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizDrawingMenu-vizDrawingMenu',

/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();

		view.on({
			mouseleave: function( menu, e, eOpts){
				menu.hide();
			},
	  		scope:me
     	});

		view.lookupReference('removeSideCompounds').on({
			click : me.removeSideCompounds,
			scope : me
		});

		view.lookupReference('duplicateSideCompounds').on({
			click : me.duplicateSideCompounds,
			scope : me
		});

		view.lookupReference('clustMetabolites').on({
			click : me.clustMetabolites,
			scope : me
		});

		view.lookupReference('makeClusters').on({
			click : me.makeClusters,
			scope : me
		});
		view.on({
			enableMakeClusters : function(){
				this.lookupReference('makeClusters').setDisabled(false);
			},
			scope : me
		});
		view.on({
			disableMakeClusters : function(){
				this.lookupReference('makeClusters').setDisabled(true);	
			},
			scope : me
		});
	},
	duplicateSideCompounds : function(){
		metExploreD3.GraphNetwork.duplicateSideCompounds('viz');
	},
	clustMetabolites : function(){
		if(!_metExploreViz.isLinkedByTypeOfMetabolite()){
			metExploreD3.GraphLink.linkTypeOfMetabolite();
			this.getView().lookupReference('clustMetabolites').setIconCls("metabolitesUnlinkedByType");
			this.getView().lookupReference('clustMetabolites').setTooltip('Release force between substrates/products');
		}
		else
		{
			metExploreD3.GraphLink.removeLinkTypeOfMetabolite();
			this.getView().lookupReference('clustMetabolites').setIconCls("metabolitesLinkedByType");
			this.getView().lookupReference('clustMetabolites').setTooltip('Draw closer substrates/products');
		}
		
	},
	makeClusters : function(){
		var useClusters = metExploreD3.getGeneralStyle().useClusters();
		metExploreD3.getGeneralStyle().setUseClusters(!useClusters);
		
		if(!useClusters){
			this.getView().lookupReference('makeClusters').setIconCls("unmakeClusters");
			this.getView().lookupReference('makeClusters').setTooltip('Release force for clusters');
			this.getView().lookupReference('makeClusters').setText("Unmake clusters");
		}
		else
		{
			this.getView().lookupReference('makeClusters').setIconCls("makeClusters");
			this.getView().lookupReference('makeClusters').setTooltip('Make clusters in function of highlighted component');
			this.getView().lookupReference('makeClusters').setText("Make clusters");
		}
		var session = _metExploreViz.getSessionById('viz');
		if((metExploreD3.GraphNetwork.isAnimated(session.getId()) == 'true') 
							|| (metExploreD3.GraphNetwork.isAnimated(session.getId())  == null))
			session.getForce().resume();
		
	},
	removeSideCompounds : function(){
		metExploreD3.GraphNetwork.removeSideCompounds();
	}
});