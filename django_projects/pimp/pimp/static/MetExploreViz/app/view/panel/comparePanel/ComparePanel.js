/**
 * @author MC
 * @description 
 */
 /**
 * comparePanel
 */
Ext.define('metExploreViz.view.panel.comparePanel.ComparePanel', {
	extend: 'Ext.panel.Panel',	
	alias: 'widget.comparePanel',
	requires: [
        "metExploreViz.view.panel.comparePanel.ComparePanelController",
        "metExploreViz.view.panel.comparePanel.ComparePanelModel"
    ],
 	controller: "panel-comparePanel-comparePanel",
    viewModel: {
        type: "panel-comparePanel-comparePanel"
    },
	collapsible: true,
    collapsed:true,
	hidden:true,
	region:'north',
	height: 300,
	width:'100%', 
	split:true,
    cls: 'comparePanel',
	resizable: {
        handles: "n",
        pinned: true
    },
	layout: {
        type: 'hbox',
        align: 'stretch'
    },
    animation: true
});