/**
 * @author MC
 * @description class to control contion selection panel and to draw mapping in the mapping story
 */

Ext.define('metExploreViz.view.form.selectConditionForm.SelectConditionFormController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.form-selectConditionForm-selectConditionForm',

/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();

		// Action to launch mapping on  the visualization
		
		view.on({
			afterDiscreteMapping : this.addMappingCaptionForm,
			scope:me
		});

		view.on({
			afterContinuousMapping : this.addMappingCaptionForm,
			scope:me
		});

		view.on({
			closeMapping : function(newMapping){
				me.closeMapping(newMapping);
			},
			scope:me
		});

		view.on({
			resetMapping : function(){
				me.resetMapping();
			},
			scope:me
		});

		view.on({
			removeMapping : function(removedMapping){
				me.removeMapping(removedMapping);
			},
			scope:me
		});

		view.on({
			reset : function(newMapping){
			},
			scope:me
		});

		view.lookupReference('addCondition').on({
			click : function() 
			{	
				var networkVizSession = _metExploreViz.getSessionById("viz");
				var that = this;
				// If the main network is already mapped we inform the user: OK/CANCEL
				if(networkVizSession.isMapped()!='false')	
				{
			        Ext.Msg.show({
			           title:'Are you sure?',
			           msg: 'This action will remove previous mapping. <br />Would you like to do this?',
			           buttons: Ext.Msg.OKCANCEL,
			           fn: function(btn){
							if(btn=="ok")
							{	
								var newMapping ='true';
								me.closeMapping(newMapping);
								that.map();
							}
			           },
			           icon: Ext.Msg.QUESTION
			       });
				}
				else
					this.map();												
			},
			scope : me
		});
	},


	removeMapping:function(mapping){
		var session = _metExploreViz.getSessionById('viz');
		var component = Ext.getCmp("selectConditionForm");

        if(component!= undefined){
           // Remove mapping caption
            var activeMapping = session.getActiveMapping();
	        if(activeMapping == mapping.getName()){
				var storeCond = Ext.getStore('S_Condition');
				var oldMapping = session.isMapped();

				this.removeGraphMapping(oldMapping);
				if(oldMapping!= false && oldMapping!= "false" && oldMapping!= "none"){


					if(session.getMappingDataType()=="Continuous"){
						var colorStore = session.getColorMappingsSet();        
				        var newColor = session.getColorMappingsSetLength()==0;
				        
				        if(!newColor){
				        	colorStore = [];
				        }
				    }
			    

					var container = Ext.getCmp('panel'+session.isMapped());
					
					if(container!=undefined){				
						container.close();
						var colorStore = session.getColorMappingsSet();
						colorStore.forEach(function(color){
							var newId = color.getName().toString().replace(".", "_");
							if(Ext.getCmp("selectConditionForm").down("#mappingCaptionForm"+newId)!=null)
								Ext.getCmp("selectConditionForm").down("#mappingCaptionForm"+newId).close();
						});

						if(Ext.getCmp("selectConditionForm").down("#undefined")!=null)
							Ext.getCmp("selectConditionForm").down("#undefined").close();
					}
				}

				session.setMapped('false');

				var comboCond = Ext.getCmp('selectCondition');
				var storeCond = comboCond.getStore();
		        //take an array to store the object that we will get from the ajax response
				var record = [];
		        storeCond.loadData(record, false);

				var addCondition = Ext.getCmp('addCondition');
				var selectConditionType = Ext.getCmp('selectConditionType');
				
				comboCond.clearValue();
				comboCond.setDisabled(true);
				addCondition.setDisabled(true);
				addCondition.setTooltip('You must choose a condition to add it');
					
				selectConditionType.setDisabled(true);
		 			
	        }
        	metExploreD3.fireEventArg('selectMappingVisu', "removemapping", mapping);
        	_metExploreViz.removeMapping(mapping.getName()); 
	    }

	}
	,
	resetMapping:function(mappingJSON){
		var session = _metExploreViz.getSessionById('viz');
		var component = Ext.getCmp("selectConditionForm");

        if(component!= undefined){
           // Remove mapping caption
			var storeCond = Ext.getStore('S_Condition');
			var oldMapping = session.isMapped();

			this.removeGraphMapping(oldMapping);

			if(session.getMappingDataType()=="Continuous"){
				var colorStore = session.getColorMappingsSet();        
		        var newColor = session.getColorMappingsSetLength()==0;
		        
		        if(!newColor){
		        	colorStore = [];
		        }
		    }
		    

			var container = Ext.getCmp('panel'+session.isMapped());
			
			if(container!=undefined){				
				container.close();
				var colorStore = session.getColorMappingsSet();
				colorStore.forEach(function(color){
					var newId = color.getName().toString().replace(".", "_");
					if(Ext.getCmp("selectConditionForm").down("#mappingCaptionForm"+newId)!=null)
						Ext.getCmp("selectConditionForm").down("#mappingCaptionForm"+newId).close();
				});

				if(Ext.getCmp("selectConditionForm").down("#undefined")!=null)
					Ext.getCmp("selectConditionForm").down("#undefined").close();
			}
			
			session.setMapped('false');

			var comboCond = Ext.getCmp('selectCondition');
			var storeCond = comboCond.getStore();
	        //take an array to store the object that we will get from the ajax response
			var record = [];
	        storeCond.loadData(record, false);

			var addCondition = Ext.getCmp('addCondition');
			var selectConditionType = Ext.getCmp('selectConditionType');
			
			comboCond.clearValue();
			comboCond.setDisabled(true);
			addCondition.setDisabled(true);
			addCondition.setTooltip('You must choose a condition to add it');
				
			selectConditionType.setDisabled(true);
	 			
        	var comboMapping = Ext.getCmp('selectMappingVisu');
			var store = comboMapping.getStore();
            var records = [];

			store.loadData(records, false);
            comboMapping.clearValue();
            comboMapping.setDisabled(true);
        }

	}
	,
	/*******************************************
	* Removing of mapping
	* @param {} newMapping : boolean to know if a new mapping is launched
	*/
	closeMapping : function(newMapping){

		var session = _metExploreViz.getSessionById('viz');
		if(session.isMapped()!="false")	
		{	

			var addCondition = Ext.getCmp('addCondition'); 
			if(addCondition!=undefined){	
				addCondition.setDisabled(false);
				addCondition.setTooltip('The condition will be add to the network');						
			}
			// Remove mapping caption
			var storeCond = Ext.getStore('S_Condition');
			var oldMapping = session.isMapped();

			if(newMapping!=undefined)
				this.removeGraphMapping(oldMapping);

			if(session.getMappingDataType()=="Continuous"){
				var colorStore = session.getColorMappingsSet();        
		        var newColor = session.getColorMappingsSetLength()==0;
		        
		        if(!newColor){
		        	colorStore = [];
		        }
		    }
		    

			var container = Ext.getCmp('panel'+session.isMapped());
			
			if(container!=undefined){				
				container.close();
				var colorStore = session.getColorMappingsSet();
				colorStore.forEach(function(color){
					var newId = color.getName().toString().replace(".", "_");
					if(Ext.getCmp("selectConditionForm").down("#mappingCaptionForm"+newId)!=null)
						Ext.getCmp("selectConditionForm").down("#mappingCaptionForm"+newId).close();
				});

				if(Ext.getCmp("selectConditionForm").down("#undefined")!=null)
					Ext.getCmp("selectConditionForm").down("#undefined").close();
			}
			
			session.setMapped('false');
		}
	},

	// RemoveMapping in function of data type
	removeGraphMapping : function(conditionName) {

		metExploreD3.GraphMapping.removeGraphMappingData(conditionName);

		var storeCond = Ext.getCmp('selectCondition').getStore();
		var addCondition = Ext.getCmp('addCondition'); 
		var selectConditionType = Ext.getCmp('selectConditionType'); 
		if(addCondition!=undefined && storeCond.getCount()!=0 && selectConditionType!=undefined && selectConditionType.getValue()!=null){	
			addCondition.setDisabled(false);
			addCondition.setTooltip('The condition will be add to the network');						
		}

	},

	/*******************************************
	* Initialisation of mapping
	*/
	map : function(){
		var selectCondition = Ext.getCmp('selectCondition');
		var selectMapping = Ext.getCmp('selectMappingVisu');
		var selectedCondition = selectCondition.getValue();
		var selectedMapping = selectMapping.getValue();
		var dataType = Ext.getCmp("selectConditionType").getValue();
		
		this.graphMapping(dataType, selectedCondition, selectedMapping);
	},

	// Do Mapping in function of data type
	graphMapping : function(dataType, conditionName, mappingName) {

		var session = _metExploreViz.getSessionById('viz');
		session.setActiveMapping(mappingName);
		if(dataType=="Continuous")
			metExploreD3.GraphMapping.graphMappingContinuousData(mappingName, conditionName);

		// if(dataType=="Binary")
		// 	metExploreD3.GraphMapping.graphMappingBinary(mappingName, conditionName);
			
		if(dataType=="Discrete")
			metExploreD3.GraphMapping.graphMappingDiscreteData(mappingName, conditionName);


		session.setMappingDataType(dataType);
	},

	/*******************************************
	* Add the panel caption corresponding to mapping
	* @param {} type : data type of mapping values
	*/
	addMappingCaptionForm : function(type) {
		// We add form corresponding to the mapping data type
		var selectConditionForm = Ext.getCmp('selectConditionForm');
	    var selectCondition = Ext.getCmp('selectCondition');
		var selectedCondition = selectCondition.getValue();

		var selectMapping = Ext.getCmp('selectMappingVisu');
		var selectedMapping = selectMapping.getValue();

		var networkVizSession = _metExploreViz.getSessionById("viz");
		networkVizSession.setMapped(selectedCondition);
		
		if(selectConditionForm !=undefined)
		{
			if(Ext.getCmp('panel'+selectedCondition)==undefined)
			{
			
				var idColors = [];
				var listMappingCaptionForm = [];	
				var colorStore = networkVizSession.getColorMappingsSet();
				var that = this;

				// // Call of jscolor library
				var e = document.createElement('script'); 
				e.setAttribute('src', document.location.href.split("index.html")[0] + 'resources/lib/jscolor/jscolor.js'); 
				document.body.appendChild(e); 	

				// For each value we add corresponding color caption
				colorStore.forEach(function(color){
			    	var colorName = color.getName();
			    	var value = colorName;
			    	var newId = colorName.toString().replace(".", "_");
			    	var newMappingCaptionForm = Ext.create('metExploreViz.view.form.MappingCaptionForm', {
					
				    	itemId: 'mappingCaptionForm'+newId,
				    	//id: 'mappingCaptionForm'+newId,

			            margin: '0 0 0 0',
			            padding: '0 0 0 0',
			            border:false,
					    items: 
					    [
						    {   
						        
						        itemId:'chooseColorReaction'+newId,
						        //id:'chooseColorReaction'+newId,
						        xtype:'panel',
						        border:false,
						        layout:{
						           type:'hbox',
						           align:'stretch'
						        },
						        items:[
						        	{
							            xtype: 'label',
							            forId: 'color',
							            text: value+' :',
							            margin: '0 0 0 10',
							            flex:1,
							            border:false      
						        	},{
						        		border:false,
							            xtype: 'hiddenfield',
							            itemId: 'hidden' + newId,
							            //id: 'hidden' + newId,
							           	value: color.getValue(),
										listeners: {
											change: function(newValue, oldValue){
												this.lastValue = newValue;

										    }
										}    
						        	},
						        	{
							            border:false,
							            margin: '0 10 0 0',
							            width: "40%",
							            // Object to change color var field= Ext.ComponentQuery.query('#theField')[0];
							            html: '<input size="5" onchange="Ext.getCmp(\'selectConditionForm\').down(\'#hidden'+newId+'\').fireEvent(\'change\', \'#\'+this.color.valueElement.value, \''+color.getValue()+'\');" value=\''+color.getValue()+';\'" class="color {pickerFaceColor:\'#5FA2DD\',pickerPosition:\'right\',pickerFace:5}">'
							            // html: '<input size="5" onchange="console.log(\'Color :\',this.color.valueElement.value); Ext.getCmp(\'hidden'+newId+'\').value=\'#\'+this.color.valueElement.value; console.log(\'hidden :\',document.getElementById(\''+'hidden'+newId+'\').value); document.getElementById(\''+'hidden'+newId+'\').value = \'#\'+this.color.valueElement.value;" value=\''+color.getValue()+';\'" class="color {pickerFaceColor:\'#99BCE8\',pickerPosition:\'right\',pickerFace:5}">',
							            // html: '<input size="5" onchange="document.getElementById(\''+'hidden'+newId+'\').value = \'#\'+this.color;" value=\''+color.getValue()+';\'" class="color {pickerFaceColor:\'#99BCE8\',pickerPosition:\'right\',pickerFace:5}">',
							        }
						        ]
						    }
					    ]
					});
					
					listMappingCaptionForm.push(newMappingCaptionForm);
					idColors.push(newId);
			    }
				);
			
				var newConditionPanel = Ext.create('Ext.panel.Panel', {
			    	id: 'panel'+selectedCondition,
			    	border:false,
			    	width: '100%',
				    bodyBorder: false,
				    xtype:'panel',
			        layout:{
			           type:'hbox',
			           align:'stretch'
			        },
				    items: [{
				        xtype: 'label',
				        forId: 'condName',
				        margin:'8 5 5 10',
						flex:1,
				        text: selectedCondition
				    }]
				});

				// Create button to remove mapping
				var delButton = Ext.create('Ext.Button', {
				    iconCls:'del',
		            tooltip:'You must choose a condition to add it',
		            //formBind: true,
		            margin:'5 5 5 0',
		            id: 'delCondition'+selectedCondition,
		            action: 'delCondition'+selectedCondition,     
				    handler: function() {
				        var container = this.findParentBy(function (component)
						{
						  return component instanceof Ext.panel.Panel;
						});  
						var addCondition = Ext.getCmp('addCondition'); 

						if(addCondition!=undefined){	
							addCondition.setDisabled(false);
							addCondition.setTooltip('The condition will be add to the network');						
						}

						that.closeMapping(selectedMapping);
	
				    }
				});
			    newConditionPanel.add(delButton);
			    
			    var dataType = Ext.getCmp("selectConditionType").getValue();
				var mapp = selectedMapping;

				// Add button to change colors
				var refreshColorButton = Ext.create('Ext.Button', {
				    iconCls:'refresh',
		            margin:'5 5 5 0',
		            id: 'refreshColor'+selectedCondition,
		            action: 'refreshColor'+selectedCondition,     
				    handler: function() {
				        var mapping = mapp;
				    	var colorStore = networkVizSession.getColorMappingsSet();
						if(type=="discrete"){
							colorStore.forEach(function(color){
								var newId = color.getName().toString().replace(".", "_");
								if(Ext.getCmp("selectConditionForm").down("#hidden"+newId)!=null){
									if(color.getValue()!=Ext.getCmp("selectConditionForm").down("#hidden"+newId).lastValue){
										// PERF: Must be changed to set only the color
										metExploreD3.GraphMapping.setDiscreteMappingColor(Ext.getCmp("selectConditionForm").down("#hidden"+newId).lastValue, color.getName(), selectedCondition, mapp);
						        	}

						        }
							});
						}
						else
						{
							colorStore.forEach(function(color){
								var newId = color.getName().toString().replace(".", "_");
								if(Ext.getCmp("selectConditionForm").down("#hidden"+newId)!=null){
									if(color.getValue()!=Ext.getCmp("selectConditionForm").down("#hidden"+newId).lastValue){
										// PERF: Must be changed to set only the color
										metExploreD3.GraphMapping.setContinuousMappingColor(Ext.getCmp("selectConditionForm").down("#hidden"+newId).lastValue, color.getName(), selectedCondition, mapp);
						        	}
						        	
						        }
							});
							
							if(parseFloat(networkVizSession.getColorMappingsSet()[0].getName())<parseFloat(networkVizSession.getColorMappingsSet()[1].getName())){
								maxValue = parseFloat(networkVizSession.getColorMappingsSet()[1].getName());
								minValue = parseFloat(networkVizSession.getColorMappingsSet()[0].getName());
							}
							else
							{
								maxValue = parseFloat(networkVizSession.getColorMappingsSet()[0].getName());
								minValue = parseFloat(networkVizSession.getColorMappingsSet()[1].getName());
							}
							
							
							metExploreD3.GraphMapping.graphMappingContinuousData(mapp, selectedCondition, networkVizSession.getColorMappingById(minValue).getValue(), networkVizSession.getColorMappingById(maxValue).getValue());
						}
				    }
				});
			    newConditionPanel.add(refreshColorButton);


				// Add mapping caption to selectConditionForm panel
			    var selectConditionForm = Ext.getCmp('selectConditionForm');
			    if(selectConditionForm!=undefined)
				{	
					selectConditionForm.add(newConditionPanel);
					listMappingCaptionForm.forEach(function(aMappingCaptionForm){

						selectConditionForm.add(aMappingCaptionForm);
					});
				}
			}
		}
	}
});