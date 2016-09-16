/**
 * @author MC
 * @description 
 */
 /**
 * draw a link
 */
var LinkStyle = function(size, lineWidth, markerWidth, markerHeight, markerInColor, markerOutColor, markerStrokeColor, markerStrokeWidth, strokeColor){
    this.size = size ;
    this.lineWidth = lineWidth;
    this.markerWidth = markerWidth;
    this.markerHeight = markerHeight;
    this.markerInColor = markerInColor;
    this.markerOutColor = markerOutColor;
    this.markerStrokeColor = markerStrokeColor;
    this.markerStrokeWidth = markerStrokeWidth;
    this.strokeColor = strokeColor;
};

LinkStyle.prototype = {
    // Getters & Setters
    getMarkerInColor:function()
    {
      return this.markerInColor;
    },

    getLineWidth:function()
    {
      return this.lineWidth;
    },

    getMarkerOutColor:function()
    {
      return this.markerOutColor;
    },

    getSize:function()
    {
      return this.size;
    },

    getMarkerWidth:function()
    {
      return this.markerWidth;
    },

    getMarkerStrokeWidth:function()
    {
      return this.markerStrokeWidth;
    },

    getMarkerHeight:function()
    {
      return this.markerHeight;
    },

    getMarkerStrokeColor:function()
    {
      return this.markerStrokeColor;
    },

    getStrokeColor:function()
    {
      return this.strokeColor;
    },

    setMarkerInColor:function(newData)
    {
      this.markerInColor = newData;
    },

    setLineWidth:function(newData)
    {
      this.lineWidth = newData;
    },

    setMarkerOutColor:function(newData)
    {
      this.markerOutColor = newData;
    },

    setSize:function(newData)
    {
      this.size =  newData;
    },

    setMarkerWidth:function(newData)
    {
      this.markerWidth = newData;
    }

    ,setMarkerStrokeWidth:function(newData)
    {
      this.markerStrokeWidth = newData;;
    },

    setMarkerHeight:function(newData)
    {
      this.markerHeight = newData;;
    },

    setMarkerStrokeColor:function(newData)
    {
      this.markerStrokeColor = newData;;
    },

    setStrokeColor:function(newData)
    {
      this.strokeColor = newData;;
    }
};