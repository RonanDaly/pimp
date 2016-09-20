/**
 * This class is the controller for the main view for the application. It is specified as
 * the "controller" of the Main view class.
 *
 * TODO - Replace this content of this view to suite the needs of your application.
 */
Ext.define('metExploreViz.view.button.buttonImportToNetwork.ButtonImportToNetworkController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.buttonImportToNetwork',
   
    init: function() {
		var me=this,
		viewModel = me.getViewModel(),
		view      = me.getView();		

		view.lookupReference('importNetwork').on({
			change: function () {
				metExploreD3.GraphUtils.handleFileSelect(view.lookupReference('importNetwork').fileInputEl.dom, metExploreD3.GraphPanel.refreshPanel);
            },
            scope : me
		});

		view.on({
			reloadMapping:me.reloadMapping,
			scope:me
		});
	},

	

	reloadMapping : function(bool){
	    if(_metExploreViz.getMappingsLength()!=0){
	    	var component = Ext.getCmp('comparisonSidePanel');
	        if(component!= undefined){
				
				var comboMapping = Ext.getCmp('selectMappingVisu');
				var store = comboMapping.getStore();
				store.loadData([], false);
				comboMapping.clearValue();
	            //take an array to store the object that we will get from the ajax response
				var records = [];
				console.log(bool);
				// comboMapping.bindStore(store);
				if(bool){

					var mappings = _metExploreViz.getMappingsSet();
					mappings.forEach(function(mapping){
						records.push(new Ext.data.Record({
		                    name: mapping.getName()
		                }));

						store.each(function(mappingName){
							records.push(new Ext.data.Record({
			                    name: mappingName.getData().name
			                }));
						});
					});

					store.loadData(records, false);
				}        	

                if(store.getCount()==0)
                	comboMapping.setDisabled(true);
	        }
	    }

		var comboCond = Ext.getCmp('selectCondition');
		var addCondition = Ext.getCmp('addCondition');
		var selectConditionType = Ext.getCmp('selectConditionType');
		
		if(addCondition!=undefined && selectCondition!=undefined && selectConditionType!=undefined){					
			comboCond.clearValue();

			addCondition.setDisabled(true);
			addCondition.setTooltip('You must choose a condition to add it');
				
			comboCond.setDisabled(true);
			selectConditionType.setDisabled(true);

		}

		var networkVizSession = _metExploreViz.getSessionById("viz");
		var that = this;
		// If the main network is already mapped we inform the user: OK/CANCEL
		// if(networkVizSession.isMapped()!='false')	
		// {
	        	
		// 	var newMapping ='true';
		// 	me.closeMapping(newMapping);
		// }
	}
});
