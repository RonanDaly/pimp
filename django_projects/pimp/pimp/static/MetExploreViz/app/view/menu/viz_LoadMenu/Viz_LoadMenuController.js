Ext.define('metExploreViz.view.menu.viz_LoadMenu.Viz_LoadMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizLoadMenu-vizLoadMenu',

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

		view.on({
			cartFilled: function(){
				view.lookupReference('loadNetworkFromWebsite').setDisabled(false);
			},
	  		scope:me
     	});
     	
		view.lookupReference('loadNetworkFromJSON').on({
			click : function(){
				// console.log(Ext.getCmp("IDload"));
				// console.log(Ext.getCmp("buttonMap"));
				var component = Ext.getCmp("IDimportNetwork");
		        if(component!= undefined){
					component.fileInputEl.dom.click();
		        }
			},
			scope : me
		});

		view.lookupReference('loadNetworkFromWebsite').on({
			click : function(){
		        	metExploreD3.GraphPanel.refreshPanel(_metExploreViz.getDataFromWebSite());
			},
			scope : me
		});
	},

	loadMapping : function(){
		metExploreD3.GraphMapping.loadMapping();
	}
});