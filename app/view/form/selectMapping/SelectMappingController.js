/**
 * @author MC
 * @description class to control contion selection panel
 * C_SelectMapping
 */

Ext.define('metExploreViz.view.form.selectMapping.SelectMappingController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.form-selectMapping-selectMapping',

	// config : {
	// 	stores : [ 'S_MappingInfo' ],
	// 	views : [ 'view.form.SelectMapping']
	// },
	/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();

		view.on({
			jsonmapping : function(mappingJSON){
				me.initMapping(mappingJSON);
			},
			removemapping : function(mapping){
				me.removeMapping(mapping);
			},
			change : function(that, newMapping, old){
				// if(view.getStore().getCount()>0){
					var component = Ext.getCmp("selectConditionForm");
					
			        if(component!= undefined){
			        	_metExploreViz.getSessionById('viz').setActiveMapping(newMapping);
			            component.fireEvent("closeMapping", newMapping);
						var mappings = _metExploreViz.getMappingsSet();
						if (_metExploreViz.getMappingsLength()!=0) {
							
							var theMapping = _metExploreViz.getMappingByName(newMapping);
							if(theMapping!=null)
							{
								var conds = theMapping.getConditions();
								if(theMapping != undefined)
									me.fillComboSelectCondition(that, theMapping, old);
							}
						}
			        }
				// }	
			},
			collapse : function(field, eOpts){
				var mappings = _metExploreViz.getMappingsSet();
				if (_metExploreViz.getMappingsLength()!=0) {
					
					var theMapping = _metExploreViz.getMappingByName(field.getValue());
					if(theMapping != undefined)
						metExploreD3.GraphMapping.mapNodes(theMapping.getName());
				}
			},
			scope:me
		});
	},

	initMapping:function(mappingJSON){
		if(_metExploreViz.getMappingsLength()!=0 ){
	    	
	    	var component = Ext.getCmp('comparisonSidePanel');
	        if(component!= undefined){
	        	if(component.isHidden())
	           		component.setHidden(false);
				component.expand();
				var comboMapping = Ext.getCmp('selectMappingVisu');
				comboMapping.setValue(mappingJSON.getName());
				
				var store = comboMapping.getStore();
	            //take an array to store the object that we will get from the ajax response
				var records = [];

				// comboMapping.bindStore(store);
				     
				records.push(new Ext.data.Record({
                    name: mappingJSON.getName()
                }));

				store.each(function(mappingName){
					records.push(new Ext.data.Record({
	                    name: mappingName.getData().name
	                }));
				});
				_metExploreViz.getSessionById('viz').setActiveMapping(mappingJSON.getName());
				store.loadData(records, false);
                
                if(store.getCount()==1)
                	comboMapping.setDisabled(false);
	        }
	    }
	},

	removeMapping:function(mapping){
	    	var component = Ext.getCmp('comparisonSidePanel');
	        if(component!= undefined){
	        	if(component.isHidden())
	           		component.setHidden(false);
				component.expand();
				var comboMapping = Ext.getCmp('selectMappingVisu');
				var store = comboMapping.getStore();
	            //take an array to store the object that we will get from the ajax response
				var records = [];

				store.each(function(mappingName){
					if(mappingName.getData().name!=mapping.getName()){
						records.push(new Ext.data.Record({
		                    name: mappingName.getData().name
		                }));
					}
				});

				store.loadData(records, false);
                
				comboMapping.clearValue();

                if(store.getCount()==0)
                	comboMapping.setDisabled(true);
	        }
	},

	/*******************************************
	* Affect selected mapping conditions to the comboBox: SelectCondition 
	* @param {} that 
	* @param {} newMapping : id of new mapping
	* @param {} old 
	*/
	fillComboSelectCondition : function(that, newMapping, old) {

		_metExploreViz.getSessionById('viz').setMapped("false");
			            
		var mappingInfoStore = _metExploreViz.getMappingsSet();
		var conditions = newMapping.getConditions();
		var comboCond = Ext.getCmp('selectCondition');
		var storeCond = comboCond.getStore();
        //take an array to store the object that we will get from the ajax response
		var record = [];
         	
		for (var i = 0 ; i<conditions.length ; i++) {
			record.push({
	            name : conditions[i]
	        });
		}

		storeCond.loadData(record, false);
		var nbCond = storeCond.getCount();
		if(nbCond>=1)
            comboCond.setDisabled(false);

        comboCond.setValue(storeCond[0]);

		var selectConditionType = Ext.getCmp('selectConditionType');
		
		if(selectCondition!=undefined && selectConditionType!=undefined){

			if(nbCond<1  || (nbCond==1 && conditions[0]=="undefined")){
 			
 				comboCond.clearValue();
 				comboCond.setDisabled(true);
 				selectConditionType.setDisabled(true);
 			}
 			else
 			{
				selectConditionType.setValue(selectConditionType.getStore().first()); 
				comboCond.setValue(storeCond.first());   
 				
 				comboCond.setDisabled(false);
 				selectConditionType.setDisabled(false);
 			}
		}
	}	
});