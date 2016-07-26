/**
 * @author MC
 * @description 
 */
 /**
 * ComparedPanel
 */
var ComparedPanel = function(panel, visible, parent, title){
    this.panel = panel;
    this.visible = visible;
    this.parent = parent;
    this.title = title;
};

ComparedPanel.prototype = {

    // Getters & Setters
    getPanel:function()
    {
      return this.panel;
    },

    setPanel:function(newData)
    {
      this.panel = newData;
    },

    isVisible:function()
    {
      return this.visible;
    },

    setVisible:function(newData)
    {
      this.visible = newData;
    },

    getParent:function()
    {
      return this.parent;
    },

    setParent:function(newData)
    {
      this.parent = newData;
    },

    getTitle:function()
    {
      return this.title;
    },

    setTitle:function(newData)
    {
      this.title = newData;
    }

};