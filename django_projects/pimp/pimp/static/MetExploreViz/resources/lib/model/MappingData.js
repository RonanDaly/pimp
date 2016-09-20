var MappingData = function(node, titleMap, conditionN, val){

	this.node = node;
	this.mappingName = titleMap;
	this.conditionName = conditionN;
	this.mapValue = val;
};

MappingData.prototype = {
	getNode : function(){
		return this.node;
	},
	setNode : function(newNode){
		this.node = newNode;
	},
	
	getMappingName : function(){
		return this.mappingName;
	},

	getConditionName : function(){
		return this.conditionName;
	},
	
	getMapValue : function(){
		return this.mapValue;
	},
	setMapValue : function(val){
		this.mapValue = val;
	}
};