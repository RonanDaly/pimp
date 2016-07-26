
/**
 * @author MC
 * @description class to control general styles or configs
 */

Ext.define('metExploreViz.view.form.generalStyleForm.GeneralStyleFormController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.form-generalStyleForm-generalStyleForm',

	/**
	 * Init function Checks the changes on general style
	 */
	init : function() {
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();
		
		view.on({
			setGeneralStyle : function(){
				var s_GeneralStyle = _metExploreViz.getGeneralStyle();
				view.lookupReference('chooseMaxNodes').setValue(s_GeneralStyle.getReactionThreshold()); 
				view.lookupReference('chooseDisplayForOpt').items.get("name").setValue(s_GeneralStyle.isDisplayedLabelsForOpt());   
				view.lookupReference('chooseDisplayForOpt').items.get("links").setValue(s_GeneralStyle.isDisplayedLinksForOpt());   
			},
			scope:me
		});

		view.lookupReference('refreshGeneralConf').on({
			click : function() 
			{	
				var s_GeneralStyle = metExploreD3.getGeneralStyle();
				var isset = false;
				
				var threshold = view.lookupReference('chooseMaxNodes').getValue();
				var newThreshold = ((!isNaN(threshold) && threshold>0) ? threshold : s_GeneralStyle.getReactionThreshold());
				
				var newname = view.lookupReference('chooseDisplayForOpt').items.get("name").getValue();
				var newlinks = view.lookupReference('chooseDisplayForOpt').items.get("links").getValue();

				if(
					(newThreshold != s_GeneralStyle.getReactionThreshold())
					|| (newname != s_GeneralStyle.isDisplayedLabelsForOpt())
					|| (newlinks != s_GeneralStyle.isDisplayedLinksForOpt())
				){
					isset=true;
				
					if(newlinks != s_GeneralStyle.isDisplayedLinksForOpt() ){
						if(!newlinks){
							metExploreD3.GraphLink.reloadLinks(
								"viz", 
								_metExploreViz.getSessionById("viz").getD3Data(), 
								metExploreD3.getLinkStyle(), 
								metExploreD3.getMetaboliteStyle());					

						}	
						else
						{
							d3.selectAll("path.link").remove();
						}
						metExploreD3.GraphLink.tick("viz",metExploreD3.getScaleById("viz"));
					}	
					s_GeneralStyle.setReactionThreshold(parseFloat(newThreshold));
					s_GeneralStyle.setDisplayLabelsForOpt(newname);
					s_GeneralStyle.setDisplayLinksForOpt(newlinks);
					
				}					
			},
			scope : me
		});

		view.lookupReference('chooseMaxNodes').on({
			afterrender: function(me){
				var s_GeneralStyle = metExploreD3.getGeneralStyle();
				
		        view.lookupReference('chooseMaxNodes').setValue(s_GeneralStyle.getReactionThreshold());   
		    },
			scope : me
		});

		view.lookupReference('chooseDisplayForOpt').items.get("name").on({
			afterrender: function(me){
				var s_GeneralStyle = metExploreD3.getGeneralStyle();
				
		        view.lookupReference('chooseDisplayForOpt').items.get("name").setValue(s_GeneralStyle.isDisplayedLabelsForOpt());   
		    },
			scope : me
		});

		view.lookupReference('chooseDisplayForOpt').items.get("links").on({
			afterrender: function(me){
				var s_GeneralStyle = metExploreD3.getGeneralStyle();
				
		        view.lookupReference('chooseDisplayForOpt').items.get("links").setValue(s_GeneralStyle.isDisplayedLinksForOpt());   
		    },
			scope : me
		});
		// });
	}
});

