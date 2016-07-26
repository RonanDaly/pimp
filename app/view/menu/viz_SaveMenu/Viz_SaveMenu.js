/**
 * @author Fabien Jourdan
 * @description Menu export network viz
 */

Ext.define('metExploreViz.view.menu.viz_SaveMenu.Viz_SaveMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizSaveMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_SaveMenu.Viz_SaveMenuController',
            'metExploreViz.view.menu.viz_SaveMenu.Viz_SaveMenuModel'
        ],

        controller: "menu-vizSaveMenu-vizSaveMenu",
        viewModel: {
            type: "menu-vizSaveMenu-vizSaveMenu"
        },
        
        items:  [
             {
                 text: 'Save Viz as json',
                 reference:'exportJSON',
                 tooltip:'Save network viz as a json file',
                 iconCls:'saveNetwork'
                },
                {
                 text: 'Save Viz as dot',
                 reference:'exportDOT',
                 tooltip:'Save network viz as a dot file',
                 iconCls:'exportDot'
                },
                {
                 text: 'Save Viz as gml',
                 reference:'exportGML',
                 tooltip:'Save network viz as a gml file',
                 iconCls:'exportGml'
                },
                {
                 text: 'Save Viz as XGMML',
                 hidden:true,
                 reference:'exportXGMML',
                 tooltip:'Save network viz as a XGMML file with Cytoscape\'s graphical attibutes', 
                 iconCls:'cytoscapeWebStart'
             }
        ]
});

