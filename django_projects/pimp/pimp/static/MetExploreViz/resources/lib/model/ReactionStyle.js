/**
 * @author MC
 * @description 
 */
 /**
 * draw a reaction
 */
 
var ReactionStyle = function(height, width, rx, ry, displayNodeName, fontSize, strokeColor, strokeWidth){
    this.height = height;
    this.width = width;
    this.rx = rx;
    this.ry = ry;
    this.label = displayNodeName;
    this.strokeColor = strokeColor;
    this.fontSize = fontSize;
    this.strokeWidth = strokeWidth;
};

ReactionStyle.prototype = {
	// Getters & Setters
    getHeight:function()
    {
      return this.height;
    },

    setHeight:function(newData)
    {
      this.height = newData;
    },

    getStrokeWidth:function()
    {
      return this.strokeWidth;
    },

    setStrokeWidth:function(newData)
    {
      this.strokeWidth = newData;
    },

    getWidth:function()
    {
      return this.width;
    },

    setWidth:function(newData)
    {
      this.width = newData;
    },

    getRX:function()
    {
      return this.rx;
    },

    setRX:function(newData)
    {
      this.rx = newData;
    },

    getRY:function()
    {
      return this.ry;
    },

    setRY:function(newData)
    {
      this.ry = newData;
    },

    getStrokeColor:function()
    {
      return this.strokeColor;
    },

    setStrokeColor:function(newData)
    {
      this.strokeColor = newData;
    },
    getFontSize:function()
    {
      return this.fontSize;
    },
    setFontSize:function(newData)
    {
      this.fontSize = newData;
    },


    getLabel:function()
    {
      return this.label;
    },

    setLabel:function(newData)
    {
      this.label = newData;
    },

    getDisplayLabel:function(node, label)
    {
        var displayedLabel;
        switch(label) {
            case "ec":
                displayedLabel = node.getEC();
                break;
            case "name":
                displayedLabel = node.getName();
                break;
            case "dbIdentifier":
                displayedLabel = node.getDbIdentifier();
                break;
            default:
                displayedLabel = node.getName();
        }
        if(displayedLabel == undefined)
            displayedLabel = node.getName();
        
        return displayedLabel;
    }
};