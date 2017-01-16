Ext.define('metExploreViz.view.menu.viz_AlgorithmMenu.Viz_AlgorithmMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizAlgorithmMenu-vizAlgorithmMenu',

/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();
		
		// view.on({
		// 	setGeneralStyle : function(){
		// 		console.log("vizAlgorithmMenusetGeneralStyle", view.lookupReference('highlightCompartments'));
		// 		var s_GeneralStyle = _metExploreViz.getGeneralStyle();
		// 		console.log(s_GeneralStyle.isDisplayedConvexhulls());
		// 		console.log(s_GeneralStyle.useClusters());
		// 		if(s_GeneralStyle.isDisplayedConvexhulls()=="Compartments"){
		// 			view.lookupReference('highlightCompartments').setChecked(true);  
		// 			metExploreD3.fireEvent("vizIdDrawing", "enableMakeClusters");
					
		// 			if(s_GeneralStyle.useClusters()){
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setIconCls("unmakeClusters");
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setTooltip('Release force for clusters');
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setText("Unmake clusters");
		// 			}
		// 			else
		// 			{
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setIconCls("makeClusters");
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setTooltip('Make clusters in function of highlighted component');
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setText("Make clusters");
		// 			}
		// 		} 
		// 		else
		// 		{
		// 			if(s_GeneralStyle.isDisplayedConvexhulls()=="Pathways"){
		// 				view.lookupReference('highlightPathways').setChecked(true);  
		// 				metExploreD3.fireEvent("vizIdDrawing", "enableMakeClusters");
						
		// 				if(s_GeneralStyle.useClusters()){
		// 					Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setIconCls("unmakeClusters");
		// 					Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setTooltip('Release force for clusters');
		// 					Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setText("Unmake clusters");
		// 				}
		// 				else
		// 				{
		// 					Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setIconCls("makeClusters");
		// 					Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setTooltip('Make clusters in function of highlighted component');
		// 					Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setText("Make clusters");
		// 				}
		// 			}
		// 			else
		// 			{
		// 				view.lookupReference('highlightCompartments').setChecked(false);  
		// 				view.lookupReference('highlightPathways').setChecked(false);  
		// 				metExploreD3.fireEvent("vizIdDrawing", "disableMakeClusters");

		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setIconCls("makeClusters");
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setTooltip('Make clusters in function of highlighted component');
		// 				Ext.getCmp("vizIdDrawing").lookupReference('makeClusters').setText("Make clusters");
		// 			}
		// 		}
		// 	},
		// 	scope:me
		// });

        view.lookupReference('betweennessCentrality').on({
			click : metExploreD3.GraphFunction.betweennessCentrality,
			scope : me
		});
	}
});