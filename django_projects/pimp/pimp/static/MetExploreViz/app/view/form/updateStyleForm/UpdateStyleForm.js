/**
 * @author MC
 * @description 
 */
Ext.define('metExploreViz.view.form.updateStyleForm.UpdateStyleForm', {
    extend: 'Ext.panel.Panel',  
    alias: 'widget.updateStyleForm',
    requires: [ 
        "metExploreViz.view.form.reactionStyleForm.ReactionStyleForm",
        "metExploreViz.view.form.metaboliteStyleForm.MetaboliteStyleForm",
        "metExploreViz.view.form.generalStyleForm.GeneralStyleForm",
        "metExploreViz.view.form.updateStyleForm.UpdateStyleFormController"
    ],

    controller: "form-updateStyleForm-updateStyleForm",
    
    height: 200,
    width:'100%', 
    margin:'0 0 0 0',
    split:true,
    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    animation: true,
    
    items: [{   
        id:'selectObject',
        xtype:'combobox',
        editable: false,
        margin:'5 5 5 5',
        action:'changeObject',
        emptyText:'-- Choose an object --',
        store: [
                ['reactionStyleForm','Reaction'],
                ['metaboliteStyleForm', 'Metabolite'],
                // ['linkStyleForm', 'Link'], 
                ['generalStyleForm', 'General']
        ]
    },{
        xtype: 'menuseparator'
    }
    ,
    {   
        id:'reactionStyleForm',
        xtype:'reactionStyleForm',
        hidden:true
    }
    ,{   
        id:'metaboliteStyleForm',
        xtype:'metaboliteStyleForm',
        hidden:true
    }
    // ,
    // {   
    //     id:'linkStyleForm',
    //     xtype:'linkStyleForm',
    //     hidden:true
    // }
    ,{   
        id:'generalStyleForm',
        xtype:'generalStyleForm',
        hidden:true
    }
    ] 
});