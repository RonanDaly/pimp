/**
 * @author MC
 * @description 
 */
 /**
 * Scale
 */
var Scale = function(graphName){
   this.graphName = graphName;
};

Scale.prototype = {
 
    // Getters & Setters
    setScale:function(newxScale, newyScale, newzoomScale, newxScaleCompare, newyScaleCompare, newzoomScaleCompare, newzoom)
    {
        this.xScale = newxScale;
        this.yScale = newyScale;
        this.zoomScale = newzoomScale;
        this.xScaleCompare = newxScaleCompare;
        this.yScaleCompare = newyScaleCompare;
        this.zoomScaleCompare = newzoomScaleCompare;
        this.zoom = newzoom;
    },

    getGraphName:function()
    {
      return this.graphName;
    },

    setGraphName:function(newData)
    {
      this.graphName = newData;
    },

    getXScale:function()
    {
      return this.xScale;
    },

    setXScale:function(newData)
    {
      this.xScale = newData;
    },

    getYScale:function()
    {
      return this.yScale;
    },

    setYScale:function(newData)
    {
      this.yScale = newData;
    },

    getZoomScale:function()
    {
      return this.zoomScale;
    },

    setZoomScale:function(newData)
    {
      this.zoomScale = newData;
    },
    getXScaleCompare:function()
    {
      return this.xScaleCompare;
    },

    setXScaleCompare:function(newData)
    {
      this.xScaleCompare = newData;
    },

    getYScaleCompare:function()
    {
      return this.yScaleCompare;
    },

    setYScaleCompare:function(newData)
    {
      this.yScaleCompare = newData;
    },

    getZoomScaleCompare:function()
    {
      return this.zoomScaleCompare;
    },

    setZoomScaleCompare:function(newData)
    {
      this.zoomScaleCompare = newData;
    },
    getZoom:function()
    {
      return this.zoom;
    },

    setZoom:function(newData)
    {
      this.zoom = newData;
    }
};