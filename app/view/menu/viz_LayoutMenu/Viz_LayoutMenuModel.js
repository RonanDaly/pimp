Ext.define('metExploreViz.view.menu.viz_LayoutMenu.Viz_LayoutMenuModel', {
    extend: 'Ext.app.ViewModel',

   /* requires:['metexplore.model.d3.Network',
    'metexplore.model.d3.LinkReactionMetabolite'],
*/
    alias: 'viewmodel.menu-vizLayoutMenu-vizLayoutMenu',

    parent:'graphPanel',
    data: {
        name: 'metExploreViz'
    }
});
