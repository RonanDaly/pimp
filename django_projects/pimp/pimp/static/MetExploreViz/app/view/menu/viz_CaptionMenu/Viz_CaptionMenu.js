/**
 * @author Maxime Chazalviel
 * @description Menu export network viz
 */

Ext.define('metExploreViz.view.menu.viz_CaptionMenu.Viz_CaptionMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizCaptionMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_CaptionMenu.Viz_CaptionMenuController',
            'metExploreViz.view.menu.viz_CaptionMenu.Viz_CaptionMenuModel'
        ],

        controller: "menu-vizCaptionMenu-vizCaptionMenu",
        viewModel: {
            type: "menu-vizCaptionMenu-vizCaptionMenu"
        },

           // <-- submenu by nested config object
        items: [
            {
                text: 'Compartments',
                checked: false,
                reference:'captionCompartments'
            }, {
                text: 'Pathways',
                checked: false,
                reference:'captionPathways'
            }
        ]
});

