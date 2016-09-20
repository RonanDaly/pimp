Ext.define('metExploreViz.view.button.buttonImportToNetwork.ButtonImportToNetwork', {
    extend: 'Ext.form.Panel',
    alias:'widget.buttonImportToNetwork',
	controller : 'buttonImportToNetwork',
    requires: [
    	'metExploreViz.view.button.buttonImportToNetwork.ButtonImportToNetworkController'
    ],
    text: 'Import mapping from tab file',
            
    items: [{
        xtype: 'filefield',
        name : 'fileData',
        buttonOnly: true,
            // text: '',
        height:'100%',
        width:'100px', 

      //   buttonConfig: {
      //       iconCls: 'importToRsx',
    		// scale: 'large',                                
      //       border: false
      //   },
        reference : 'importNetwork',
        buttonConfig: {
            id : 'IDimportNetwork'
    //     border: false,
    //     iconCls: 'importToRsx',
    //     text: 'Mapping',
    //     height:'100%',
    //     width:'100%', 
    //     scale: 'large',                                
    //     padding:'0 0 0 0'
        }
    }],
    hideLabel: true
    //tooltip:'Choose a file to create the network',
    
});
