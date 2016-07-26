/**
 * @author MC
 * @description 
 */
 Ext.define('metExploreViz.view.panel.viz.Viz', {
    extend: 'Ext.panel.Panel', 
    alias: 'widget.viz',
    requires: [
        'metExploreViz.view.panel.viz.VizController',
        'metExploreViz.view.panel.viz.VizModel'
    ],

    controller: "panel-viz-viz",
    viewModel: {
        type: "panel-viz-viz"
    },
    margins:'0 0 0 0',
	closable: false,
	region:'center',
	height:'100%',
	width:'100%', 
	flex:1,
    split:true,
    layout:{
       type:'vbox',
       align:'stretch',
       pack: 'center'
    }
    // ,
    // items: [
    //     {
    //         xtype: 'panel',
    //         html: '<center><img src="resources/icons/logoViz.png" alt="panoramic image" border="0"></center>'
    //     },
    //     {
    //         xtype: 'panel',
    //         html: '<div style="text-align: center;"">This panel permits to visualize metabolic network.</div>'
    //     }
    // ]
});