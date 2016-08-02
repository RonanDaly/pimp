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

		if(targetName[0]=="reactionDBIdentifier" || targetName[0]=="metaboliteDBIdentifier" || targetName[0]=="reactionId" || targetName[0]=="metaboliteId" || targetName[0]=="inchi")
		{
		    var mapping = new Mapping(title, firstLine, targetName[0], array);
		    _metExploreViz.addMapping(mapping);

		    for (var i = lines.length - 1; i >= 0; i--) {
		    	lines[i] = lines[i].split('\t');
		    };
		    metExploreD3.GraphMapping.mapNodeData(mapping, lines);
		    metExploreD3.fireEventArg('selectMappingVisu', "jsonmapping", mapping);
		}
		else
		{
			// Type ERROR
			metExploreD3.displayWarning("Syntaxe error", 'File have bad syntax. See <a href="http://metexplore.toulouse.inra.fr/metexploreViz/doc/documentation.php#import">MetExploreViz documentation</a>.');
		}
	}
});
