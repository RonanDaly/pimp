/**
 * LinkData class
 * id : a String for the identifier of the Link
 * Contains a source Node
 * Contains a target Node
 * Boolean telling wether the Link is directed or not
 */

var LinkData = function(id, source, target, interaction, reversible){
    this.id = id;
    this.source = source;
    this.target = target; 
    this.interaction = interaction;
    this.reversible = reversible;
};

LinkData.prototype = {
    
    equals : function(x){
		if(this.id!=x.id)
			return false;
				
			return true;
	},

    isReversible :function(){
    return this.reversible;
    },

    // Getters & Setters
    getId:function(){
        return this.id;
    },
   
    setInteraction:function(inte){
        this.interaction = inte;
    },

    getInteraction:function(){
        return this.interaction;
    },

    getSource:function(){
        return this.source;
    },

    getTarget:function(){
        return this.target;
    },

    setSource:function(source){
        this.source = source;
    },

    setTarget:function(target){
        this.target = target;
    }
};