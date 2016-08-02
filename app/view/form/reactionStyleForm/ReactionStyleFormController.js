
/**
 * @author MC
 * @description class to control reaction styles or configs
 */

Ext.define('metExploreViz.view.form.reactionStyleForm.ReactionStyleFormController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.form-reactionStyleForm-reactionStyleForm',

	/**
	 * Init function Checks the changes on reaction style
	 */
	init : function() {
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();
		
		view.on({
			setReactionStyle : function(){
				var s_ReactionStyle = metExploreD3.getReactionStyle();
				
		        view.lookupReference('chooseHeightReaction').setValue(s_ReactionStyle.getHeight());   
	
		        view.lookupReference('chooseWidthReaction').setValue(s_ReactionStyle.getWidth());   
	
		        view.lookupReference('chooseRxReaction').setValue(s_ReactionStyle.getRX());   
		   
		        view.lookupReference('chooseRyReaction').setValue(s_ReactionStyle.getRY());   
		    
		        view.lookupReference('chooseStrokeReaction').setValue(s_ReactionStyle.getStrokeWidth());   
		    
		    	view.down('#hiddenColor').lastValue = s_ReactionStyle.getStrokeColor();
				
				metExploreD3.fireEventArg("chooseStrokeColorReactionPicker", "change", s_ReactionStyle.getStrokeColor())

      			Ext.getCmp('selectDisplayReactionLabel').setValue(s_ReactionStyle.getLabel());   
			},
			scope:me
		});

		view.lookupReference('refreshReactionStyle').on({
			click : function() 
			{	
				var s_ReactionStyle = metExploreD3.getReactionStyle();
				var isset = false;
				
				var height = view.lookupReference('chooseHeightReaction').getValue();
				var newHeight = ((!isNaN(height) && height>0 && height<200) ? height : s_ReactionStyle.getHeight());
				
				var color = view.down('#hiddenColor').lastValue;
				var newColor = (color!='init' ? color : s_ReactionStyle.getStrokeColor());
				
				var width = view.lookupReference('chooseWidthReaction').getValue();
				var newWidth = (!isNaN(width) && width>0 && width<200) ? width : s_ReactionStyle.getWidth();
				
				var strokewidth = view.lookupReference('chooseStrokeReaction').getValue();
				var newstrokewidth = (!isNaN(strokewidth) && strokewidth>0 && strokewidth<200) ? strokewidth :s_ReactionStyle.getStrokeWidth();
				
				var rx = view.lookupReference('chooseRxReaction').getValue();
				var newrx = (!isNaN(rx) && rx>=0 && rx<200) ? rx : s_ReactionStyle.getRX();
				
				var ry = view.lookupReference('chooseRyReaction').getValue();
				var newry = (!isNaN(ry) && ry>=0 && ry<200) ? ry : s_ReactionStyle.getRY();

				var newLabel = view.lookupReference('selectDisplayReactionLabel').getValue();

				if(newLabel!=s_ReactionStyle.getLabel()
					|| (newHeight != s_ReactionStyle.getHeight())
					|| (newWidth != s_ReactionStyle.getWidth())
					|| (newstrokewidth != s_ReactionStyle.getStrokeWidth())
					|| (newrx != s_ReactionStyle.getRX())
					|| (newry != s_ReactionStyle.getRY())
					|| (newColor != s_ReactionStyle.getStrokeColor())
				){
					isset=true;
					s_ReactionStyle.setStrokeColor(newColor);
					s_ReactionStyle.setHeight(parseFloat(newHeight));
					s_ReactionStyle.setWidth(parseFloat(newWidth));
					s_ReactionStyle.setStrokeWidth(parseFloat(newstrokewidth));
					s_ReactionStyle.setRX(parseFloat(newrx));
					s_ReactionStyle.setRY(parseFloat(newry));
					s_ReactionStyle.setLabel(newLabel);
				}	

				if(isset){
					metExploreD3.GraphNode.refreshStyleOfReaction();							
					metExploreD3.GraphCaption.refreshStyleOfReaction();							

				}
			},
			scope : me
		});

		view.lookupReference('chooseHeightReaction').on({
			afterrender: function(me){
				var s_ReactionStyle = metExploreD3.getReactionStyle();
				
		        view.lookupReference('chooseHeightReaction').setValue(s_ReactionStyle.getHeight());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>0 && newValue<200){
		    		me.changeHeight(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseWidthReaction').on({
			afterrender: function(me){
				var s_ReactionStyle = metExploreD3.getReactionStyle();
				
		        view.lookupReference('chooseWidthReaction').setValue(s_ReactionStyle.getWidth());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>0 && newValue<200){
		    		me.changeWidth(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseRxReaction').on({
			afterrender: function(me){
				var s_ReactionStyle = metExploreD3.getReactionStyle();
				
		        view.lookupReference('chooseRxReaction').setValue(s_ReactionStyle.getRX());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>=0 && newValue<200){
		    		me.changeRx(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseRyReaction').on({
			afterrender: function(me){
				var s_ReactionStyle = metExploreD3.getReactionStyle();
				
		        view.lookupReference('chooseRyReaction').setValue(s_ReactionStyle.getRY());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>=0 && newValue<200){
		    		me.changeRy(newValue);
				}
			},
			scope : me
		});

		view.lookupReference('chooseStrokeReaction').on({
			afterrender: function(me){
				var s_ReactionStyle = metExploreD3.getReactionStyle();
				
		        view.lookupReference('chooseStrokeReaction').setValue(s_ReactionStyle.getStrokeWidth());   
		    },
		    change: function(thas, newValue, oldValue){
				if(!isNaN(newValue) && newValue>0 && newValue<200){
		    		me.changeStroke(newValue);
				}
			},
			scope : me
		});

		view.down('#hiddenColor').on({
		    change: function(newValue, oldValue){
		    	view.down('#hiddenColor').lastValue = newValue;
		    	me.changeStrokeColor(newValue);
			},
			scope : me
		});

		this.control({
			'reactionStyleForm' : {
				beforerender : function(){
					var reactionStyle = metExploreD3.getReactionStyle();

					// // Call of jscolor library
					var e = document.createElement('script'); 
					e.setAttribute('src', document.location.href.split("index.html")[0] + 'resources/lib/jscolor/jscolor.js'); 
					e.setAttribute('src', document.location.href.split("SpecRunner.html")[0] + 'resources/lib/jscolor/jscolor.js'); 
					document.body.appendChild(e); 

				 	var picker = new Ext.Panel({
				 		id:'chooseStrokeColorReactionPicker',
			            border:false,
						html: '<input size="5" onchange="Ext.getCmp(\'reactionStyleForm\').down(\'#hiddenColor\').fireEvent(\'change\', \'#\'+this.color.valueElement.value, \''+reactionStyle.getStrokeColor()+'\');" value=\''+reactionStyle.getStrokeColor().split("#")[1]+'\'" class="color {pickerFaceColor:\'#5FA2DD\',pickerPosition:\'right\', pickerFace:5}" style="border:1px solid #606060; border-radius: 2px;">'
			      	});
	      			Ext.getCmp('chooseStrokeColorReaction').add(picker);	


		            //Ext.getCmp('reactionStyleForm').down('#hidden').fireEvent('change', reactionStyle.getStrokeColor(), 'init');
		        },
		        show : function() {
					this.displayNode();
				} 
			},
			// Listeners to manage changed of label nodes
			'selectDisplayReactionLabel': 
			{
				afterrender: function(me){
					var s_ReactionStyle = metExploreD3.getReactionStyle();
					
			        me.setValue(s_ReactionStyle.getLabel());   
			    },
				change : function(that, newLabel, old){
					me.changeLabel(newLabel);
				}
			}
		});

		
	},
	
	changeHeight : function(height) {
		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("height", height);

			vis.select("g.node")
				.select("text")
				.attr("y",height);
		}
	},

	changeWidth : function(width) {
		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("width", width);

			/*vis.select("g.node")
				.select("text")
				.attr("y",height);*/
		}
	},

	changeStroke : function(stroke) {
		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").style("stroke-width", stroke);

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	changeStrokeColor : function(stroke) {
		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");

			vis.select("g.node").select("rect").style("stroke", stroke);

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	changeRx : function(rx) {
		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("rx", rx);

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	changeRy : function(ry) {
		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");
			vis.select("g.node").select("rect").attr("ry", ry);

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	changeLabel : function(label) {
		var reactionStyle = metExploreD3.getReactionStyle();
		var minDim = Math.min(reactionStyle.getWidth(),reactionStyle.getHeight());

		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){
					
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");
			vis.select("g.node").select('text').remove();
			vis.select("g.node")
				.append("svg:text")
				.attr("class", "reaction")
				.attr("id", "reaction")
	        	.attr("fill", "black")
				// .text(function(d) { return d.getName(); })
				.text(function(d) {

					var text=$("<div/>").html(label).text();
					if(text=="")
						var text=$("<div/>").html(label).text();
					return text;
				})
				.style(
					"font-size",//reactionStyle.getFontSize())
					 function(d) {
					 	return Math.min(2 * minDim,(2*minDim - 2)/ this.getComputedTextLength()* 10)+ "px";
				})
				.style("font-weight", 'bold')
				.attr("dy", ".3em");

			// vis.select("g.node")
			// 	.select("text")
			// 	.attr("y",height);
		}
	},

	displayNode : function() {
		if(d3.select("#vizExempleReaction").select("#D3vizExemple")[0][0]!=null){

			d3.select("#vizExempleReaction").select("#D3vizExemple")
				.selectAll("*").remove();
			var vis = d3.select("#vizExempleReaction")
						.select("#D3vizExemple");
		}
		else
		{
			var vis = d3.select("#vizExempleReaction")
				.append("svg")
				.attr("width", "100%")
				.attr("height", "100%")
				.attr("class", "D3vizExemple")
				.attr("id", "D3vizExemple")
		}
		
		var reactionStyle = metExploreD3.getReactionStyle();

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
		var h = parseInt(d3.select("#vizExempleReaction").style("height"));
		var w = parseInt(d3.select("#vizExempleReaction").style("width"));
				
		vis.append("svg:g").attr("class", "node")
			.style("fill", "white")
			.attr("cx",w/2).attr("cy",h/2)
			.attr("transform", "translate("+w/2+","+h/2+")")
			.append("rect")
			.attr("class", "example")
			.attr("id", "example")
			.attr("width", reactionStyle.getWidth())
			.attr("height", reactionStyle.getHeight())
			.attr("rx", reactionStyle.getRX())
			.attr("ry", reactionStyle.getRY())
			.attr("transform", "translate(-" + reactionStyle.getWidth() / 2 + ",-"
									+ reactionStyle.getHeight() / 2
									+ ")")
			.style("stroke", reactionStyle.getStrokeColor())
          	.style("stroke-width",1);

		vis.select("g.node")
			.append("svg:text")
			.attr("class", "reaction")
			.attr("id", "reaction")
        	.attr("fill", "black")
			// .text(function(d) { return d.getName(); })
			.text(function(d) {

				var text=$("<div/>").html(reactionStyle.getLabel()).text();
				if(text=="")
					var text=$("<div/>").html(reactionStyle.getLabel()).text();
				return text;
			})
			.style(
				"font-size",//reactionStyle.getFontSize())
				 function(d) {
				 	return Math.min(reactionStyle.getWidth(),(reactionStyle.getWidth() - reactionStyle.getWidth()/10)/ this.getComputedTextLength()* 10)+ "px";
			})
			.style("font-weight", 'bold')
			.attr("dy", ".3em");
	},

	zoom:function(panel) {
		d3.select("#vizExempleReaction").select("#D3vizExemple").select("#graphComponent").attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
	}
	
});

