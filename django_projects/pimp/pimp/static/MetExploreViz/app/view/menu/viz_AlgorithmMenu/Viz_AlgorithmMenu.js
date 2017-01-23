/**
 * @author Maxime Chazalviel
 * @description Menu export network viz
 */

Ext.define('metExploreViz.view.menu.viz_AlgorithmMenu.Viz_AlgorithmMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizAlgorithmMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_AlgorithmMenu.Viz_AlgorithmMenuController',
            'metExploreViz.view.menu.viz_AlgorithmMenu.Viz_AlgorithmMenuModel'
        ],

        controller: "menu-vizAlgorithmMenu-vizAlgorithmMenu",
        viewModel: {
            type: "menu-vizAlgorithmMenu-vizAlgorithmMenu"
        },

           // <-- submenu by nested config object
        items: [
            {
                text: 'Betweenness Centrality',
                reference:'betweennessCentrality',
                iconCls:'betweennessCentrality'
            }
        ]
});

