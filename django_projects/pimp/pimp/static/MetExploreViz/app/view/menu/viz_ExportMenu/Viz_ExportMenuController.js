Ext.define('metExploreViz.view.menu.viz_ExportMenu.Viz_ExportMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizExportMenu-vizExportMenu',

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
     	
		view.lookupReference('exportSVG').on({
			click : me.exportSVG,
			scope : me
		});

		view.lookupReference('exportPNG').on({
			click : me.exportPNG,
			scope : me
		});

		view.lookupReference('exportJPG').on({
			click : me.exportJPG,
			scope : me
		});

	},
	exportSVG : function(){
		metExploreD3.GraphUtils.exportSVG();
	},
	exportPNG : function(){
		metExploreD3.GraphUtils.exportPNG();
	},
	exportJPG : function(){
		metExploreD3.GraphUtils.exportJPG();
	}
});