/**
 * @author MC
 * @description class to control contion selection panel and to draw mapping in the mapping story
 */

Ext.define('metExploreViz.view.panel.networkPanel.NetworkPanelController', {
	extend: 'Ext.app.ViewController',
	alias: 'controller.panel-networkPanel-networkPanel',

	/**
 * Aplies event linsteners to the view
 */
	init:function(){
		var me 		= this,
		viewModel   = me.getViewModel(),
		view      	= me.getView();
		
		view.on({
			afterrender : me.initParams,
			scope:me
		});	

		view.on({
			afterlunch : function(panel){
				
				me.myRender(panel);
				Ext.on('resize', function(w, h){
					//console.log(document.getElementById("visualisation"));
				    document.getElementById("visualisation").style.width = w+"px";
				    document.getElementById("visualisation").style.height = h+"px";
				    view.setSize(w, h);
	            });
			},
			scope:me
		});	    
	},

	initParams : function(){
		
        if(Ext.getCmp("networkPanel")!= undefined){

        	var mask = new Ext.LoadMask({
                    target: Ext.getCmp("networkPanel"), 
                    msg: 'This panel allows to visualize metabolic network.', 
                    id:"maskInit",
                    msgCls:'msgClsLaunchMask'
                });
            mask.show();
            var maskMsgDiv = mask.getEl().down('.x-mask-msg');
            var buttonDiv = maskMsgDiv.getFirstChild()
								.appendChild({
									tag: 'div', 
									class: 'x-mask-msg-text'
								});


			Ext.create('Ext.form.Label',{
		        text: 'Load network from : ',
		        id: 'textloadnetworkfrom',
		        style:'top : 15px',
		        renderTo:buttonDiv
		    });

            Ext.create('Ext.button.Button',{
		        text: 'JSON File',
		        id: 'butloadnetworkfromjson',
		        style:'margin : 10px 10px 10px 10px',
		        handler: function(){
		            var component = Ext.getCmp("IDimportNetwork");
			        if(component!= undefined){
						component.fileInputEl.dom.click();
			        }
			        mask.hide();
		        },
		        renderTo:buttonDiv
		    });

		    // Ext.create('metExploreViz.view.button.buttonImportToNetworkFromWebsite.ButtonImportToNetworkFromWebsite',{
		    //     text: 'Website',
		    //     style:'margin : 10px 10px 10px 10px',
		    //     handler: function(){
		    //         mask.hide();
		    //     },
		    //     renderTo:buttonDiv

		    // });

		    Ext.create('Ext.button.Button',{
		        text: metExploreD3.getGeneralStyle().getWebsiteName(),
		        id:'buttonImportToNetworkFromWebsite',
	            disabled:true,
	            hidden:false,
		        style:'margin : 10px 10px 10px 10px',
		        handler: function(){
		        	metExploreD3.GraphPanel.refreshPanel(_metExploreViz.getDataFromWebSite());
                    mask.hide();
		        },
		        listeners: {
			        hideInitialLoadButtons: function(){
			        	Ext.getCmp("textloadnetworkfrom").hide();
			        	Ext.getCmp("butloadnetworkfromjson").hide();
			        	this.hide();
			        },
					hideMask: function(){
                        mask.hide();
                    },
			        setGeneralStyle: function(){
			        	this.setText(metExploreD3.getGeneralStyle().getWebsiteName());
			        },
			        cartFilled: function() {
			            this.setDisabled(false);
			        }
			    },
		        renderTo:buttonDiv
			});
        }
		var networkVizSession = new NetworkVizSession();
	    networkVizSession.setVizEngine("D3");
	    networkVizSession.setId('viz');
	    networkVizSession.setMapped('false');
	    networkVizSession.setDisplayNodeName('name');

	    _metExploreViz.addSession(networkVizSession);
	},

	myRender : function(panel){
		var me 		= this,
		view      	= me.getView();

		var element = document.getElementById(panel);
    	view.render(element);
	}
});

