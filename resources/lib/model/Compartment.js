var Compartment = function(id, name){
	this.id = id;
	this.identifier = name;
	this.name = name;
	this.color = "";
};

Compartment.prototype = {
		

   	getIdentifier:function()
    {
      return this.identifier;
    },
    getName:function()
    {
      return this.name;
  	},
    getColor:function()
    {
      return this.color;
    },
    setColor:function(newColor)
    {
      return this.color = newColor;
    }
};
