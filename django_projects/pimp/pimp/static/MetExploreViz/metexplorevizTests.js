

var MetExploreViz = {
    initFrame:function(panel){
		var iframe = document.createElement('iframe');
		// iframe.rel = "external",
		iframe.id = "iFrameMetExploreViz",
		iframe.height = '100%',
		iframe.width = '100%',
		iframe.border = 0,
		iframe.setAttribute("style", "border: none;top: 0; right: 0;bottom: 0; left: 0; width: 100%;height: 100%;");
		
		var scripts = document.getElementsByTagName("script");
		var libSrc;
		for (var i = 0; i < scripts.length; i++) {
			if (scripts[i].src.search("metexplorevizTests.js") != -1) {
				libSrc = scripts[i].src;
			}
		};
		var locationSrc = document.location.href;

		var index=0;
		while (libSrc[index]==locationSrc[index] 
				&& index != locationSrc.length 
					&& index != libSrc.length) {
		    index++;
		}

		libSrc = libSrc.split("/metexplorevizTests.js");

		res = locationSrc.substr(index, locationSrc.length-1);

		res = res.split('/');

		var headString = "";

		for (var i = 0; i < res.length-1; i++) {
			headString+="../"; 	
		};

		var source = headString + libSrc[0] + "/index.html";

		document.getElementById(panel).insertBefore(iframe, document.getElementById(panel).firstChild);
		iframe.src = source;
	},

	launchMetexploreFunction:function(func) {
        if (typeof metExploreViz !== 'undefined') {
           // the variable is defined
           func();
           return;
        }
        var that = this;
        setTimeout(function(){that.launchMetexploreFunction(func);}, 100);    },

    onloadMetExploreViz : function(func){
        this.launchMetexploreFunction(func);
    }
};