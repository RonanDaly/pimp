/**
 * @author Maxime Chazalviel
 * @description Menu export network viz
 */

Ext.define('metExploreViz.view.menu.viz_ConvexHullMenu.Viz_ConvexHullMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizConvexHullMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_ConvexHullMenu.Viz_ConvexHullMenuController',
            'metExploreViz.view.menu.viz_ConvexHullMenu.Viz_ConvexHullMenuModel'
        ],

        controller: "menu-vizConvexHullMenu-vizConvexHullMenu",
        viewModel: {
            type: "menu-vizConvexHullMenu-vizConvexHullMenu"
        },

           // <-- submenu by nested config object
        items: [
            {
                text: 'Compartments',
                checked: false,
                reference:'highlightCompartments'
            }, {
                text: 'Pathways',
                checked: false,
                reference:'highlightPathways'
            }
        ]
});

