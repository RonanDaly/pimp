/**
 * @author MC
 * @description 
 */
Ext.define('metExploreViz.view.form.selectConditionForm.SelectConditionForm', {
    extend: 'Ext.panel.Panel',  
    alias: 'widget.selectConditionForm',
    requires: [
        'metExploreViz.view.form.SelectConditionType',
        'metExploreViz.view.form.selectCondition.SelectCondition',
        'metExploreViz.view.form.selectMapping.SelectMapping',
        "metExploreViz.view.form.selectConditionForm.SelectConditionFormController",
        "metExploreViz.view.form.selectConditionForm.SelectConditionFormModel"
    ],
    controller: "form-selectConditionForm-selectConditionForm",
    viewModel: {
        type: "form-selectConditionForm-selectConditionForm"
    },
    layout:{
       type:'vbox',
       align:'stretch'
    },
    // collapsible: true,
    // collapsed:false,
    region:'north',
    width:'100%', 
    margins:'0 0 0 0',
    split:true,
    animation: true,
    autoScroll: true,
    autoHeight: true,

    items: [
    {
        id:'selectMappingVisu',
        xtype:'selectMapping',
        disabled:true
    },
    {
        xtype: 'menuseparator'
    },
    {
        id:'selectConditionType',
        xtype:'selectConditionType',
        reference:'selectConditionType',
        disabled:true
    }
    ,
    {

        margin:'10 0 0 5',
        xtype      : 'fieldcontainer',
        defaultType: 'checkboxfield',
        reference : 'opacity', 
        hidden : true,
        items: [
            {
                boxLabel  : 'Opacity',
                name      : 'opacity',
                inputValue: true,
                id        : 'opacityCheck'
            }
        ]
    },
    {   
        border:false,
        id:'chooseCondition',
        xtype:'panel',
        autoScroll: true,
        layout:{
           type:'hbox',
           align:'stretch'
        },
        items:[{
            id:'selectCondition',
            xtype:'selectCondition',
            reference:'selectCondition',
            disabled:true           
        }
        ]
    }
        ,{
            xtype: 'menuseparator'
    }
    ]  
});