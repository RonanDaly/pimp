Ext.define('metExploreViz.view.panel.comparePanel.ComparePanelModel', {
    extend: 'Ext.app.ViewModel',

   /* requires:['metexplore.model.d3.Network',
    'metexplore.model.d3.LinkReactionMetabolite'],
*/
    alias: 'viewmodel.panel-comparePanel-comparePanel',

    parent:'graphPanel',
    data: {
        name: 'metExploreViz'
    }

    /*stores:{
    	d3network:{
            model:'metexplore.model.d3.Network',
            autoLoad:false
        },
        linkReactionMetab:{
            model:'metexplore.model.d3.LinkReactionMetabolite',
            autoLoad:false
        }
    }*/

});
