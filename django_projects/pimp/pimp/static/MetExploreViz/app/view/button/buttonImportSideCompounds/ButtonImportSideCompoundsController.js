/**
 * This class is the controller for the main view for the application. It is specified as
 * the "controller" of the Main view class.
 *
 * TODO - Replace this content of this view to suite the needs of your application.
 */
Ext.define('metExploreViz.view.button.buttonImportSideCompounds.ButtonImportSideCompoundsController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.buttonImportSideCompounds',
   
    init: function() {
		var me=this,
		viewModel = me.getViewModel(),
		view      = me.getView();	

		view.lookupReference('importSideCompoundsHidden').on({
			change:function(){
				metExploreD3.GraphUtils.handleFileSelect(view.lookupReference('importSideCompoundsHidden').fileInputEl.dom, me.loadData);
			},
			scope:me
		});

	},

	/*****************************************************
	* Load data from file and launch setting of SC 
	*/
	loadData : function(tabTxt) {
		tabTxt = tabTxt.replace(/\r/g, "");
	    var sideCompounds = tabTxt.split('\n');
	    var find = metExploreD3.GraphNode.loadSideCompounds(sideCompounds);

      	if(find)
	    	metExploreD3.displayMessage("MetExploreViz", "Side compounds are imported!");
	    else	    
	    	metExploreD3.displayMessage("MetExploreViz Warning", "Side compounds not found!");
	
	}
});
