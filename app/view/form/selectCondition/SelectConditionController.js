/**
 * @author MC
 * @description class to control contion selection panel and to draw mapping in the mapping story
 */

Ext.define('metExploreViz.view.form.selectCondition.SelectConditionController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.form-selectCondition-selectCondition',

	/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();

		/*view.on({
			newMapping : metExploreD3.GraphCaption.drawCaption,
			scope:me
		});*/
	}
// Listener to manage mapping selection
	// 		'selectConditionForm selectMapping': 
	// 		{
	
	// 			collapse : function(that, newMapping, old){
	// 				metExploreD3.GraphMapping.mapNodes();
	// 			}
	// 		},
	// 		// Listener to manage the condition of mapping selection
	// 		'selectConditionForm selectCondition': 
	// 		{
	// 			change : function() 
	// 			{	
					
	// 				var storeCond = Ext.getStore('S_Condition');
	// 				var addCondition = Ext.getCmp('addCondition'); 
	// 				var selectConditionType = Ext.getCmp('selectConditionType'); 
	// 				if(addCondition!=undefined && storeCond.getCount()!=0 && selectConditionType.getValue()!=null){	
	// 					addCondition.setDisabled(false);
	// 					addCondition.setTooltip('The condition will be add to the network');						
	// 				}
	// 			// We add form corresponding to the mapping data type
	// 				// this.refresh();
	// 			}
	// 		},
	// 		// Listener to manage type of values selection
	// 		'selectConditionForm selectConditionType': 
	// 		{
	// 			change : function() 
	// 			{	
	// 				var addCondition = Ext.getCmp('addCondition');
	// 				if(addCondition!=undefined){	
	// 					addCondition.setDisabled(false);
	// 					addCondition.setTooltip('The condition will be add to the network');						
	// 				}
	// 			// We add form corresponding to the mapping data type
	// 				// this.refresh();
	// 			}
	// 		},
	// 		// Listener to manage mapping when a refresh is launched
	// 		'graphPanel button[action=refresh]' : {
	// 			click : function() {
	// 				var newMapping = undefined;
	// 				this.closeMapping(newMapping);
	// 			}
	// 		},
	// 	});
	// },

	// /*******************************************
	// * Initialisation of mapping
	// */
	// map : function(){
	// 	var selectCondition = Ext.getCmp('selectCondition');
	// 	var selectedCondition = selectCondition.getValue();
	// 	var dataType = Ext.getCmp("selectConditionType").getValue();
	// 	var storeCond = Ext.getStore('S_Condition');
	// 	var condition = storeCond.getStoreByCondName(selectedCondition);
	// 	var condInMetabolite = condition.getCondInMetabolite();
		
	// 	this.graphMapping(dataType, condInMetabolite);
	// },
	
	

	// /*******************************************
	// * Remove the panel to do mapping
	// */
	// refreshMappingPanel : function() {
	// 	var mappingInfoStore = Ext.getStore('S_MappingInfo');

	// 	if (mappingInfoStore!=undefined) {

	//       	mappingInfoStore.each(function(mapping)
	// 	  	{
	// 			var conditions = mapping.get('condName');
	// 			// var container = this.findParentBy(function (component)
	// 			// {
	// 			//   return component instanceof Ext.panel.Panel;
	// 			// });  
	//       		for(var indCond=0;indCond<conditions.length;indCond++){
	// 				var condName = mapping.get('id')+"_"+conditions[indCond]+"Panel";
	// 				var container = Ext.getCmp(condName);
	// 				if(container!=null)
	// 					container.close();
	// 			}	
	// 	  	})	
	// 	}
	// },

	// /*******************************************
	// * Add the panel caption corresponding to mapping
	// * @param {} type : data type of mapping values
	// */
	// addMappingCaptionForm : function(type) {
		
	// 	// We add form corresponding to the mapping data type
	// 	var selectConditionForm = Ext.getCmp('selectConditionForm');
	//     var selectCondition = Ext.getCmp('selectCondition');
	// 	var selectedCondition = selectCondition.getValue();
	// 	var networkVizSessionStore = Ext.getStore('S_NetworkVizSession');
	// 	networkVizSession = networkVizSessionStore.getById("viz");
	// 	networkVizSession.setMapped(selectedCondition);
		
	// 	if(selectConditionForm !=undefined)
	// 	{
	// 		if(selectConditionForm.getChildByElement(selectedCondition+"Panel")==null)
	// 		{
			
	// 			var idColors = [];
	// 			var listMappingCaptionForm = [];	
	// 			var colorStore = Ext.getStore('S_ColorMapping');
	// 			var that = this;

	// 			// For each value we add corresponding color caption
	// 			colorStore.each(function(color){
	// 		    	var newId = color.getName();
	// 		    	var newMappingCaptionForm = Ext.create('MetExplore.view.form.V_MappingCaptionForm', {
	// 			    	id: 'mappingCaptionForm'+newId,

	// 				    items: 
	// 				    [{   
	// 				        border:false,
	// 				        id:'chooseColorReaction'+newId,
	// 				        xtype:'panel',
	// 				        layout:{
	// 				           type:'hbox',
	// 				           align:'stretch'
	// 				        },
	// 				        items:[{
	// 				            xtype: 'label',
	// 				            forId: 'color',
	// 				            text: color.getName()+' :',
	// 				            margins: '5 5 5 10'        
	// 				        },{
	// 				            xtype: 'hiddenfield',
	// 				            id: 'hidden' + newId,
	// 				           	value: color.getValue(),
	// 							listeners: {
	// 								change: function(newValue, oldValue){
	// 									Ext.getCmp('hidden'+newId).value = newValue;
	// 							    }
	// 							}    
	// 				        },
	// 				        {
	// 				            border:0,
	// 				            margins: '2 5 5 0',

	// 				            // Object to change color
	// 				            html: '<input size="5" onchange="Ext.getCmp(\'hidden'+newId+'\').fireEvent(\'change\', \'#\'+this.color.valueElement.value, \''+color.getValue()+'\');" value=\''+color.getValue()+';\'" class="color {pickerFaceColor:\'#99BCE8\',pickerPosition:\'right\',pickerFace:5}">',
	// 				            // html: '<input size="5" onchange="console.log(\'Color :\',this.color.valueElement.value); Ext.getCmp(\'hidden'+newId+'\').value=\'#\'+this.color.valueElement.value; console.log(\'hidden :\',document.getElementById(\''+'hidden'+newId+'\').value); document.getElementById(\''+'hidden'+newId+'\').value = \'#\'+this.color.valueElement.value;" value=\''+color.getValue()+';\'" class="color {pickerFaceColor:\'#99BCE8\',pickerPosition:\'right\',pickerFace:5}">',
	// 				            // html: '<input size="5" onchange="document.getElementById(\''+'hidden'+newId+'\').value = \'#\'+this.color;" value=\''+color.getValue()+';\'" class="color {pickerFaceColor:\'#99BCE8\',pickerPosition:\'right\',pickerFace:5}">',
	// 				        }
	// 				        ]
	// 				    }]
	// 				});

	// 				listMappingCaptionForm.push(newMappingCaptionForm);
	// 				idColors.push(newId);
	// 		    }
	// 			);

	// 			// Create button to remove mapping
	// 			var delButton = Ext.create('Ext.Button', {
	// 			    iconCls:'del',
	// 	            tooltip:'You must choose a condition to add it',
	// 	            //formBind: true,
	// 	            width: 22,
	// 	            margin:'5 5 5 0',
	// 	            id: selectedCondition+'delCondition',
	// 	            action: selectedCondition+'delCondition',     
	// 			    handler: function() {
	// 			        var container = this.findParentBy(function (component)
	// 					{
	// 					  return component instanceof Ext.panel.Panel;
	// 					});  
	// 					var addCondition = Ext.getCmp('addCondition'); 

	// 					if(addCondition!=undefined){	
	// 						addCondition.setDisabled(false);
	// 						addCondition.setTooltip('The condition will be add to the network');						
	// 					}

	// 					var storeCond = Ext.getStore('S_Condition');
	// 					var cmp = container.id.substring(0, container.id.length-5);
	// 					var condition = storeCond.getStoreByCondName(cmp);
	// 					var condInMetabolite = condition.getCondInMetabolite();
	// 					that.removeGraphMapping(condInMetabolite);

	// 					container.close();
	// 					idColors.forEach(function(id){
	// 						Ext.getCmp('mappingCaptionForm'+id).close();
	// 					});
	// 					var networkVizSessionStore = Ext.getStore('S_NetworkVizSession');
	// 					networkVizSession = networkVizSessionStore.getById("viz");
	// 					networkVizSession.setMapped('false');
		
	// 			    }
	// 			});
		        
	// 		    var newConditionPanel = Ext.create('Ext.panel.Panel', {
	// 		    	id: selectedCondition+'Panel',
	// 		    	border:false,
	// 		    	width: '100%',
	// 			    bodyBorder: false,
	// 			    xtype:'panel',
	// 		        autoScroll: true,
	// 		        layout:{
	// 		           type:'hbox',
	// 		           align:'stretch'
	// 		        },
	// 			    items: [{
	// 			        xtype: 'label',
	// 			        forId: 'condName',
	// 			        margin:'8 5 5 10',
	// 					flex:1,
	// 			        text: selectedCondition
	// 			    }]
	// 			});
	// 		    newConditionPanel.add(delButton);
			    
	// 		    // Call of jscolor library
	// 			var e = document.createElement('script'); 
	// 			e.setAttribute('src', 'lib/javascript/jscolor/jscolor.js'); 
	// 			document.body.appendChild(e); 	

	// 			// Add mapping caption to selectConditionForm panel
	// 		    var selectConditionForm = Ext.getCmp('selectConditionForm');
	// 		    if(selectConditionForm!=undefined)
	// 			{	
	// 				selectConditionForm.add(newConditionPanel);
	// 				listMappingCaptionForm.forEach(function(aMappingCaptionForm){
	// 					selectConditionForm.add(aMappingCaptionForm);
	// 				});
	// 			}
	// 		}

	// 		var dataType = Ext.getCmp("selectConditionType").getValue();
	
	// 		// Add button to change colors
	// 		var refreshColorButton = Ext.create('Ext.Button', {
	// 		    iconCls:'refresh',
	//             width: 22,
	//             margin:'5 5 5 0',
	//             id: selectedCondition+'refreshColor',
	//             action: selectedCondition+'refreshColor',     
	// 		    handler: function() {
	// 		    	var colorStore = Ext.getStore('S_ColorMapping');
	// 				colorStore.each(function(color){
	// 					var newId = color.getName();
	// 					if(color.getValue()!=Ext.getCmp('hidden'+newId).value){
	// 		        		var storeCond = Ext.getStore('S_Condition');
	// 						var condition = storeCond.getStoreByCondName(selectedCondition);
	// 						var condInMetabolite = condition.getCondInMetabolite();
							
	// 						// PERF: Must be changed to set only the color
	// 		        		metExploreD3.GraphMapping.setDiscreteMappingColor(Ext.getCmp('hidden'+newId).value, color.getName(), condInMetabolite);
	// 		        	}
	// 				});
	// 		    }
	// 		});
	// 	    newConditionPanel.add(refreshColorButton);
	// 	}
	// },

	// // Do Mapping in function of data type
	// graphMapping : function(dataType, conditionName) {

	// 	var networkVizSessionStore = Ext.getStore('S_NetworkVizSession');
	// 	var session = networkVizSessionStore.getStoreById('viz');
	// 	if(dataType=="Continuous")
	// 		metExploreD3.GraphMapping.graphMappingContinuous(conditionName);

	// 	if(dataType=="Binary")
	// 		metExploreD3.GraphMapping.graphMappingBinary(conditionName);
			
	// 	if(dataType=="Discrete")
	// 		metExploreD3.GraphMapping.graphMappingDiscrete(conditionName);


	// 	session.setMappingDataType(dataType);
	// 	var storeCond = metExploreD3.getConditionsSet();
	// 	var addCondition = Ext.getCmp('addCondition');
	// 	var selectConditionType = Ext.getCmp('selectConditionType');
	// 	if(addCondition!=undefined && metExploreD3.getConditionsSetLength(storeCond)!=0 && selectConditionType!=undefined && selectConditionType.getValue()!=null){	
	// 		addCondition.setDisabled(false);
	// 		addCondition.setTooltip('The condition will be add to the network');						
	// 	}
	// },

	// // RemoveMapping in function of data type
	// removeGraphMapping : function(conditionName) {

	// 	metExploreD3.GraphMapping.removeGraphMapping(conditionName);
		
	// 	var storeCond = Ext.getStore("S_Condition");
	// 	var addCondition = Ext.getCmp('addCondition'); 
	// 	var selectConditionType = Ext.getCmp('selectConditionType'); 
	// 	if(addCondition!=undefined && storeCond.getCount()!=0 && selectConditionType!=undefined && selectConditionType.getValue()!=null){	
	// 		addCondition.setDisabled(false);
	// 		addCondition.setTooltip('The condition will be add to the network');						
	// 	}
	// },

});