/**
 * @author Fabien Jourdan
 * @description Menu to call graph algorithms on Cytoscape network
 */

Ext.define('metExploreViz.view.menu.viz_MiningMenu.Viz_MiningMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizMiningMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_MiningMenu.Viz_MiningMenuController',
            'metExploreViz.view.menu.viz_MiningMenu.Viz_MiningMenuModel'
        ],

        controller: "menu-vizMiningMenu-vizMiningMenu",
        viewModel: {
            type: "menu-vizMiningMenu-vizMiningMenu"
        },

        items:  [
             {
                 text: 'Highlight Subnetwork',
                 reference :'highlightSubnetwork',
                 tooltip:'Highlight sub-network based on node selection or mapped nodes',
                 iconCls:'highlightSubnetwork'
             },
              {
                 text: 'Extract Subnetwork',
                 reference:'keepOnlySubnetwork',
                 tooltip:'Extract sub-network based on node selection',
                 iconCls:'subnetwork'
              }
            //  {
            //     text: 'Extract Subnetwork',action:'subnetwork',tooltip:'Extract sub-network based on node selection',iconCls:'subnetwork',
            //  },
            //  '-',
            // {
            //     text: 'Make Acyclic',action:'makeAcyclic',tooltip:'Delete edges to get an acyclic network',iconCls:'makeAcyclic',
            //  },

        ]
});