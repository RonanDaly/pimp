/**
 * Model to handle List of Mappings liste des mappings effectues
 * id : M<num>	<num> = numero du mapping
 * object : objet sur leque a ete fait le mapping (par defaut : Metabolite)
 * element : element sur lequel a ete fait le mapping (par defaut : dbIdentifier)
 * ListId : liste des id mysql qui ont ete mappes
 */

var Mapping = function(title, conditions, targetLabel, id){

	this.name = title;
	this.conditions = conditions;
	this.targetLabel = targetLabel;
	this.data = [];
	this.id = id;
};

Mapping.prototype = {
	getId : function(){
		return this.id;
	},
	setId : function(newid){
		this.id = newid;
	},

	getName : function(){
		return this.name;
	},

	setName : function(newName){
		this.name = newName;
	},

	getConditions : function(){
		return this.conditions;
	},
	
	getTargetLabel : function(){
		return this.targetLabel;
	},

	getConditionByName : function(name){
		var theCondition = null;
        this.comparedPanels.forEach(function(aCondition){            
            if(aCondition.name==name)
                theCondition = aCondition;
        });
        return theCondition;
	},

	addMap : function(map){
		this.data.push(map);
	},

	getData : function(){
		return this.data;
	}
};