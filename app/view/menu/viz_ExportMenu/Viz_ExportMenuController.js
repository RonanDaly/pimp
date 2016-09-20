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

		// view.lookupReference('exportComparison').on({
		// 	click : me.exportComparison,
		// 	scope : me
		// });

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
	// ,
	// exportComparison : function(){
	// 	if(_metExploreViz.getComparedPanelsLength()==2){
	// 		// Ext.create('Ext.window.Window', {
	// 		//     title: 'Hello',
	// 		//     height: '100%',
	// 		//     width: '100%',
	// 		//     layout: 'fit',
	// 		//     autoScroll: true,
	// 		//     items: {  // Let's put an empty grid in just to illustrate fit layout
	// 		//         xtype: 'panel', // A dummy empty data store
	// 		//         listeners: {
	// 		//         	render : function(){
	// 		//         		var chart = metExploreD3.GraphMapping.compareMappingConditionChart();
	// 		// 				chart.exportChart();
	// 		//         		document.getElementById(this.id).insertBefore(chart, document.getElementById(this.id).firstChild);
     //
	// 		//         	}
	// 		//         }
	// 		//     }
	// 		// }).show();
    	// 	var chart = metExploreD3.GraphMapping.compareMappingConditionChart();
	// 		chart.exportChart();
	// 	}
	// }
});