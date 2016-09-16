Ext.define('metExploreViz.view.button.buttonImportSideCompounds.ButtonImportSideCompounds', {
    extend: 'Ext.form.Panel',
    alias:'widget.buttonImportSideCompounds',
	controller : 'buttonImportSideCompounds',
    requires: [
    	'metExploreViz.view.button.buttonImportSideCompounds.ButtonImportSideCompoundsController'
    ],
    hideLabel: true,
    items: [{
        xtype: 'filefield',
        name : 'fileData',
        buttonOnly: true,   
        id : 'IDimportSC',
        reference : 'importSideCompoundsHidden',
        buttonConfig: {
            id : 'IDimportSideCompounds'
    //     border: false,
    //     iconCls: 'importToRsx',
    //     text: 'SideCompounds',
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
    //     text: 'SideCompounds',
    //     height:'100%',
    //     width:'100%', 
    //     scale: 'large',                                
    //     padding:'0 0 0 0'
    // }
});