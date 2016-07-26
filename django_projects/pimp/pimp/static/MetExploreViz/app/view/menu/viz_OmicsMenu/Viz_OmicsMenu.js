/**
 * @author Fabien Jourdan
 * @description Menu to call mapping functions on cytoscape view
 */

Ext.define('metExploreViz.view.menu.viz_OmicsMenu.Viz_OmicsMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizOmicsMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_OmicsMenu.Viz_OmicsMenuController',
            'metExploreViz.view.menu.viz_OmicsMenu.Viz_OmicsMenuModel'
        ],
        
        controller: "menu-vizOmicsMenu-vizOmicsMenu",
        viewModel: {
            type: "menu-vizOmicsMenu-vizOmicsMenu"
        },

        items:  [
             {
                 text: 'Import Mapping',
                 action:'GraphMapping',
                 tooltip:'Display mapping info on Graph',
                 iconCls:'importData'
             }
        ]
});