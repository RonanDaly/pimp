Ext.define('metExploreViz.view.button.buttonImportMapping.ButtonImportMapping', {
    extend: 'Ext.form.Panel',
    alias:'widget.buttonImportMapping',
	controller : 'buttonImportMapping',
    requires: [
    	'metExploreViz.view.button.buttonImportMapping.ButtonImportMappingController'
    ],
    hideLabel: true,
    items: [{
        xtype: 'filefield',
        name : 'fileData',
        buttonOnly: true,   
        id : 'IDimport',
        reference : 'importMappingHidden',
        buttonConfig: {
            id : 'IDimportMapping'
    //     border: false,
    //     iconCls: 'importToRsx',
    //     text: 'Mapping',
    //     height:'100%',
    //     width:'100%', 
    //     scale: 'large',                                
    //     padding:'0 0 0 0'
        }
    }]

    //tooltip:'Choose a file to create the network',
    // buttonConfig: {
    //     border: false,
    //     iconCls: 'importToRsx',
    //     text: 'Mapping',
    //     height:'100%',
    //     width:'100%', 
    //     scale: 'large',                                
    //     padding:'0 0 0 0'
    // }
});