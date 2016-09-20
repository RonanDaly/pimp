var metExploreD3 = {

    // Naming
    GraphUtils:"",
    GraphCaption:"",
    GraphNetwork:"",
    GraphLink:"",
    GraphFunction:"",
    GraphMapping:"",
    GraphPanel:"",
    GraphPath:"",
    GraphNode:"",

    testWSMappingGraphToken : function(token, inchis, pathways, func) {
       
        var data={
                token: token,
                Content: inchis,
                pathways: pathways
        };
       
        Ext.Ajax.request({
            // Bien préciser qu'il faut envoyer les données en POST:
            method:'POST',
            
            url: 'http://metexplore.toulouse.inra.fr:8080/metExploreWebService/mapping/launchtokenmapping/inchi/1363/filteredbypathways/',
            
            // le json a envoyer en post:
            jsonData:data,
            success: function(response, opts) {
                
                var rep=Ext.decode(response.responseText);
                func(rep);
            },
            failure:function(response, opts){
                console.log(response)
            }
        });
    },

    /*****************************************************
    * Update the network to fit the cart content
    */
    testWSMappingPathways : function(inchis, func) {
        var data={
                token: "",
                Content: inchis
        };

       
        Ext.Ajax.request({
            // Bien préciser qu'il faut envoyer les données en POST:
            method:'POST',
            
            url: 'http://metexplore.toulouse.inra.fr:8080/metExploreWebService/mapping/launchtokenmapping/inchi/1363/aspathways/',
            
            // le json a envoyer en post:
            jsonData:data,
            success: function(response, opts) {
                
                var rep=Ext.decode(response.responseText);
                func(rep);
            },
            failure:function(response, opts){
                console.log(response)
            }
        });
    },

    /*****************************************************
    * Update the network to fit the cart content
    */
    testWSMappingGraph : function(inchis, pathws, func) {
        var pathways = "";
        pathws.forEach(function(pathway){
            pathways+=pathway;
            if(pathws.indexOf(pathway)!=pathws.length-1)
                pathways+=",";
        });

        var data={
                token: "",
                Content: inchis,
                pathways: "("+pathways+")"
        };

       
        Ext.Ajax.request({
            // Bien préciser qu'il faut envoyer les données en POST:
            method:'POST',
            
            url: 'http://metexplore.toulouse.inra.fr:8080/metExploreWebService/mapping/launchtokenmapping/inchi/1363/filteredbypathways/',
            
            // le json a envoyer en post:
            jsonData:data,
            success: function(response, opts) {
                
                var rep=Ext.decode(response.responseText);
                func(rep);
            },
            failure:function(response, opts){
                console.log(response)
            }
        });
    },

    resetMetExploreViz : function(){
        metExploreD3.fireEvent('selectConditionForm', "resetMapping");
        metExploreD3.fireEvent('graphPanel', "initSearch");
        if(_metExploreViz.getMappingsLength()>0 && key=="viz")
        {
            metExploreD3.fireEventArg('buttonMap', "reloadMapping", false);
            metExploreD3.fireEventArg('buttonRefresh', "reloadMapping", false);
            _metExploreViz.resetMappings();

        }
        var component = Ext.getCmp('comparisonSidePanel');
        if(component!= undefined)
            component.collapse();
              

            // If the main network is already mapped we inform the user: OK/CANCEL
            // if(networkVizSession.isMapped()!='false')    
            // {
                    
            //  var newMapping ='true';
            //  me.closeMapping(newMapping);
            // }
        
        if(Ext.getCmp("maskInit")!= undefined){
            var mask = Ext.getCmp("maskInit");
            mask.show();

            Ext.getCmp("buttonImportToNetworkFromWebsite").setDisabled(true); 
        }
        var sessions = _metExploreViz.getSessionsSet();
        for (var key in sessions) {   
            if(sessions[key].getForce()!=undefined)                  
            {
                sessions[key].getForce().on("end", null);
                sessions[key].getForce().stop(); 
            }
            if(sessions[key].getId()!="viz"){
               if(Ext.getCmp(sessions[key].getId().replace("-body", ""))!=null)
                    Ext.getCmp(sessions[key].getId().replace("-body", "")).destroy()
            }  
        }
        
        d3.select("#viz").select("#D3viz").remove();

        _metExploreViz.sessions = {};

        _metExploreViz.launched = false;
        _metExploreViz.dataFromWebSite = null;
         _metExploreViz.initialData = undefined;
        
        _metExploreViz.comparedPanels = [];
        _metExploreViz.mappings = [];
        _metExploreViz.linkedByTypeOfMetabolite = false;
        _metExploreViz.oldCoodinates = [];

        var networkVizSession = new NetworkVizSession();
        networkVizSession.setVizEngine("D3");
        networkVizSession.setId('viz');
        networkVizSession.setMapped('false');
        networkVizSession.setDisplayNodeName('name');

        _metExploreViz.addSession(networkVizSession);
    },

    // Interface with stores
    // Getters & Setters
    getGlobals : function(){
        return _metExploreViz;
    },

    newNetworkData : function(panel){
        return new NetworkData(panel);
    },
    
    newGeneralStyle : function(siteName, minContinuous, maxContinuous, max, dispLabel, dispLink, dispConvexhull, clust, dispCaption){
        return new GeneralStyle(siteName, minContinuous, maxContinuous, max, dispLabel, dispLink, dispConvexhull, clust, dispCaption);
    },

    // CompartmentInBioSource
    getCompartmentInBiosourceSet : function(){
        return _metExploreViz.getSessionById("viz").getD3Data().getCompartments();
    },
    sortCompartmentInBiosource : function(){
        _metExploreViz.getSessionById("viz").getD3Data().sortCompartments();
    },
    getCompartmentInBiosourceLength : function(){
        return _metExploreViz.getSessionById("viz").getD3Data().getCompartmentsLength();
    },
    getCompartmentsGroup : function(){
        var compartmentGroup = [];

        var sqrt = Math.ceil(Math.sqrt(metExploreD3.getCompartmentInBiosourceLength()));
        
        var h = parseInt(metExploreD3.GraphPanel.getHeight("viz"));
        var w = parseInt(metExploreD3.GraphPanel.getWidth("viz"));

        var hDiv = h/sqrt;
        var wDiv = w/sqrt;

        var hBegin = hDiv/2;
        var wBegin = wDiv/2;

        var alt = -1;

        metExploreD3.getCompartmentInBiosourceSet()
            .forEach(function(compartment){
                var mod = metExploreD3.getCompartmentInBiosourceSet().indexOf(compartment)%sqrt; 
                if(mod==0)
                    alt++;

                var xCenter = wBegin+(mod * wDiv);
                var yCenter = hBegin+(alt * hDiv);
                var object = {key:compartment.getIdentifier(), center:{x:xCenter, y:yCenter}};
                compartmentGroup.push(object);
            }
        );

        function addNodeInGroup(node, compartment){
            if(compartment!=undefined){
               
                if(compartment.values==undefined)
                        compartment.values=[];

                if(compartment.values.indexOf(node)==-1)
                    compartment.values.push(node);
            }
        }
        _metExploreViz.getSessionById("viz").getD3Data().getLinks()
            .forEach(function(d){
                var source = d.source;
                var target = d.target;
                if(source.getBiologicalType()=="metabolite"){

                   
                    addNodeInGroup(
                        source, 
                        compartmentGroup
                            .find(function(compart)
                            {
                                return compart.key==source.getCompartment();
                            }
                        )
                    );
                    addNodeInGroup(
                        target, 
                        compartmentGroup
                            .find(function(compart)
                            {
                                return compart.key==source.getCompartment();
                            }
                        )
                    );
                }
                else
                {
                    addNodeInGroup(
                        source, 
                        compartmentGroup
                            .find(function(compart)
                            {
                                return compart.key==target.getCompartment();
                            }
                        )
                    );
                    addNodeInGroup(
                        target, 
                        compartmentGroup
                            .find(function(compart)
                            {
                                return compart.key==target.getCompartment();
                            }
                        )
                    );
                }
            });
        return compartmentGroup;
    },

    // CompartmentInBioSource
    getPathwaysSet : function(){
        return _metExploreViz.getSessionById("viz").getD3Data().getPathways();
    },
    getPathwaysGroup : function(){
        var pathwayGroup = [];

        var sqrt = Math.ceil(Math.sqrt(metExploreD3.getPathwaysLength()));
        
        var h = parseInt(metExploreD3.GraphPanel.getHeight("viz"));
        var w = parseInt(metExploreD3.GraphPanel.getWidth("viz"));

        var hDiv = h/sqrt;
        var wDiv = w/sqrt;

        var hBegin = hDiv/2;
        var wBegin = wDiv/2;

        var alt = -1;

        metExploreD3.getPathwaysSet()
            .forEach(function(pathway){
                var mod = metExploreD3.getPathwaysSet().indexOf(pathway)%sqrt; 
                if(mod==0)
                    alt++;

                var xCenter = wBegin+(mod * wDiv);
                var yCenter = hBegin+(alt * hDiv);
                var object = {key:pathway, center:{x:xCenter, y:yCenter}};
                pathwayGroup.push(object);
            }
        );

        function addNodeInGroup(node, pathway){
            if(pathway!=undefined){
                if(pathway.values==undefined)
                        pathway.values=[];

                if(pathway.values.indexOf(node)==-1)
                    pathway.values.push(node);
            }
        }
        _metExploreViz.getSessionById("viz").getD3Data().getLinks()
            .forEach(function(d){
                var source = d.source;
                var target = d.target;
                if(source.getBiologicalType()=="reaction"){
                    source.getPathways()
                        .forEach(function(pathway){

                            addNodeInGroup(
                                source, 
                                pathwayGroup
                                    .find(function(pathw)
                                    {
                                        return pathw.key==pathway;
                                    }
                                )
                            );
                            addNodeInGroup(
                                target, 
                                pathwayGroup
                                    .find(function(pathw)
                                    {
                                        return pathw.key==pathway;
                                    }
                                )
                            );
                        }
                    );
                }
                else
                {
                    target.getPathways()
                        .forEach(function(pathway){

                            addNodeInGroup(
                                source, 
                                pathwayGroup
                                    .find(function(pathw)
                                    {
                                        return pathw.key==pathway;
                                    }
                                )
                            );
                            addNodeInGroup(
                                target, 
                                pathwayGroup
                                    .find(function(pathw)
                                    {
                                        return pathw.key==pathway;
                                    }
                                )
                            );
                        }
                    );
                }
            });
        
        return pathwayGroup;
    },
    sortPathways : function(){
        _metExploreViz.getSessionById("viz").getD3Data().sortPathways();
    },
    getPathwaysLength : function(){
        return _metExploreViz.getSessionById("viz").getD3Data().getPathwaysLength();
    },

    // Scale
    setScale : function(store, panel){
        _metExploreViz.getSessionById(panel).setScale(store);
    },
    getScaleById : function(panel){
        return _metExploreViz.getSessionById(panel).getScale();
    },
    

    // Metabolite
    setMetabolitesSet : function(store){
        Ext.getStore("S_Metabolite") = store;
    },
    getMetabolitesSet : function(){
        return Ext.getStore("S_Metabolite");
    },
    getMetaboliteById : function(store, id){
        return store.getById(id);
    },
    

    // Reaction
    setReactionsSet : function(store){
        Ext.getStore("S_Reaction") = store;
    },
    getReactionsSet : function(){
        return Ext.getStore("S_Reaction");
    },
    getReactionById : function(store, id){
        return store.getById(id);
    },


    // ReactionStyle
    setReactionStyle : function(store){
        _metExploreViz.reactionStyle = store;
        metExploreD3.fireEvent("reactionStyleForm", "setReactionStyle");
    },
    getReactionStyle : function(){
        return _metExploreViz.reactionStyle;
        },

    getGeneralStyle : function(){
        return _metExploreViz.generalStyle;
    }, 
    setGeneralStyle : function(store){
        _metExploreViz.generalStyle = store;
        metExploreD3.fireEvent("generalStyleForm", "setGeneralStyle");
        metExploreD3.fireEvent("vizIdConvexHullMenu", "setGeneralStyle");
        metExploreD3.fireEvent("buttonImportToNetworkFromWebsite", "setGeneralStyle");
    },

    // MetaboliteStyle
    setMetaboliteStyle : function(store){
        _metExploreViz.metaboliteStyle = store;
        metExploreD3.fireEvent("metaboliteStyleForm", "setMetaboliteStyle");
    },
    getMetaboliteStyle : function(){
        return _metExploreViz.metaboliteStyle;
    },


    // LinkStyle
    setLinkStyle : function(store){
        _metExploreViz.linkStyle = store;
    },
    getLinkStyle : function(){
        return _metExploreViz.linkStyle;
    },


    // Condition
    setConditionsSet : function(store){
        Ext.getStore("S_Condition") = store;
    },
    getConditionsSet : function(){
        return Ext.getStore("S_Condition");
    },
    getConditionById : function(store, id){
        return store.getById(id);
    },
    getConditionsSetLength : function(store){
        return store.getCount();
    },


    getConditionsMapped : function(){
        return Ext.getCmp('selectConditionForm').lookupReference('selectCondition').lastValue;
    },


    // MappingInfo
    setMappingInfosSet : function(store){
        Ext.getStore("S_MappingInfo") = store;
    },
    getMappingInfosSet : function(){
        return Ext.getStore("S_MappingInfo");
    },
    getMappingInfoById : function(store, id){
        return store.getById(id);
    },
    findMappingInfo : function(mappingInfoStore, id, idMapping){
        return mappingInfoStore.findRecord(id, idMapping);
    },


    // ReactionMap
    newReactionMapStore : function(store){
        return Ext.create('Ext.data.Store',{
            fields : ['id','ec','name','reversible']
        });
    },
    addReactionMap : function(storeReactionMap, myid, myec, myname, myreversible){
        storeReactionMap.add({
            id: myid,
            ec: myec,
            name: myname,
            reversible: myreversible
        });
    },
    getReactionMapsSetLength : function(store){
        return store.getCount();
    },


    // Mapping selectionned by user
    getMappingSelection : function(){
        var combBoxSelectMappingVisu = Ext.getCmp('selectMappingVisu');
        return combBoxSelectMappingVisu.getValue();
    },

    // Other function 
   
    /******************************************
    * Display the mask with the loading GIF 
    * @param {} mask : The mask to show
    */
    showMask : function(mask){
        mask.show();
    },
    /******************************************
    * Hide the mask
    * @param {} mask : The mask to hide
    */
    hideMask : function(mask){
        mask.hide();
    },
    /******************************************
    * Create a mask with the loading GIF 
    * @param {} label : The mask label
    * @param {} component : The panel where is displayed the mask
    */
    createLoadMask : function(label, component){
        if(component!='viz')
            var panelComponent = component.substring(0, component.length-5);
        else
            var panelComponent = component;
        if(panelComponent!= undefined){

            return new Ext.LoadMask({
                    target: Ext.getCmp(panelComponent), 
                    msg: label, 
                    msgCls:'msgClsCustomLoadMask'
                });
        }
        else{
            return undefined;
        }
    },


    /******************************************
    * Create a task 
    * @param {} func : The task function
    */
    createDelayedTask : function(func){
        return new Ext.util.DelayedTask(func);
    },
    /******************************************
    * Fix a delay to task 
    * @param {} task : The task to delay
    * @param {} time : The delay
    */
    fixDelay : function(task, time){
       task.delay(time);
    },
    /******************************************
    * Stop task 
    * @param {} task : The task to stop
    */
    stopTask : function(task){
       task.cancel();
    },

    /******************************************
    * Fire event with argument
    * @param {} cmp : View which received the event
    * @param {} task : Name of the event
    * @param {} arg : Argument for the event
    */
    fireEvent2Arg : function(cmp, name, arg1, arg2){
        var component = Ext.getCmp(cmp);
        if(component!= undefined){
            component.fireEvent(name, arg1, arg2);
        }
    },

    /******************************************
    * Fire event with argument
    * @param {} cmp : View which received the event
    * @param {} task : Name of the event
    * @param {} arg : Argument for the event
    */
    fireEventArg : function(cmp, name, arg){
        var component = Ext.getCmp(cmp);
        if(component!= undefined){
            component.fireEvent(name, arg);
        }
    },

    /******************************************
    * Fire Event
    * @param {} cmp : View which received the event
    * @param {} task : Name of the event
    */
    fireEvent : function(cmp, name){
        var component = Ext.getCmp(cmp);
        if(component!= undefined){
            component.fireEvent(name);
        }
    },

     /******************************************
    * Fire Event 
    * @param {} cmp : View which received the event
    * @param {} task : Name of the event
    */
    hideInitialMask : function(data){
        var component = Ext.getCmp("buttonImportToNetworkFromWebsite");
        if(component!= undefined){
            component.fireEvent("hideMask");
        }
    },


    /******************************************
    * Fire Event 
    * @param {} cmp : View which received the event
    * @param {} task : Name of the event
    */
    hideInitialLoadButtons : function(data){
        var component = Ext.getCmp("buttonImportToNetworkFromWebsite");
        if(component!= undefined){
            component.fireEvent("hideInitialLoadButtons");
        }
    },

    /******************************************
    * Fire Event 
    * @param {} cmp : View which received the event
    * @param {} task : Name of the event
    */
    cartFilled : function(data){
        var component = Ext.getCmp("buttonImportToNetworkFromWebsite");
        if(component!= undefined){
            component.fireEvent("cartFilled");
        }
        component = Ext.getCmp("viz_LoadMenu");
        if(component!= undefined){
            component.fireEvent("cartFilled");
        }
        _metExploreViz.setDataFromWebSite(data);
    },

    /******************************************
    * Fire Event
    * @param {} cmp : View which received the event
    * @param {} task : Name of the event
    */
    fireEventParentWebSite : function(myEvent, arg){
        var theEvent = new Event(myEvent, arg);
        theEvent.value = arg;
        _metExploreViz.getParentWebSite().document.dispatchEvent(theEvent);
    },

    /******************************************
    * Display message 
    * @param {} type : Message type
    * @param {} msg : Message to display
    */
    displayMessage : function(type, msg){
       Ext.Msg.alert(type, msg);
    },

    /******************************************
    * Display message 
    * @param {} type : Message type
    * @param {} msg : Message to display
    */
    displayWarning : function(msgTitle, msg){
        Ext.Msg.show({
           title:msgTitle,
           msg: msg,
           buttons: Ext.Msg.OK,
           icon: Ext.Msg.ERROR
       });
    },

    /******************************************
    * Display message question Ok
    * @param {} type : Message type
    * @param {} msg : Message to display
    */
    displayMessageOK : function(msgTitle, msg, fct){
       
        Ext.Msg.show({
           title:msgTitle,
           msg: msg,
           buttons: Ext.Msg.OKCANCEL,
           fn: fct,
           icon: Ext.Msg.QUESTION
       });
    },

    /******************************************
    * Display message question Yes No
    * @param {} type : Message type
    * @param {} msg : Message to display
    */
    displayMessageYesNo : function(msgTitle, msg, fct){
       
        Ext.Msg.confirm(msgTitle, msg, fct);
    },
    /******************************************
    * Defer function 
    * @param {} func : The function to defer
    * @param {} time : The delay
    */
    deferFunction : function(func, time){
        return new Ext.defer(func, time);
    },

    launchMetexploreFunction:function(func) {
        if (_metExploreViz.getSessionById('viz') !== 'undefined') {
            if (typeof _metExploreViz.getSessionById('viz').getForce() !== 'undefined') {
               // the variable is defined
               func();
               return;
            }
        }
        setTimeout(function(){metExploreD3.launchMetexploreFunction(func);}, 1000);
    },

    onloadSession : function(func){
        metExploreD3.launchMetexploreFunction(func);
    },

    launchMetexploreMapping:function(mappingName, func) {
        if(_metExploreViz.getMappingByName(mappingName) != null){
           // the variable is defined
           func();
           return;
        }
        setTimeout(function(){metExploreD3.launchMetexploreMapping(mappingName, func);}, 1000);
    },

    onloadMapping : function(mappingName, func){
        metExploreD3.launchMetexploreMapping(mappingName, func);
    }
};

