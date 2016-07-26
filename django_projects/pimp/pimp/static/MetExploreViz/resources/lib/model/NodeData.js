/**
 * NodeData class
 * For now, only contains the id
 */
var NodeData = function(name, compart, dbIdentifier, ec, id, reactionReversibility, isSideCompound, biologicalType, isSelected, labelVisible, svg, svgWidth, svgHeight, mappings, isDuplicated, identifier, pathW) {
        this.name=name;
        this.dbIdentifier = dbIdentifier ;
        this.ec = ec;
        this.id = id;  
        this.identifier = identifier;   
               
        this.reactionReversibility = reactionReversibility;
        this.isSideCompound = isSideCompound;
          //a reaction or a metabolite...later a gene?
        this.biologicalType = biologicalType;
        this.selected = isSelected;
        this.duplicated = isDuplicated;
        this.labelVisible = labelVisible
        this.svg = svg;
        this.svgWidth = svgWidth;
        this.svgHeight = svgHeight;

        if(pathW==undefined)
            this.pathways =[];
        else
            this.pathways = pathW;

        this.compartment = compart;
        
        if(mappings==undefined)
            mappings=[];
        this.mappingDatas = mappings;
};


NodeData.prototype = {
    equals : function(x){
    	var equal=true;
      if(this.id!=x.id)
        {equal=false;}
      return equal;
    },

    toString :function(){
      return this.id;
    },

    isSelected :function(){
      return this.selected;
    },

    setIsSelected : function(b){
      this.selected = b;
    },

    isDuplicated :function(){
      return this.duplicated;
    },

    setIsDuplicated : function(b){
      this.duplicated = b;
    },

    getIsSideCompound : function(){
      return this.isSideCompound;
    },

    setIsSideCompound : function(b){
      this.isSideCompound = b;
    },

    getId:function()
    {
      return this.id;
    },

    getIdentifier:function()
    {
      return this.identifier;
    },

    getDbIdentifier:function()
    {
      return this.dbIdentifier;
    },

    getBiologicalType:function()
    {
      return this.biologicalType;
    },

    getLabelVisible:function()
    {
      return this.labelVisible;
    },

    getReactionReversibility:function()
    {
      return this.reactionReversibility;
    },

    getName:function()
    {
      return this.name;
    },

    getId:function()
    {
      return this.id;
    },

    getSvg:function()
    {
      return this.svg;
    },

    getSvgHeight:function()
    {
      return this.svgHeight;
    },

    getSvgWidth:function()
    {
      return this.svgWidth;
    },

    getCompartment:function()
    {
      return this.compartment;
    },
    getEC:function()
    {
      return this.ec;
    },
    
    resetMapping : function(){
        this.mappingDatas=[];
    },
    addMappingData : function(aMappingData){
        this.mappingDatas.push(aMappingData);
    },
    removeMappingData : function(mappingTitle){
        var mapDatasToRemove = [];
        this.mappingDatas.forEach(function(mapData){
            if(mapData.getMappingName()==mappingTitle)
            {
                mapDatasToRemove.push(mapData);
            }
        });
        mapDatasToRemove.forEach(function(mapDataToRemove){
            var i = mapDatasToRemove.indexOf(mapDataToRemove);
            if(i!=-1)
                mapDatasToRemove.splice(i, 1);
        })
    },
    getMappingDatasLength : function(){
        return this.mappingDatas.length;
    },
    getMappingDatas : function(){
        return this.mappingDatas;
    },
    getMappingDataByNameAndCond : function(name, cond){
        var themappingData = null;
        this.mappingDatas.forEach(function(aMappingData){            
            if(aMappingData.getMappingName()==name && aMappingData.getConditionName()==cond)
                themappingData = aMappingData;
        });
        return themappingData;
    },
    getPathways : function(){
        return this.pathways;
    },
    setPathways : function(pathw){
        this.pathways = pathw;
    },
    addPathway : function(pathw){
        if(this.pathways.indexOf(pathw)==-1)
            this.pathways.push(pathw);
    }
};