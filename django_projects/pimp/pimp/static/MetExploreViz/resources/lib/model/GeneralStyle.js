
/**
 * @author MC
 * @description 
 */
 /**
 * General style
 */
var GeneralStyle = function(siteName, minContinuous, maxContinuous, max, dispLabel, dispLink, dispConvexhull, clust, dispCaption, eventForNodeInfo, loadButtonHidden, windowsAlertDisable){
    this.websiteName = siteName;
    this.colorMinMappingContinuous = minContinuous;
    this.colorMaxMappingContinuous = maxContinuous;
    this.maxReactionThreshold = max;
    this.displayLabelsForOpt = dispLabel;
    this.displayLinksForOpt = dispLink;
    this.displayConvexhulls = dispConvexhull;
    this.displayCaption = dispCaption;
    this.eventForNodeInfo=eventForNodeInfo;
    this.loadButtonHidden=false;
    this.windowsAlertDisable=false;
    this.clustered=clust;
};

GeneralStyle.prototype = {
    loadButtonIsHidden:function(){
        return this.loadButtonHidden;
    },
    setLoadButtonIsHidden:function(bool){
        this.loadButtonHidden = bool;
        metExploreD3.fireEvent("graphPanel", "setLoadButtonHidden");
    },
    windowsAlertIsDisable:function(){
        return this.windowsAlertDisable;
    },
    setWindowsAlertDisable:function(bool){
        this.windowsAlertDisable = bool;
    },
    // Getters & Setters
    getColorMinMappingContinuous:function()
    {
      return this.colorMinMappingContinuous;
    },
    getColorMaxMappingContinuous:function()
    {
      return this.colorMaxMappingContinuous;
    },

    setMaxColorMappingContinuous:function(newColor)
    {
      this.colorMaxMappingContinuous = newColor;
    },

    setMinColorMappingContinuous:function(newColor)
    {
      this.colorMinMappingContinuous = newColor;
    },

    getWebsiteName:function(){return this.websiteName;},
   
//If there are less than this number of reactions in the store, then different graph components are displayed.
    getReactionThreshold:function(){return this.maxReactionThreshold;},
    setReactionThreshold:function(maxReaction){this.maxReactionThreshold = maxReaction;},

    hasEventForNodeInfo:function(){return this.eventForNodeInfo;},
    setEventForNodeInfo:function(bool){this.eventForNodeInfo = bool;},

    isDisplayedLabelsForOpt:function(){return this.displayLabelsForOpt;},
    setDisplayLabelsForOpt:function(dispLabel){this.displayLabelsForOpt = dispLabel;},

    isDisplayedLinksForOpt:function(){return this.displayLinksForOpt;},
    setDisplayLinksForOpt:function(dispLink){this.displayLinksForOpt = dispLink;},

    isDisplayedConvexhulls:function(){return this.displayConvexhulls;},
    setDisplayConvexhulls:function(dispConvexhull){this.displayConvexhulls = dispConvexhull;},
 
    isDisplayedCaption:function(){return this.displayCaption;},
    setDisplayCaption:function(dispCaption){this.displayCaption = dispCaption;},
 
    useClusters:function(){return this.clustered;},
    setUseClusters:function(bool){this.clustered = bool;}
};