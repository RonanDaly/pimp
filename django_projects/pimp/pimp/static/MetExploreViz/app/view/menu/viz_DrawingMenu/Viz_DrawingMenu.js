/**
 * @author Fabien Jourdan
 * @description Menu to call mapping functions on cytoscape view
 */

Ext.define('metExploreViz.view.menu.viz_DrawingMenu.Viz_DrawingMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizDrawingMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_DrawingMenu.Viz_DrawingMenuController',
            'metExploreViz.view.menu.viz_DrawingMenu.Viz_DrawingMenuModel'
        ],
        
        controller: "menu-vizDrawingMenu-vizDrawingMenu",
        viewModel: {
            type: "menu-vizDrawingMenu-vizDrawingMenu"
        },

        items:  [
             {
                 text: 'Remove side compounds',
                 reference:'removeSideCompounds',
                 tooltip:'Remove metabolites annotated as side compounds',
                 iconCls:'delete-sideCompounds'
             },
             {
                text: 'Layout', 
                scale: 'large',
                menu:{id:'vizIdLayoutMenu',xtype: 'vizLayoutMenu'},
                id:'vizLayoutMenuID',
                reference:'vizLayoutMenuID',
                padding:'0 0 0 0',
                iconCls:'drawhierarchicallayout',
                hidden:true
             },
             {
                 text: 'Duplicate side compounds',
                 reference:'duplicateSideCompounds',
                 tooltip:'Duplicate metabolites annotated as side compounds',
                 iconCls:'duplicate-sideCompounds'
             },
             {
                text: 'Color', 
                scale: 'large',
                menu:{id:'vizIdColorMenu',xtype: 'vizColorMenu'},
                id:'vizColorMenuID',
                reference:'vizColorMenuID',
                padding:'0 0 0 0',
                iconCls:'color'
             },
             {
                 text: 'Draw closer substrates/products',
                 reference:'clustMetabolites',
                 iconCls:'metabolitesLinkedByType'
             },
             {
                text: 'Highlight component', 
                scale: 'large',
                menu:{id:'vizIdConvexHullMenu',xtype: 'vizConvexHullMenu'},
                id:'vizConvexHullMenuID',
                reference:'vizConvexHullMenuID',
                padding:'0 0 0 0',
                iconCls:'highlightCompartments'
             },
             {
                 text: 'Make clusters',
                 reference:'makeClusters',
                 tooltip:'Make clusters in function of highlighted component',
                 iconCls:'makeClusters',
                 disabled:true
             }
        ]
});