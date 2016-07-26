/**
 * @author MC
 * @description combobox to select condition in mapping
 * selectCondition
 */
Ext.define('metExploreViz.view.form.selectCondition.SelectCondition', {
    extend: 'Ext.form.field.ComboBox',
	alias: 'widget.selectCondition',
	requires: [
            "metExploreViz.view.form.selectCondition.SelectConditionController"
    ],
    controller: "form-selectCondition-selectCondition",
    store: {
        fields: ['name']
    },
	displayField: 'name',
	valueField: 'name',
	queryMode: 'local',
	editable:false,
	emptyText:'-- Select a condition --',
	margin:'5 0 5 0',
	anyMatch : true
});