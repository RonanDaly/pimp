/**
 * @author MC
 * @description 
 */
 /**
* NetworkData class
* nodes is an array of Node objects
* link is an array of Link objects
*/
var NetworkData = function(id){
    this.id = id,
    this.nodes = [];
    this.links = [];
    this.compartments = [];
    this.pathways = [];
};

NetworkData.prototype = {
    resetMapping : function(){
        this.nodes.forEach(function(node){
            node.resetMapping();
        })
    },

    removeMapping : function(mappingTitle){
        this.nodes.forEach(function(node){
            node.removeMappingData(mappingTitle);
        })
    },

    initNodeIndex:function()
    {
        tabNodes = this.nodes;
        this.nodes.forEach(function(node){
            node.index = tabNodes.indexOf(node);
        })
    },
    getNodes:function()
    {
      return this.nodes;
    },

    setId:function(newId)
    {
       this.id = newId;
    },
        

    getId:function()
    {
       return this.id;
    }, 

    copyData:function(aData)
    {
      this.nodes = aData.getNodes();
      this.links = aData.getLinks();
    },
    getNodesLength:function()
    {
      return this.nodes.length;
    },

    getLinks:function()
    {
      return this.links;
    },

    getCompartments:function()
    {
      return this.compartments;
    },

    getCompartmentsLength:function()
    {
      return this.compartments.length;
    },
    
    getCompartmentByName: function(name){
        var allCompartments=[];
        allCompartments=this.compartments;
        //console.log(this.data.nodes);
        var comp;
        for(i=0;i<allCompartments.length;i++)
        {
            if(allCompartments[i].getName()==(name))
            {
                comp=allCompartments[i];
                return comp;
            }
        }
        return null;
        
    },

    sortCompartments:function()
    {
        this.compartments.sort(function (a, b) {
            if (a.name > b.name)
              return 1;
            if (a.name < b.name)
              return -1;
            // a doit être égale à b
            return 0;
        });
    },

    addCompartment:function(name){
      if(this.compartments == undefined)
        this.compartments = [];

      var object = new Compartment(this.compartments.length, name);
      this.compartments.push(object);
    },

    getPathways:function()
    {
      return this.pathways;
    },

    getPathwaysLength:function()
    {
      return this.pathways.length;
    },
    
    getPathwayByName: function(name){
        var allPathways=[];
        allPathways=this.pathways;
        //console.log(this.data.nodes);
        var comp;
        for(i=0;i<allPathways.length;i++)
        {
            if(allPathways[i]==(name))
            {
                comp=allPathways[i];
                return comp;
            }
        }
        return null;
        
    },

    sortPathways:function()
    {
        this.pathways.sort(function (a, b) {
            if (a > b)
              return 1;
            if (a < b)
              return -1;
            // a doit être égale à b
            return 0;
        });
    },

    addPathway:function(name){
      if(this.pathways == undefined)
        this.pathways = [];

      this.pathways.push(name);
    },

    containsNode: function(id)
    {
        var allNodes=[];
        var contains=false;
        allNodes=this.nodes;
        for(i=0;i<allNodes.length;i++)
        {
            if(allNodes[i].getId()==(id))
                {contains=true;break;}
        }
        return contains;
    },

    getNodeById: function(id){
        var allNodes=[];
        allNodes=this.nodes;
        //console.log(this.data.nodes);
        var node = undefined;
        for(i=0;i<allNodes.length;i++)
        {
           //  console.log(" id searched "+id);
           // console.log("node ",allNodes[i]);
           // console.log("node id ",allNodes[i].id);
            if(allNodes[i].getId()==(id))
                {node=allNodes[i];break;}
        }
        return node;
    },

    getNodeByName: function(name){
        var allNodes=[];
        allNodes=this.nodes;
        //console.log(this.data.nodes);
        var node = undefined;
        for(i=0;i<allNodes.length;i++)
        {
           //  console.log(" id searched "+id);
           // console.log("node ",allNodes[i]);
           // console.log("node id ",allNodes[i].id);
            if(allNodes[i].getName()==(name))
                {node=allNodes[i];break;}
        }
        return node;
    },

    getNodeByDbIdentifier: function(id){
        var allNodes=[];
        allNodes=this.nodes;
        //console.log(this.data.nodes);
        var node = undefined;
        for(i=0;i<allNodes.length;i++)
        {
           //  console.log(" id searched "+id);
           // console.log("node ",allNodes[i].getDbIdentifier());
           // console.log("id ",id);

            if(allNodes[i].getDbIdentifier()==(id))
                {node=allNodes[i];break;}
        }
        return node;
    },

    getNodeByMappedInchi: function(inchi){
        var allNodes=[];
        allNodes=this.nodes;
        //console.log(this.data.nodes);
        var nodes = allNodes.filter(function(node){
            return node.mappedInchi==(inchi);
        });
        
        if(nodes.length==0)
            nodes = undefined;

        return nodes;
    },
    getLinkById: function(id){
        var allLinks=[];
        allLinks=this.links;
        var link;
        for(i=0;i<allLinks.length;i++)
        {
            if(allLinks[i].getId()==(id))
                {link=allLinks[i];break;}
        }
        return link;
    },

    getNode: function(indice){
        return this.nodes[indice];
    },

    getLink: function(indice){
        return this.links[indice];
    },

    addLink:function(id,source,target,interaction,reversible){
      if(this.links == undefined)
        this.links = [];

      var object = new LinkData(id, source, target, interaction, reversible);
      this.links.push(object);
    },

    getDataNodes:function(){
        var nodes=[];

        this.nodes.forEach(function(node){
            nodes.push(node);
        });

        return nodes;
    },

    addNodeCopy:function(node){
         this.nodes.push(node);
    },
   
    addNode:function(name,compartment,dbIdentifier,id,reactionReversibility,biologicalType,selected,labelVisible,svg,svgWidth,svgHeight,isSideCompound,ec,isDuplicated, identifier, pathway){
        if(this.nodes == undefined)
            this.nodes = [];

        var object = new NodeData(name, compartment, dbIdentifier, ec, id, reactionReversibility, isSideCompound, biologicalType, selected, labelVisible, svg, svgWidth, svgHeight, undefined, isDuplicated, identifier, pathway);
        //console.log('ec '+ec);
        //console.log('ec '+object.getEC());
        this.nodes.push(object);
        return object;
    },
    
    //get the array of link adjacent to a node
    getAdjLink : function (node)
    {
    	var adjLink=[];
    	var cpt=0;
    	for(var i=0;i<this.links.length;i++)
    	{
    		var link = this.links[i];
    		var source=link.source;
    		var target=link.target;
    		if(node.id == source.id)
    		{
    			adjLink.push(link);
    		}
    		else
    		{
    		    if(node.id==target.id)
    			{
    				adjLink.push(link);
    			} 
    		} 
    	}
    	return adjLink;	
    },
    
    //remove link function
     removeLink : function (link){
			for(k=0;k<this.links.length;k++)
			{
			 	if(link.id == this.links[k].id)
			 	{this.links.splice(k, 1);}
			}
    },
    
    //remove node function
    removeNode : function (node){
    	//first, remove all the link adjacent to this node
    	//for(i=0;i if(s==this[i]) this.splice(i, 1);
    	var adjLink=this.getAdjLink(node);
    	
    	if(adjLink.length!=0)
    	{
    		for(var i=0;i<adjLink.length;i++)
    		{

    			//for(j=0;j<adjLink.length;j++){console.log('-'+adjLink[j].id);}
    			var link2remove=adjLink[i];
    			this.removeLink(link2remove);
    			//for(j=0;j<adjLink.length;j++){console.log('-'+adjLink[j].id);}
    		}
    		
    	}
    	for(var k=0;k<this.nodes.length;k++)
		{
		 	if(node.id == this.nodes[k].id)
		 	{this.nodes.splice(k, 1);}
		}
    },

    cloneObject : function(obj){
        var that = this;
        

        // if(obj.compartments==undefined)
        // {
           obj.links.forEach(function(link){
           that.addLink(link.id,
                        link.source,
                        link.target,
                        link.interaction, 
                        link.reversible);
            });

            obj.nodes.forEach(function(node){
                if(node.biologicalType=="reaction"){

                
                    that.addNode(node.name,
                        undefined, node.dbIdentifier,
                        node.id, node.reactionReversibility,
                        'reaction', false, true, undefined,
                        undefined, undefined,undefined,node.ec, false, undefined, node.pathways);
                }
                else
                {
                
                    that.addNode(node.name,
                        node.compartment, node.dbIdentifier,
                        node.id, undefined,
                        'metabolite', false, true, node.svg,
                        node.svgWidth, node.svgHeight,node.isSideCompound,undefined, node.duplicated, node.identifier, node.pathways);
                }
                if(node.mappingDatas!=undefined){
                    if(node.mappingDatas.length>0){
                        node.mappingDatas.forEach(function(mappingData){
                            var map = new MappingData(mappingData.node, mappingData.mappingName, mappingData.conditionName, mappingData.mapValue);
                            that.nodes[that.nodes.length-1].addMappingData(map);
                        });
                    }
                }

                that.nodes[that.nodes.length-1].x = node.x;
                that.nodes[that.nodes.length-1].y = node.y;
            });
    }
};