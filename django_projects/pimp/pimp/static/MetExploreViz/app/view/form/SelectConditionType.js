/**
 * @author MC
 * @description combobox to select type of condition
 */
/**
 * selectConditionType
 */
Ext.define('metExploreViz.view.form.SelectConditionType', {
    extend: 'Ext.form.field.ComboBox',
	alias: 'widget.selectConditionType',
	store: {
        fields: ['name'],
        data : [
            {"name":"Continuous"},
            {"name":"Discrete"},
            {"name":"Flux"}
        ]
    },
    listeners: {
        render: function(c) {
            new Ext.ToolTip({
                target: c.getEl(),
                html: 'Select a type of data'
            });
        },
        change: function(){
            console.log('change');
            var comboCond = Ext.getCmp('selectCondition');
            comboCond.clearValue();
        }
    }, 
    displayField: 'name',
    valueField: 'name',
    queryMode: 'local',
    editable:false,
    emptyText:'-- Type of data --',
    margin:'5 0 5 0',
    anyMatch : true
});