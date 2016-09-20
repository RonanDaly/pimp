/**
 * @author MC
 * @description 
 */
Ext.define('metExploreViz.view.form.generalStyleForm.GeneralStyleForm', {
    extend: 'Ext.panel.Panel',  
    alias: 'widget.generalStyleForm',
    requires: [
        "metExploreViz.view.form.generalStyleForm.GeneralStyleFormController",
        "metExploreViz.view.form.SelectDisplayReactionLabel",
        "metExploreViz.view.form.SelectDisplayMetaboliteLabel"
    ],
    controller: "form-generalStyleForm-generalStyleForm",
    
    region:'north',
    margin :'0 0 0 0',
    flex:1,
    width:'100%',
    border:false,
    autoScroll:true,
    layout: {
        type: 'vbox',
        align: 'stretch'
    }, 
    items: [
    {   
        xtype: 'textfield',
        reference:'chooseMaxNodes',
        margin:'5 5 5 5',
        fieldLabel: "Threshold of reactions for optimization :",
        displayField: 'threshold',
        editable:true,
        margin:'5 5 5 5',
        width:'100%', 
        listeners: {
            change: function(newValue, oldValue){
                this.lastValue = newValue;
            }   
        }        
    }
    ,  
    {
        xtype      : 'fieldcontainer',
        fieldLabel : 'Remove on visualisation ',
        reference:'chooseDisplayForOpt',
        margin:'5 5 5 5',
        defaultType: 'checkboxfield',
        items: [
            {
                boxLabel  : 'Name on nodes',
                name      : 'display',
                inputValue: '1',
                checked   : true,
                id        : 'name'
            }, {
                boxLabel  : 'Links',
                name      : 'display',
                inputValue: '2',
                checked   : true,
                id        : 'links'
            }
        ]
    }
    ,  
    {
        xtype:'button',
        iconCls:'refresh',
        margin:'5 5 5 0',
        reference: 'refreshGeneralConf',
        action: 'refreshGeneralConf'  
    }
    ]  
});