/**
 * @author Maxime Chazalviel
 * @description Menu export network viz
 */

Ext.define('metExploreViz.view.menu.viz_LayoutMenu.Viz_LayoutMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizLayoutMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_LayoutMenu.Viz_LayoutMenuController',
            'metExploreViz.view.menu.viz_LayoutMenu.Viz_LayoutMenuModel'
        ],

        controller: "menu-vizLayoutMenu-vizLayoutMenu",
        viewModel: {
            type: "menu-vizLayoutMenu-vizLayoutMenu"
        },

           // <-- submenu by nested config object
        items: [
            {
                text: 'Hierarchical Tree (R-T Extended)',
                reference:'hierarchicalTreeLayout',
                iconCls:'drawhierarchicallayout'
            }, {
                text: 'Sugiyama (OGDF)',
                reference:'sugiyamaLayout',
                iconCls:'drawhierarchicallayout'
            }
        ]
});

