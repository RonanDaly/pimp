/**
 * @author MC
 * To select the metabolite label 
 */
Ext.define('metExploreViz.view.form.SelectDisplayMetaboliteLabel', {
        extend: 'Ext.form.ComboBox',
	    alias: 'widget.selectDisplayMetaboliteLabel',
		fieldLabel: "Metabolite label",
        displayField: 'name',
        valueField: 'value', 
        queryMode: 'local',
        multiSelect:false,
        editable:false,
        margin:'5 5 5 5',
        width:'100%', 
        store: {
                fields: ['name','value'],
                data: [
                       {'name':'Database identifier', 'value':'dbIdentifier'},
                       {'name':'Name', 'value':'name'}
                       ]
        },
        emptyText:'-- Select Display Metabolite Label --'
});