Ext.define('metExploreViz.view.panel.comparisonSidePanel.ComparisonSidePanelController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.panel-comparisonSidePanel-comparisonSidePanel',

	// requires:['metexplore.model.d3.Network','metexplore.global.Graph'],


/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();

		view.on({
			newMapping : me.drawCaption,
			scope:me
		});
	},
	
	drawCaption : function(){
		metExploreD3.GraphCaption.drawCaption();
	}
});