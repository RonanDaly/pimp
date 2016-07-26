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
            {"name":"Discrete"}
        ]
    },
    flex:1,
    displayField: 'name',
    valueField: 'name',
    queryMode: 'local',
    editable:false,
    emptyText:'-- Type of data --',
    margin:'5 0 5 0',
    anyMatch : true
});