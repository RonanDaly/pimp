/**
 * This class is the controller for the main view for the application. It is specified as
 * the "controller" of the Main view class.
 *
 * TODO - Replace this content of this view to suite the needs of your application.
 */
Ext.define('metExploreViz.view.button.buttonImportMapping.ButtonImportMappingController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.buttonImportMapping',
   
    init: function() {
		var me=this,
		viewModel = me.getViewModel(),
		view      = me.getView();	

		view.lookupReference('importMappingHidden').on({
			change:function(){
				console.log(view.lookupReference('importMappingHidden').fileInputEl.dom);
				metExploreD3.GraphUtils.handleFileSelect(view.lookupReference('importMappingHidden').fileInputEl.dom, me.loadData);
			},
			scope:me
		});

		view.on({
			reloadMapping:function(){
				view.reset();
			},
			scope:me
		});
	},

	/*****************************************************
	* Update the network to fit the cart content
	*/
	loadData : function(tabTxt, title) {
		var data = tabTxt;
		tabTxt = tabTxt.replace(/\r/g, "");
	    var lines = tabTxt.split('\n');

	    var firstLine = lines.splice(0, 1);
	    firstLine = firstLine[0].split('\t');
	   
	    var targetName = firstLine.splice(0, 1);
	    var array = [];
	    var mapping = new Mapping(title, firstLine, targetName[0], array);
	    _metExploreViz.addMapping(mapping);	 
	   

	    for (var i = lines.length - 1; i >= 0; i--) {
	    	lines[i] = lines[i].split('\t');
	    };
	    metExploreD3.GraphMapping.mapNodeData(mapping, lines);
	    metExploreD3.fireEventArg('selectMappingVisu', "jsonmapping", mapping);
	}
});
