Ext.define('metExploreViz.view.menu.viz_CaptionMenu.Viz_CaptionMenuController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.menu-vizCaptionMenu-vizCaptionMenu',

/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();
		
		view.on({
			setGeneralStyle : function(){
				var s_GeneralStyle = _metExploreViz.getGeneralStyle();
				if(s_GeneralStyle.isDisplayedCaption()=="Compartments"){
					view.lookupReference('captionCompartments').setChecked(true);  
				} 
				else
				{
					if(s_GeneralStyle.isDisplayedCaption()=="Pathways"){
						view.lookupReference('captionPathways').setChecked(true);  
					}
					else
					{
						view.lookupReference('captionCompartments').setChecked(false);  
						view.lookupReference('captionPathways').setChecked(false);  
					}
				}
			},
			scope:me
		});

		view.lookupReference('captionCompartments').on({
			click : me.checkHandler,
			scope : me
		});

        view.lookupReference('captionPathways').on({
			click : me.checkHandler,
			scope : me
		});
	},
	checkHandler: function (item, checked){
        var me 		= this;
        if(item.checked){
        	me.captionComponents(item.text);
        	item.parentMenu.items.items
                .filter(function(anItem){
                    return anItem!=item;
                })  
                .forEach(function(anItem){
                    anItem.setChecked(false);
                }
            );       
        }
        else
        {
        	me.hideComponents();
        }
    },
    captionComponents : function(component){

    	var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();


		var s_GeneralStyle = _metExploreViz.getGeneralStyle();
		
		s_GeneralStyle.setDisplayCaption(component);
		if(component=="Pathways"){
			metExploreD3.GraphCaption.colorPathwayLegend(175);
			d3.select("#viz").select("#D3viz")
					.select('#captionComparment')
					.classed('hide', true);
		}
		else
		{
			if(component=="Compartments"){
				d3.select("#viz").select("#D3viz")
								.select('#captionComparment')
								.classed('hide', false);
				d3.select("#viz").select("#D3viz")
					.select('#captionPathway')
					.remove();
			}
		}
	},
    hideComponents : function(){

    	var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();

		var s_GeneralStyle = _metExploreViz.getGeneralStyle();
		if(s_GeneralStyle.isDisplayedCaption()=="Pathways")
			d3.select("#viz").select("#D3viz")
				.select('#captionPathway')
				.remove();
		else
			if(s_GeneralStyle.isDisplayedCaption()=="Compartments")
				d3.select("#viz").select("#D3viz")
					.select('#captionComparment')
					.classed('hide', true);

		s_GeneralStyle.setDisplayCaption(false);
		metExploreD3.fireEvent("generalStyleForm", "setGeneralStyle");
	}
});