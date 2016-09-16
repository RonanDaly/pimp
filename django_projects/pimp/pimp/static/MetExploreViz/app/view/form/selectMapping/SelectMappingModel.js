Ext.define('metExploreViz.view.form.selectMapping.SelectMappingModel', {
    extend: 'Ext.app.ViewModel',

   /* requires:['metexplore.model.d3.Network',
    'metexplore.model.d3.LinkReactionMetabolite'],
*/
    alias: 'viewmodel.form-selectMapping-selectMapping',

    parent:'selectCondiditionForm',
    data: {
        name: 'metExploreViz'
    }

    // stores:{
    //     allMappings:{
    //         model:'metExploreViz.model.Mapping',
    //         storeId:'Mapping',
    //         autoLoad:false
    //     }
    // }
});
