Ext.define('metExploreViz.view.menu.viz_ImportMenu.Viz_ImportMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizImportMenu-vizImportMenu',

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
     	
		view.lookupReference('importMapping').on({
			click : function(){
				// console.log(Ext.getCmp("IDimport"));
				// console.log(Ext.getCmp("buttonMap"));
				var component = Ext.getCmp("IDimportMapping");
		        if(component!= undefined){
					component.fileInputEl.dom.click();
		        }
			},
			scope : me
		});

		view.lookupReference('importSideCompounds').on({
			click : function(){
				// console.log(Ext.getCmp("IDimport"));
				// console.log(Ext.getCmp("buttonMap"));
				var component = Ext.getCmp("IDimportSideCompounds");
		        if(component!= undefined){
					component.fileInputEl.dom.click();
		        }
			},
			scope : me
		});
	},

	importMapping : function(){
		metExploreD3.GraphMapping.importMapping();
	}
});