var _metExploreViz;
var metExploreViz = function(panel, webSite){
    _metExploreViz = this;

    // Global variables 
    this.sessions = {};

    this.launched = false;
    this.dataFromWebSite = null;
    this.panel = panel;
    this.linkStyle = new LinkStyle(25, 2, 5, 5, 'red', 'green', 'black', '0.7', 'black');
    this.reactionStyle = new ReactionStyle(10, 20, 3, 3, 'ec', 8, 'black', 1);
    this.metaboliteStyle = new MetaboliteStyle(10, 10, 5, 5, 6, 1,'name', '#b2ae92');
    this.generalStyle = new GeneralStyle("Website", "yellow", "blue", 500, false, false, false, false, false);
    this.initialData = undefined;
    
    this.comparedPanels = [];
    this.mappings = [];
    this.linkedByTypeOfMetabolite = false;
    this.parentWebSite = webSite;
    this.oldCoodinates = [];

    // Dispatch the event.
    metExploreD3.fireEventArg('networkPanel', "afterlunch", panel);
    this.generalStyle.setWindowsAlertDisable(true);
};

metExploreViz.prototype = {

    getDataFromWebSite : function(){
        return this.dataFromWebSite;
    },
    setDataFromWebSite : function(data){
        this.dataFromWebSite = data;
    },

    getParentWebSite : function(){
        return this.parentWebSite;
    },
    cloneNetworkData : function(networkData){
        var newData = new NetworkData();
       
        var n, name, comp, dbId, ec, id, rev, sc, bt, sel, lv, svg, svgW, svgH;

        for (var j=0; j<networkData.nodes.length; j++) {
            n = networkData.nodes[j];
            if(n.getName()!=undefined)
                name = n.getName().valueOf();
            else
                name = undefined;
            
            if(n.getCompartment()!=undefined)
                comp = n.getCompartment().valueOf();
            else
                comp = undefined;
            
            if(n.getDbIdentifier()!=undefined)
                dbId = n.getDbIdentifier().valueOf();
            else
                dbId = undefined;
            
            if(n.getEC()!=undefined)
                ec = n.getEC().valueOf();
            else
                ec = undefined;
            
            if(n.getId()!=undefined)
                id = n.getId().valueOf();
            else
                id = undefined;

            if(n.getReactionReversibility()!=undefined && n.getBiologicalType()=="reaction")
                rev = n.getReactionReversibility().valueOf();
            else
                rev = undefined;
            
            if(n.getIsSideCompound()!=undefined)
                sc = n.getIsSideCompound().valueOf();
            else
                sc = undefined;
            
            if(n.getBiologicalType()!=undefined)
                bt = n.getBiologicalType().valueOf();
            else
                bt = undefined;

            if(n.isSelected()!=undefined)
                sel = n.isSelected().valueOf();
            else
                sel = undefined;

            if(n.getLabelVisible()!=undefined)
                lv = n.getLabelVisible().valueOf();
            else
                lv = undefined;

            if(n.getSvg()!=undefined)
                svg = n.getSvg().valueOf();
            else
                svg = undefined;

            if(n.getSvgWidth()!=undefined)
                svgW = n.getSvgWidth().valueOf();
            else
                svgW = undefined;

            if(n.getSvgHeight()!=undefined)
                svgH = n.getSvgHeight().valueOf();
            else
                svgH = undefined;

            newData.addNode(name,comp,dbId,id,rev,bt,sel,lv,svg,svgW,svgH,sc,ec);
        }

        for (var j=0; j<networkData.links.length; j++) {

            var id = networkData.links[j].getId().valueOf(); 
            var src = networkData.links[j].getSource();
            var source = newData.nodes[src];
            
            var tgt = networkData.links[j].getTarget();
            var target = newData.nodes[tgt];
       
            var interaction = networkData.links[j].getInteraction().valueOf();    
            var reversible = networkData.links[j].isReversible().valueOf();  
            
            newData.links[j] = new LinkData(id, source, target, interaction, reversible);
        }

        return newData;
    },
    
    cloneSession : function(){
        var mainSession = this.getSessionById('viz');
        var newSession = new NetworkVizSession();
        newSession.reset();
        
        var n, name, comp, dbId, ec, id, rev, sc, bt, sel, lv, svg, svgW, svgH;

        // for (var j=0; j<this.initialData.nodes.length; j++) {
        //     n = this.initialData.nodes[j];
        mainSession.getD3Data().getNodes().forEach(function(n){
            if(n.getName()!=undefined)
                name = n.getName().valueOf();
            else
                name = undefined;
            
            if(n.getCompartment()!=undefined)
                comp = n.getCompartment().valueOf();
            else
                comp = undefined;
            
            if(n.getDbIdentifier()!=undefined)
                dbId = n.getDbIdentifier().valueOf();
            else
                dbId = undefined;
            
            if(n.getEC()!=undefined)
                ec = n.getEC().valueOf();
            else
                ec = undefined;
            
            if(n.getId()!=undefined)
                id = n.getId().valueOf();
            else
                id = undefined;

            if(n.getReactionReversibility()!=undefined && n.getBiologicalType()=="reaction")
                rev = n.getReactionReversibility().valueOf();
            else
                rev = undefined;
            
            if(n.getIsSideCompound()!=undefined)
                sc = n.getIsSideCompound().valueOf();
            else
                sc = undefined;
            
            if(n.getBiologicalType()!=undefined)
                bt = n.getBiologicalType().valueOf();
            else
                bt = undefined;

            if(n.isSelected()!=undefined)
                sel = n.isSelected().valueOf();
            else
                sel = undefined;

            if(n.getLabelVisible()!=undefined)
                lv = n.getLabelVisible().valueOf();
            else
                lv = undefined;

            if(n.getSvg()!=undefined)
                svg = n.getSvg().valueOf();
            else
                svg = undefined;

            if(n.getSvgWidth()!=undefined)
                svgW = n.getSvgWidth().valueOf();
            else
                svgW = undefined;

            if(n.getSvgHeight()!=undefined)
                svgH = n.getSvgHeight().valueOf();
            else
                svgH = undefined;

            if(n.getIdentifier()!=undefined)
                identif = n.getIdentifier().valueOf();
            else
                identif = undefined;

            var isDuplicated = false;

            if(n.isDuplicated()!=undefined)
                isDuplicated = n.isDuplicated().valueOf();
            else
                isDuplicated = false;


            var node = newSession.d3Data.addNode(name,comp,dbId,id,rev,bt,sel,lv,svg,svgW,svgH,sc,ec,isDuplicated,identif);
        });

        mainSession.getD3Data().getLinks().forEach(function(link){

            var id = link.getId().valueOf(); 

            var src = link.getSource();
            var source = newSession.d3Data.nodes[mainSession.getD3Data().getNodes().indexOf(src)];
            
            var tgt = link.getTarget();
            var target = newSession.d3Data.nodes[mainSession.getD3Data().getNodes().indexOf(tgt)];
       
            var interaction = link.getInteraction().valueOf();    
            var reversible = link.isReversible().valueOf();  
            
            newSession.d3Data.addLink(id, source, target, interaction, reversible);
        });

        return newSession;
    },
    
    getGeneralStyle : function(){
        return this.generalStyle;
    },
    getMetaboliteStyle : function(){
        return this.metaboliteStyle;
    },

    //NetworkVizSession
    addSession : function(store){
        this.sessions[store.getId()] = store;
    },
    getSessionsSet : function(){
        return this.sessions;
    },
    getSessionById : function(panel){
        return this.sessions[panel];
    },
    getSessionsLength : function(){
        return this.sessions.length;
    },
    removeSession : function(panel){
        if(this.sessions[panel]!=undefined)
        {
            delete this.sessions[panel];    
        }
    },


    getInitialData:function()
    {
       return this.initialData;
    },    
    setInitialData:function(initialData)
    {
       this.initialData = initialData;
    },
    
    isLaunched :function(){
        return this.launched;
    },
    setLaunched : function(bool){
        this.launched = bool;
    },

    addComparedPanel : function(aComparedPanel){
        this.comparedPanels.push(aComparedPanel);
    },
    removeComparedPanel : function(aComparedPanel){
        var found=false;
        var i=0;
        while(!found)
        {
            if(this.comparedPanels[i].getPanel()==aComparedPanel.getPanel())
            {
                this.comparedPanels.splice(i,1);
                found=true;        
            }
            i++;
        }
    },
    getComparedPanelsLength : function(){
        return this.comparedPanels.length;
    },
    getComparedPanelById : function(id){
        var theComparedPanel = null;
        this.comparedPanels.forEach(function(aComparedPanel){            
            if(aComparedPanel.getPanel()==id)
                theComparedPanel = aComparedPanel;
        });
        return theComparedPanel;
    },

    // Mapping
    getOldCoodinates : function(){
        return this.oldCoodinates;
    },
    addOldCoodinates : function(coord){
        this.oldCoodinates.push(coord);
    },
    resetOldCoodinates : function(){
        this.oldCoodinates = [];
    },

    // Mapping
    getMappingsSet : function(){
        return this.mappings;
    },
    addMapping : function(aMapping){
        if(this.getMappingByName(aMapping.getName())!=null){
            aMapping.setName(aMapping.getName()+"I");
            this.addMapping(aMapping);
        }
        else
            this.mappings.push(aMapping);
    },
    resetMappings : function(aMapping){
        this.mappings = [];
        _metExploreViz.getSessionById("viz").getD3Data().resetMapping();
    },
    removeMapping : function(aMapping){
        var found=false;
        var i=0;
        while(!found && i<this.mappings.length)
        {
            if(this.mappings[i].getName()==aMapping)
            {
                this.mappings.splice(i,1);
                found=true;        
            }
            i++;
        }
    },
    getMappingsLength : function(){
        return this.mappings.length;
    },
    getMappingByName : function(name){
        var themapping = null;
        this.mappings.forEach(function(aMapping){            
            if(aMapping.getName()==name)
                themapping = aMapping;
        });
        return themapping;
    },

    isLinkedByTypeOfMetabolite : function(){
        return this.linkedByTypeOfMetabolite;
    },
    setLinkedByTypeOfMetabolite : function(bool){
        this.linkedByTypeOfMetabolite = bool;
    }

};
