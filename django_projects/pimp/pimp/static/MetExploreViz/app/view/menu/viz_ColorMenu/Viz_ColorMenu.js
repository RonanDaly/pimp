/**
 * @author Maxime Chazalviel
 * @description Menu export network viz
 */

Ext.define('metExploreViz.view.menu.viz_ColorMenu.Viz_ColorMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizColorMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_ColorMenu.Viz_ColorMenuController',
            'metExploreViz.view.menu.viz_ColorMenu.Viz_ColorMenuModel'
        ],

        controller: "menu-vizColorMenu-vizColorMenu",
        viewModel: {
            type: "menu-vizColorMenu-vizColorMenu"
        },

           // <-- submenu by nested config object
        items: [
            {
                text: 'Display in black and white',
                checked: false,
                reference:'blackWhite',
                iconCls:'blackWhite'
            }
        ]
});

