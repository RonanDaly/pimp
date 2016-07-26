
/**
 * @author MC
 * @description class to control Style panel
 */

Ext.define('metExploreViz.view.form.updateStyleForm.UpdateStyleFormController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.form-updateStyleForm-updateStyleForm',


	init : function() {

		this.control({
			'updateStyleForm combobox[action=changeObject]': 
			{
				change : function(that, newValue, oldValue){
	                // Control if the user wants save
	                var newCombo = Ext.getCmp(newValue);
	                if(newCombo!=undefined)
	                	newCombo.setVisible(true);
	                
	                if(oldValue!=undefined)
	                {
	                	var oldCombo = Ext.getCmp(oldValue);
    	                if(oldCombo!=undefined)
    	                    oldCombo.setVisible(false);
    	            }
	            }
			}
		});
	}	
});

