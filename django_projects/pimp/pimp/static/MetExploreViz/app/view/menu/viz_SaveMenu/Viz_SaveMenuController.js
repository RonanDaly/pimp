Ext.define('metExploreViz.view.menu.viz_SaveMenu.Viz_SaveMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizSaveMenu-vizSaveMenu',

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
     	
		view.lookupReference('exportJSON').on({
			click : me.exportJSON,
			scope : me
		});

		view.lookupReference('exportDOT').on({
			click : me.exportDOT,
			scope : me
		});

		view.lookupReference('exportGML').on({
			click : me.exportGML,
			scope : me
		});
	},
	exportDOT : function(){
		metExploreD3.GraphUtils.saveNetworkDot();
	},
	exportGML : function(){
		metExploreD3.GraphUtils.saveNetworkGml();
	},
	exportJSON : function(){
		metExploreD3.GraphUtils.saveNetworkJSON();
	}
});