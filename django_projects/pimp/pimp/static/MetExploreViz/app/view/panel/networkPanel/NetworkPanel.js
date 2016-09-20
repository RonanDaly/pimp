/**
 * @author MC
 * @description 
 */         
Ext.define('metExploreViz.view.panel.networkPanel.NetworkPanel', {
    extend: 'Ext.panel.Panel', 
    alias: 'widget.networkPanel',
    layout: 'border',
    requires: [
        'metExploreViz.view.panel.networkPanel.NetworkPanelController',
        "metExploreViz.view.panel.graphPanel.GraphPanel",
        "metExploreViz.view.panel.comparisonSidePanel.ComparisonSidePanel"
    ],
    controller: "panel-networkPanel-networkPanel",
    id:"NetworkPanel",
    layout: 'border',
        
    height:'100%',
    width:'100%', 
    border: true, 
    items: [{   
        closable: false,
        id:'graphPanel',
        xtype : 'graphPanel',
        region:'center'
      },
        {
            hidden:true,
            id:'buttonLoadNetworkFromJSON',   
            xtype:'buttonImportToNetwork'/*,text: 'Refresh/Build network'*/
        }
    ]
});
