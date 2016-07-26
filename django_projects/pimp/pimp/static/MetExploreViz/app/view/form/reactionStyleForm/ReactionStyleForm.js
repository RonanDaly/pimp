/**
 * @author MC
 * @description 
 */
Ext.define('metExploreViz.view.form.reactionStyleForm.ReactionStyleForm', {
    extend: 'Ext.panel.Panel',  
    alias: 'widget.reactionStyleForm',
    requires: [
        "metExploreViz.view.form.reactionStyleForm.ReactionStyleFormController"
    ],
    controller: "form-reactionStyleForm-reactionStyleForm",
    
    region:'north',
    height: '100%',
    width:'100%', 
    margin:'0 0 0 0',
    flex:1,
    border:false,
    autoScroll:true,
    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    items: 
    [
    {   
        border:false,
        id:'chooseStrokeColorReaction',
        reference:'chooseStrokeColorReaction',
        xtype:'panel',
        margin:'5 5 5 5',
        layout:{
           type:'hbox',
           align:'stretch'
        },
        items:[{
            xtype: 'label',
            forId: 'color',
            margin:'0 68 0 0',
            text: 'Color :'      
        },{
            border:false,
            xtype: 'hiddenfield',
            itemId: 'hiddenColor',
            //id: 'hidden' + newId,
            value: 'init'    
        }
        ]
    }
    ,
    {   
        reference:'selectDisplayReactionLabel',
        id:'selectDisplayReactionLabel',
        xtype:'selectDisplayReactionLabel'  
    }
    , 
    {   
        xtype: 'textfield',
        reference:'chooseStrokeReaction',
        margin:'5 5 5 5',
        fieldLabel: "Stroke width:",
        displayField: 'stroke',
        editable:true,
        width:'100%', 
        width:'100%', 
        listeners: {
            change: function(newValue, oldValue){
                this.lastValue = newValue;
            }   
        }        
    }
    ,
    {   
        xtype: 'textfield',
        scale: 'small',
        reference:'chooseHeightReaction',
        margin:'5 5 5 5',
        fieldLabel: "Height :",
        displayField: 'height',
        editable:true,
        width:'100%', 
        listeners: {
            change: function(newValue, oldValue){
                this.lastValue = newValue;
            }   
        }        
    }
    ,
    {   
        xtype: 'textfield',
        reference:'chooseWidthReaction',
        margin:'5 5 5 5',
        fieldLabel: "Width :",
        displayField: 'width',
        editable:true,
        width:'100%', 
        listeners: {
            change: function(newValue, oldValue){
                this.lastValue = newValue;
            }   
        }        
    }
    ,
    {   
        xtype: 'textfield',
        reference:'chooseRxReaction',
        margin:'5 5 5 5',
        fieldLabel: "Rx :",
        displayField: 'rx',
        editable:true,
        width:'100%', 
        listeners: {
            change: function(newValue, oldValue){
                this.lastValue = newValue;
            }   
        }        
    }
    ,
    {   
        xtype: 'textfield',
        reference:'chooseRyReaction',
        margin:'5 5 5 5',
        fieldLabel: "Ry :",
        displayField: 'ry',
        editable:true,
        width:'100%', 
        listeners: {
            change: function(newValue, oldValue){
                this.lastValue = newValue;
            }   
        }        
    }
    ,
    {
        xtype: 'menuseparator'
    }
    ,
    {
        layout: {
            type: 'hbox',
            align: 'center',
            pack: 'center'
        },
        items:[{
            id :'vizExempleReaction',
            xtype : 'panel',
            margins:'0 0 0 0',
            closable: false,
            region:'center',
            height:100,
            width:100, 
            flex:1,
            split:true
        }]
    },
    {
        xtype:'button',
        iconCls:'refresh',
        margin:'5 5 5 0',
        reference: 'refreshReactionStyle',
        action: 'refreshReactionStyle'  
        
    }
    ]   
});