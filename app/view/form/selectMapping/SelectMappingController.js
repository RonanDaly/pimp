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
				if(view.getStore().getCount()>0){
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
				}	
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

	
		
	// /*******************************************
	// * Removing of mapping
	// * @param {} newMapping : boolean to know if a new mapping is launched
	// */
	// closeMapping : function(newMapping){

	//     var sessionsStore = Ext.getStore('S_NetworkVizSession');
	// 	var session = sessionsStore.getById('viz');
		
	// 	if(session && session.isMapped()!='false')	
	// 	{
	// 		var container = Ext.getCmp(session.isMapped()+'Panel');

	// 		var addCondition = Ext.getCmp('addCondition'); 
	// 		if(addCondition!=undefined){	
	// 			addCondition.setDisabled(false);
	// 			addCondition.setTooltip('The condition will be add to the network');						
	// 		}
	// 		// Remove mapping caption
	// 		var storeCond = Ext.getStore('S_Condition');
	// 		var cmp = session.isMapped();
	// 		var condition = storeCond.getStoreByCondName(cmp);
	// 		var condInMetabolite = condition.getCondInMetabolite();
	// 		if(newMapping!=undefined)
	// 			this.removeGraphMapping(condInMetabolite);
	// 		container.close();
	// 		var colorStore = Ext.getStore('S_ColorMapping');
	// 		colorStore.each(function(color){
	// 			var newId = color.getName();
	// 			Ext.getCmp('mappingCaptionForm'+newId).close();
	// 		});

	// 		if(session.getMappingDataType()=="Continuous"){
	// 			var colorStore = Ext.getStore('S_ColorMapping');
				        
	// 	        var newColor = colorStore.getCount()==0;
		        
	// 	        if(!newColor){
	// 	        	colorStore.loadData([],false);
	// 	        }
	// 	    }
		    
	// 		var networkVizSessionStore = Ext.getStore('S_NetworkVizSession');
	// 		networkVizSession = networkVizSessionStore.getById("viz");
	// 		networkVizSession.setMapped('false');
	// 	}
	// },
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

		var addCondition = Ext.getCmp('addCondition');
		var selectConditionType = Ext.getCmp('selectConditionType');
		
		if(addCondition!=undefined && selectCondition!=undefined && selectConditionType!=undefined){

			if(nbCond<1  || (nbCond==1 && conditions[0]=="undefined")){
 				addCondition.setDisabled(true);
 				addCondition.setTooltip('You must choose a condition to add it');
						
 				comboCond.clearValue();
 				comboCond.setDisabled(true);
 				selectConditionType.setDisabled(true);
 			}
 			else
 			{
				selectConditionType.setValue(selectConditionType.getStore().first()); 
				comboCond.setValue(storeCond.first());   
 				
 				addCondition.setDisabled(false);
				addCondition.setTooltip('The condition will be add to the network');	
				
 				comboCond.setDisabled(false);
 				selectConditionType.setDisabled(false);
 			}
		}	

	
	}	

	/*******************************************
	// * Affect selected mapping conditions to the comboBox: SelectCondition 
	// * @param {} that 
	// * @param {} newMapping : id of new mapping
	// * @param {} old 
	// */
	// fillComboSelectCondition : function(that, newMapping, old) {
	// 	var mappingInfoStore = _metExploreViz.getMappingsSet();
			
	// 	var conditions = newMapping.getConditions();

	// 	for(var indCond=0;indCond<conditions.length;indCond++){
	// 		storeCond.add({
	// 			'condName' : theMapping.get('id')+"_"+conditions[indCond],
	// 			'condInMetabolite' : theMapping.get('id') + 'map' + indCond
	// 		});
	// 	}	
		

	// 	var addCondition = Ext.getCmp('addCondition');
	// 	var selectCondition = Ext.getCmp('selectCondition');
	// 	var selectConditionType = Ext.getCmp('selectConditionType');
	// 	if(addCondition!=undefined && selectCondition!=undefined && selectConditionType!=undefined){					
 // 			if(storeCond.getCount()==0){
 // 				addCondition.setDisabled(true);
 // 				addCondition.setTooltip('You must choose a condition to add it');
						
 // 				selectCondition.clearValue();
 // 				selectCondition.setDisabled(true);
 // 				selectConditionType.setDisabled(true);
 // 			}
 // 			else
 // 			{
 // 				selectCondition.setDisabled(false);
 // 				selectConditionType.setDisabled(false);
 // 			}
	// 	}	

	// 	selectCondition.setValue(storeCond.first().getCondName());   
	
	// }	
	/*init : function() {
		this.getStore('S_MappingInfo')
			.addListener('datachanged',
				function(store){
					var selectMapping = Ext.getCmp('selectMapping');
					// If the MappingInfo store is empty we disable the button else enable
					if(selectMapping!=undefined)
					{
						if(store.getCount()==0)
						{
							selectMapping.setDisabled(true);
						}
						else
						{	
							selectMapping.setDisabled(false);
						}
					}
					

				    selectMapping = Ext.getCmp('selectMappingVisu');
					// If the MappingInfo store is empty we disable the button else enable
					if(selectMapping!=undefined)
					{
						if(store.getCount()==0)
						{
							selectMapping.setDisabled(true);
						}
						else
						{	
							selectMapping.setDisabled(false);
						}
					}
				}
					
		, this);
	},*/
});