Ext.define('metExploreViz.view.menu.viz_MiningMenu.Viz_MiningMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizMiningMenu-vizMiningMenu',

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

     	if(metExploreD3.Features.isEnabled('algorithm')){
			view.lookupReference('vizAlgorithmMenuID').setHidden(false);
		}
     	
	    if(metExploreD3.Features.isEnabled('highlightSubnetwork', "max")){
			view.lookupReference('highlightSubnetwork').setHidden(false);
			view.lookupReference('highlightSubnetwork').on({
				click : me.highlightSubnetwork,
				scope : me
			});
	    }	
		
		view.lookupReference('keepOnlySubnetwork').on({
			click : me.keepOnlySubnetwork,
			scope : me
		});
	},
	highlightSubnetwork : function(){
		metExploreD3.GraphFunction.highlightSubnetwork();
	},
	keepOnlySubnetwork : function(){
		metExploreD3.GraphFunction.keepOnlySubnetwork();
	}
});