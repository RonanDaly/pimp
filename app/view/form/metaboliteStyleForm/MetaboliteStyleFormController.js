
/**
 * @author MC
 * @description class to control metabolite styles or configs
 */

Ext.define('metExploreViz.view.form.metaboliteStyleForm.MetaboliteStyleFormController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.form-metaboliteStyleForm-metaboliteStyleForm',

	/**
	 * Init function Checks the changes on metabolite style
	 */
	init : function() {
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();
			
		view.on({
			setMetaboliteStyle : function(){
				var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
				
		        view.lookupReference('chooseHeightMetabolite').setValue(s_MetaboliteStyle.getHeight());   
	
		        view.lookupReference('chooseWidthMetabolite').setValue(s_MetaboliteStyle.getWidth());   
	
		        view.lookupReference('chooseRxMetabolite').setValue(s_MetaboliteStyle.getRX());   
		   
		        view.lookupReference('chooseRyMetabolite').setValue(s_MetaboliteStyle.getRY());   
		    
		        view.lookupReference('chooseStrokeMetabolite').setValue(s_MetaboliteStyle.getStrokeWidth());   
		   
      			Ext.getCmp('selectDisplayMetaboliteLabel').setValue(s_MetaboliteStyle.getLabel());   
			},
			scope:me
		});

		view.lookupReference('refreshMetaboliteStyle').on({
			click : function() 
			{	
				var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
				var isset = false;
				
				var height = view.lookupReference('chooseHeightMetabolite').getValue();
				var newHeight = ((!isNaN(height) && height>0 && height<200) ? height : s_MetaboliteStyle.getHeight());
				
				var width = view.lookupReference('chooseWidthMetabolite').getValue();
				var newWidth = (!isNaN(width) && width>0 && width<200) ? width : s_MetaboliteStyle.getWidth();
				
				var strokewidth = view.lookupReference('chooseStrokeMetabolite').getValue();
				var newstrokewidth = (!isNaN(strokewidth) && strokewidth>0 && strokewidth<200) ? strokewidth :s_MetaboliteStyle.getStrokeWidth();
				
				var rx = view.lookupReference('chooseRxMetabolite').getValue();
				var newrx = (!isNaN(rx) && rx>=-100 && rx<200) ? rx : s_MetaboliteStyle.getRX();
				
				var ry = view.lookupReference('chooseRyMetabolite').getValue();
				var newry = (!isNaN(ry) && ry>=0 && ry<200) ? ry : s_MetaboliteStyle.getRY();

				var newLabel = view.lookupReference('selectDisplayMetaboliteLabel').getValue();

				if(newLabel!=s_MetaboliteStyle.getLabel()
					|| (newHeight != s_MetaboliteStyle.getHeight())
					|| (newWidth != s_MetaboliteStyle.getWidth())
					|| (newstrokewidth != s_MetaboliteStyle.getStrokeWidth())
					|| (newrx != s_MetaboliteStyle.getRX())
					|| (newry != s_MetaboliteStyle.getRY())
				){
					console.log("ok");
					isset=true;
					s_MetaboliteStyle.setHeight(parseFloat(newHeight));
					s_MetaboliteStyle.setWidth(parseFloat(newWidth));
					s_MetaboliteStyle.setStrokeWidth(parseFloat(newstrokewidth));
					s_MetaboliteStyle.setRX(parseFloat(newrx));
					s_MetaboliteStyle.setRY(parseFloat(newry));
					s_MetaboliteStyle.setLabel(newLabel);
				}		

				if(isset){
					metExploreD3.GraphNode.refreshStyleOfMetabolite();								
					metExploreD3.GraphCaption.refreshStyleOfMetabolite();								
				}
			},
			scope : me
		});

		view.lookupReference('chooseHeightMetabolite').on({
			afterrender: function(me){
				var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
				
		        view.lookupReference('chooseHeightMetabolite').setValue(s_MetaboliteStyle.getHeight());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>0 && newValue<200){
		    		me.changeHeight(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseWidthMetabolite').on({
			afterrender: function(me){
				var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
				
		        view.lookupReference('chooseWidthMetabolite').setValue(s_MetaboliteStyle.getWidth());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>0 && newValue<200){
		    		me.changeWidth(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseStrokeMetabolite').on({
			afterrender: function(me){
				var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
				
		        view.lookupReference('chooseStrokeMetabolite').setValue(s_MetaboliteStyle.getStrokeWidth());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>0 && newValue<200){
		    		me.changeStroke(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseRxMetabolite').on({
			afterrender: function(me){
				var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
				
		        view.lookupReference('chooseRxMetabolite').setValue(s_MetaboliteStyle.getRX());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>=0 && newValue<200){
		    		me.changeRx(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseRyMetabolite').on({
			afterrender: function(me){
				var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
				
		        view.lookupReference('chooseRyMetabolite').setValue(s_MetaboliteStyle.getRY());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>=0 && newValue<200){
		    		me.changeRy(newValue);
				}
			},
			scope : me
		});

		this.control({
			'metaboliteStyleForm' : {
		        show : function() {
					this.displayNode();
				} 
			},
			// Listeners to manage changed of label nodes
			'selectDisplayMetaboliteLabel': 
			{
				afterrender: function(me){
					var s_MetaboliteStyle = metExploreD3.getMetaboliteStyle();
					
			        me.setValue(s_MetaboliteStyle.getLabel());   
			    },
				change : function(that, newLabel, old){
					me.changeLabel(newLabel);
				}
			}
		});
	},
	changeHeight : function(height) {
		if(d3.select("#vizExempleMetabolite").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleMetabolite")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("height", height);

			vis.select("g.node")
				.select("text")
				.attr("y",height);
		}
	},

	changeWidth : function(width) {
		if(d3.select("#vizExempleMetabolite").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleMetabolite")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("width", width);

			/*vis.select("g.node")
				.select("text")
				.attr("y",height);*/
		}
	},

	changeStroke : function(stroke) {
		if(d3.select("#vizExempleMetabolite").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleMetabolite")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").style("stroke-width", stroke);

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	changeRx : function(rx) {
		if(d3.select("#vizExempleMetabolite").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleMetabolite")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("rx", rx);

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	changeRy : function(ry) {
		if(d3.select("#vizExempleMetabolite").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleMetabolite")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("ry", ry);

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	changeLabel : function(label) {
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();

		if(d3.select("#vizExempleMetabolite").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleMetabolite")
						.select("#D3vizExemple");
			vis.select("g.node").select('text').text(function(d) {

				var text=$("<div/>").html(label).text();
				if(text=="")
					var text=$("<div/>").html(label).text();
				return text;
			})

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	displayNode : function() {
		if(d3.select("#vizExempleMetabolite").select("#D3vizExemple")[0][0]!=null){

			d3.select("#vizExempleMetabolite").select("#D3vizExemple")
				.selectAll("*").remove();
			var vis = d3.select("#vizExempleMetabolite")
						.select("#D3vizExemple");
		}
		else
		{
			var vis = d3.select("#vizExempleMetabolite")
				.append("svg")
				.attr("width", "100%")
				.attr("height", "100%")
				.attr("class", "D3vizExemple")
				.attr("id", "D3vizExemple")
		}
		
		var metaboliteStyle = metExploreD3.getMetaboliteStyle();

		var that = this;

		var zoomListener = d3.behavior
			.zoom()
			.scaleExtent([ 0.1, 20 ])
			.on("zoom", function(e){
				that.zoom();
			})

		vis = vis.call(zoomListener)
			// Remove zoom on double click
			.attr("pointer-events", "all")
			.append('svg:g')
			.attr("class","graphComponent").attr("id","graphComponent")

		// Get height and witdh of viz panel
		var h = parseInt(d3.select("#vizExempleMetabolite").style("height"));
		var w = parseInt(d3.select("#vizExempleMetabolite").style("width"));
				
		vis.append("svg:g").attr("class", "node")
			.style("fill", "white")
			.attr("cx",w/2).attr("cy",h/2)
			.attr("transform", "translate("+w/2+","+h/2+")")
			.append("rect")
			.attr("width", metaboliteStyle.getWidth())
			.attr("height", metaboliteStyle.getHeight())
			.attr("rx", metaboliteStyle.getRX())
			.attr("ry", metaboliteStyle.getRY())
			.attr("transform", "translate(-" + metaboliteStyle.getWidth() / 2 + ",-"
									+ metaboliteStyle.getHeight() / 2
									+ ")")
			.style("stroke", metaboliteStyle.getStrokeColor())
			.style("stroke-width", metaboliteStyle.getStrokeWidth());

		var minDim = Math.min(metaboliteStyle.getWidth(),metaboliteStyle.getHeight());
		vis.select("g.node")
			.append("svg:text")
			.attr("class", "metabolite")
			.attr("id", "metabolite")
    	 	.attr("fill", "black")
			.text(function(d) {

				var text=$("<div/>").html(metaboliteStyle.getLabel()).text();
				if(text=="")
					var text=$("<div/>").html(metaboliteStyle.getLabel()).text();
				return text;
			})
			.style("font-size",metaboliteStyle.getFontSize())
			.style("paint-order","stroke")
			.style("stroke-width", '1')
			.style("stroke", "white")
			.style("stroke-opacity", "0.7")
			// 	function(d) {
			// 		return Math.min(
			// 			(minDim) / 2,
			// 			((minDim - 3)/ this.getComputedTextLength() * 10) / 2
			// 		)+ "px";
			// })
			.attr("dy", ".4em")
			.style("font-weight", 'bold')
			.attr("y",metaboliteStyle.getHeight());
	},

	zoom:function(panel) {
		d3.select("#vizExempleMetabolite").select("#D3vizExemple").select("#graphComponent").attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
	}
	
});

