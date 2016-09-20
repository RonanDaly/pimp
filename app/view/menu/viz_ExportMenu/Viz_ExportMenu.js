/**
 * @author Fabien Jourdan
 * @description Menu export network viz
 */

Ext.define('metExploreViz.view.menu.viz_ExportMenu.Viz_ExportMenu', {
        extend: 'Ext.menu.Menu', 
        alias: 'widget.vizExportMenu',
        
        requires: [
            'metExploreViz.view.menu.viz_ExportMenu.Viz_ExportMenuController',
            'metExploreViz.view.menu.viz_ExportMenu.Viz_ExportMenuModel'
        ],

        controller: "menu-vizExportMenu-vizExportMenu",
        viewModel: {
            type: "menu-vizExportMenu-vizExportMenu"
        },
        
        items:  [
             {
                 text: 'Export Viz as svg',
                 reference:'exportSVG',
                 tooltip:'Export network viz as a svg file',
                 iconCls:'exportSvg'
                },
                {
                 text: 'Export Viz as png',
                 reference:'exportPNG',
                 tooltip:'Export network viz as a png file',
                 iconCls:'exportPng'
                },
                {
                 text: 'Export Viz as jpeg',
                 reference:'exportJPG',
                 tooltip:'Export network viz as a jpeg file',
                 iconCls:'exportJpg'
                }
            // ,
            //     {
            //      text: 'Export Comparison of Condition',
            //      reference:'exportComparison',
            //      tooltip:'Export Comparison of Condition as a png file',
            //      iconCls:'exportComparePng'
            //     }
        ]
});

