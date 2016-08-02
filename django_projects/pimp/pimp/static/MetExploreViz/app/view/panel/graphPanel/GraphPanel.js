Ext.define("metExploreViz.view.panel.graphPanel.GraphPanel",{
    extend: "Ext.panel.Panel",
    alias: 'widget.graphPanel',

    requires: [
        "metExploreViz.view.panel.graphPanel.GraphPanelController",
        "metExploreViz.view.panel.graphPanel.GraphPanelModel",
        "metExploreViz.view.panel.comparePanel.ComparePanel",

        'metExploreViz.view.menu.viz_MiningMenu.Viz_MiningMenu',
        'metExploreViz.view.menu.viz_SaveMenu.Viz_SaveMenu',
        'metExploreViz.view.menu.viz_ExportMenu.Viz_ExportMenu',
        'metExploreViz.view.menu.viz_ImportMenu.Viz_ImportMenu',
        'metExploreViz.view.menu.viz_DrawingMenu.Viz_DrawingMenu',
        'metExploreViz.view.menu.viz_ConvexHullMenu.Viz_ConvexHullMenu',
        'metExploreViz.view.menu.viz_CaptionMenu.Viz_CaptionMenu',
        'metExploreViz.view.menu.viz_ColorMenu.Viz_ColorMenu',
        'metExploreViz.view.menu.viz_LoadMenu.Viz_LoadMenu',
        'metExploreViz.view.button.buttonImportMapping.ButtonImportMapping',
        'metExploreViz.view.button.buttonImportSideCompounds.ButtonImportSideCompounds',
        'metExploreViz.view.button.buttonImportToNetwork.ButtonImportToNetwork',
        'metExploreViz.view.panel.viz.Viz'
    ],
    /*requires: [
       'lib.javascript.metExploreViz.view.graphcomponent.V_Viz'
   ],*/

    controller: "panel-graphpanel-graphpanel",
    viewModel: {
        type: "panel-graphpanel-graphpanel"
    },

   height:'100%',
   width:'100%', 
   margins:'0 0 0 0', 
   split:true, 
   layout:{
       type:'vbox',
       align:'stretch'
   },
   items: 
   [
           
           {
               tbar:{
                   id:'tbarGraph',
                   items: [
                          {
                                text: 'Load network', 
                                scale: 'large',
                                menu:{xtype: 'vizLoadMenu'},
                                tooltip:'You must create a network to use this menu',
                                id:'vizLoadMenuID',
                                reference:'vizLoadMenuID',
                                padding:'5px 5px 5px 5px',
                                iconCls: 'importToRsx',
                                cls:"loadButton",
                                iconAlign: 'left'
                          },
                          // {
                          //      xtype:'buttonImportToNetwork'/*,text: 'Refresh/Build network'*/,
                          //      id:'buttonRefresh'                               
                          //  },""
                           //{text: 'Drawing', menu:{xtype: 'cytoscapeDrawingMenu'},id:'cytoscapeDrawingMenuID',hidden:false},
                           //{text: 'Edit', menu:{xtype: 'cytoscapeEditMenu'},id:'cytoscapeEditMenuID',hidden:false},
                           {
                                text: 'Mining', 
                                scale: 'large',
                                menu:{xtype: 'vizMiningMenu'},
                                tooltip:'You must create a network to use this menu',
                                id:'vizMiningMenuID',
                                reference:'vizMiningMenuID',
                                disabled:true,
                                hidden:false,
                                padding:'0 0 0 0'
                            },
                           {
                                text: 'Drawing', 
                                scale: 'large',
                                menu:{id:'vizIdDrawing',xtype: 'vizDrawingMenu'},
                                tooltip:'You must create a network to use this menu',
                                id:'vizDrawingMenuID',
                                reference:'vizDrawingMenuID',
                                disabled:true,
                                hidden:false,
                                padding:'0 0 0 0'
                            },
                           {
                                text: 'Export', 
                                scale: 'large',
                                menu:{xtype: 'vizExportMenu'},
                                tooltip:'You must create a network to use this menu',
                                id:'vizExportMenuID',
                                reference:'vizExportMenuID',
                                disabled:true,
                                hidden:false,
                                padding:'0 0 0 0'
                          },
                          {
                                text: 'Import', 
                                scale: 'large',
                                menu:{xtype: 'vizImportMenu'},
                                tooltip:'You must create a network to use this menu',
                                id:'vizImportMenuID',
                                reference:'vizImportMenuID',
                                disabled:true,
                                hidden:false,
                                padding:'0 0 0 0'
                          },
                          {
                                text: 'Save', 
                                scale: 'large',
                                menu:{xtype: 'vizSaveMenu'},
                                tooltip:'You must create a network to use this menu',
                                id:'vizSaveMenuID',
                                reference:'vizSaveMenuID',
                                disabled:true,
                                hidden:false,
                                padding:'0 0 0 0'
                          },
                           '-',
                           {
                                xtype:'button'/*,text: 'Copy network'*/,
                                overflowText: 'Copy network',
                                scale: 'large',
                                id:'buttonCopyNetwork',
                                reference:'buttonCopyNetwork',
                                tooltip:'You must create a network to copy the network',
                                iconCls:'copyNetwork', 
                                disabled:true,                               
                                border: false,
                                padding:'0 0 0 0',
                                listeners: {
                                    click : function() {
                                      var component = Ext.getCmp('comparePanel');
                                          if(component!= undefined){
                                              component.fireEvent('copyNetwork');
                                          }
                                    }
                                }
                            },
                            '-',
                            {
                                border:false,
                                disabled:true,                               
                                xtype:'panel',
                                reference:'searchNode',
                                layout:{
                                   type:'hbox',
                                   align:'stretch'
                                },
                                items:[
                                  {
                                    xtype: 'textfield',
                                    tooltip:'Find node by name, id, compartment...',
                                    name: 'searchNodeTextField',
                                    reference:'searchNodeTextField',
                                    referenceHolder:true,
                                    fieldLabel: 'Search Node(s)',
                                    scale: 'large',
                                    listeners: {
                                        change: function(that, newValue, oldValue) {
                                            var items = this.container.component.items.items;
                                            var theButton = undefined;
                                            for (var i = 0; i < items.length; i++) {
                                              if(items[i].reference=='searchNodeButton')
                                                theButton=items[i];
                                            };
                                            
                                            if(newValue.length>0 && oldValue.length==0)
                                              theButton.setDisabled(false);
                                            else
                                                if (oldValue.length>0 && newValue.length==0) 
                                                    theButton.setDisabled(true);
                                        },
                                        specialkey : function(field, event){
                                            var items = this.container.component.items.items;
                                            var theButton = undefined;
                                            for (var i = 0; i < items.length; i++) {
                                              if(items[i].reference=='searchNodeButton')
                                                theButton=items[i];
                                            };
                                            if(event.getKey() == event.ENTER){
                                                var component = theButton;
                                              console.log(component);
                                                    if(component!= undefined){
                                                        component.fireEvent("click");
                                                    }
                                            } 
                                        }
                                    }
                                  },
                                  {
                                      xtype:'button',
                                      // scale: 'large',
                                      reference:'searchNodeButton',
                                      iconCls:'search',
                                      scale: 'large',
                                      border: false,
                                      disabled:true,
                                      tooltip:'Find node by name, id, compartment...',
                                      padding:'0 0 0 0'
                                  }
                                ]
    
                            }
                          ]}

           },
           {
              layout:{
                 type:'border',
                 align:'stretch'
             },
              xtype : 'panel',
              width:'100%', 
              margins:'0 0 0 0',
              closable: false,
              region:'south', 
              flex:1,     
              items: [{   
                  title: 'Network Manager',
                  id:'comparisonSidePanel',
                  xtype : 'comparisonSidePanel'  
                },
                {
                    id : 'viz',
                    xtype : 'viz'
                }
              ]
           }
           ,{   
              title: 'Comparative Network',
              closable: false,
              id:'comparePanel',
              xtype : 'comparePanel'
           }
    ]
});
