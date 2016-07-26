/**
 * @author MC
 * @description : Drawing links
 */
metExploreD3.GraphLink = {
	
	link:"",
	panelParent:"",

	/**********************************************/
	// INIT FUNCTIONS
	/**********************************************/
	delayedInitialisation : function(parent) {
		metExploreD3.GraphLink.panelParent = parent;
	},

	funcPath1 : function(link, panel){
		var source, target, path;

		function pathForReversibleReactions(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var rTW = (Math.abs(d)*reactionStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*reactionStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			else
			{
				var rTW = (Math.abs(d)*metaboliteStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*metaboliteStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			
			var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
			var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xWBaseArrowT = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT = yBaseArrowT - dX*(3/d);

			var xBaseArrowS = source.x + dX*(1-(d-largeurNoeudS-heightArrow)/d);
			var yBaseArrowS = source.y + dY*(1-(d-largeurNoeudS-heightArrow)/d);

			var xWBaseArrowS = xBaseArrowS - dY*(3/d);
			var yWBaseArrowS = yBaseArrowS + dX*(3/d);
			return "M"+xSource+","+ySource+"L"+xTarget+","+yTarget+"L"+xWBaseArrowT+","+yWBaseArrowT+"L"+xBaseArrowT+","+yBaseArrowT+"L"+xSource+","+ySource+"L"+xWBaseArrowS+","+yWBaseArrowS+"L"+xBaseArrowS+","+yBaseArrowS+"Z";
		}

		function path(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var largeurNoeudT = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
				var largeurNoeudS = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
			}
			else
			{
				var largeurNoeudT = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
				var largeurNoeudS = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
			}

			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrow = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrow = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xWBaseArrow = xBaseArrow + dY*(3/d);
			var yWBaseArrow = yBaseArrow - dX*(3/d);
			return "M"+source.x+","+source.y+"L"+xTarget+","+yTarget+"L"+xWBaseArrow+","+yWBaseArrow+"L"+xBaseArrow+","+yBaseArrow+"Z";
		}

		

		if(link.getSource().x==undefined){
			var networkData=_metExploreViz.getSessionById(panel).getD3Data();
			var nodes = networkData.getNodes();

			source = nodes[link.getSource()];
			target = nodes[link.getTarget()];
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
		else
		{
			source = link.getSource();
			target = link.getTarget();
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
				
		return path;
	}, 

	funcPath2 : function(link, panel){
		var source, target, path;

		function pathForReversibleReactions(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var rTW = (Math.abs(d)*reactionStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*reactionStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			else
			{
				var rTW = (Math.abs(d)*metaboliteStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*metaboliteStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			
			var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
			var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

			var xBaseArrowS = source.x + dX*(1-(d-largeurNoeudS-heightArrow)/d);
			var yBaseArrowS = source.y + dY*(1-(d-largeurNoeudS-heightArrow)/d);

			var xWBaseArrowS1 = xBaseArrowS - dY*(3/d);
			var yWBaseArrowS1 = yBaseArrowS + dX*(3/d);
			var xWBaseArrowS2 = xBaseArrowS + dY*(3/d);
			var yWBaseArrowS2 = yBaseArrowS - dX*(3/d);

			return "M"+xSource+","+ySource+
					"L"+xWBaseArrowS1+","+yWBaseArrowS1+
					"L"+xBaseArrowS+","+yBaseArrowS+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xBaseArrowS+","+yBaseArrowS+
					"L"+xWBaseArrowS2+","+yWBaseArrowS2+
					"L"+xSource+","+ySource+
					"Z";
		}

		function path(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var largeurNoeudT = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
				var largeurNoeudS = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
			}
			else
			{
				var largeurNoeudT = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
				var largeurNoeudS = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
			}
			
			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

			
			return "M"+source.x+","+source.y+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"Z";
		}

		

		if(link.getSource().x==undefined){
			var networkData=_metExploreViz.getSessionById(panel).getD3Data();
			var nodes = networkData.getNodes();

			source = nodes[link.getSource()];
			target = nodes[link.getTarget()];
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
		else
		{
			source = link.getSource();
			target = link.getTarget();
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
				
		return path;
	},

	funcPath3 : function(link, panel){
		var source, target, path;

		function pathForReversibleReactions(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var rTW = (Math.abs(d)*reactionStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*reactionStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			else
			{
				var rTW = (Math.abs(d)*metaboliteStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*metaboliteStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			var heightArrow = 5;
			
			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xBaseArrowRev = source.x + dX*((d-largeurNoeudT-heightArrow-heightArrow)/d);
			var yBaseArrowRev = source.y + dY*((d-largeurNoeudT-heightArrow-heightArrow)/d);

			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

			return "M"+source.x+","+source.y+
					"L"+xBaseArrowRev+","+yBaseArrowRev+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowRev+","+yBaseArrowRev+
					"Z";
		}

		function path(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var rTW = (Math.abs(d)*reactionStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*reactionStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			else
			{
				var rTW = (Math.abs(d)*metaboliteStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*metaboliteStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			
			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

			
			return "M"+source.x+","+source.y+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"Z";
		}

		

		if(link.getSource().x==undefined){
			var networkData=_metExploreViz.getSessionById(panel).getD3Data();
			var nodes = networkData.getNodes();

			source = nodes[link.getSource()];
			target = nodes[link.getTarget()];
			if(source!=undefined && target!=undefined)
			{
				if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
				{
					if(source.getReactionReversibility()||target.getReactionReversibility())
						path = pathForReversibleReactions(source, target);
					else
						path = path(source, target);
				}
				else
				{
					path = "M0,0L0,0Z";
				}
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
		else
		{
			source = link.getSource();
			target = link.getTarget();
			if(source!=undefined && target!=undefined)
			{
				if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
				{
					if(source.getReactionReversibility()||target.getReactionReversibility())
						path = pathForReversibleReactions(source, target);
					else
						path = path(source, target);
				}
				else
				{
					path = "M0,0L0,0Z";
				}
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
				
		return path;
	},

	funcPath4 : function(link, panel){
		var source, target, path;

		function pathForReversibleReactions(source, target){

			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var largeurNoeudS = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;

				var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
				var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

				var heightArrow = 5;

				var xBaseArrowS = source.x + dX*(1-(d-largeurNoeudS-heightArrow)/d);
				var yBaseArrowS = source.y + dY*(1-(d-largeurNoeudS-heightArrow)/d);

				var xBaseArrowRev = source.x + dX*(1-(d-largeurNoeudS-heightArrow-heightArrow)/d);
				var yBaseArrowRev = source.y + dY*(1-(d-largeurNoeudS-heightArrow-heightArrow)/d);

				var xWBaseArrowS1 = xBaseArrowS - dY*(3/d);
				var yWBaseArrowS1 = yBaseArrowS + dX*(3/d);
				var xWBaseArrowS2 = xBaseArrowS + dY*(3/d);
				var yWBaseArrowS2 = yBaseArrowS - dX*(3/d);


				path = 
				// "M"+xWBaseArrowS1+","+yWBaseArrowS1+
				// 		"L"+xWBaseArrowS2+","+yWBaseArrowS2+
				// 		"L"+xSource+","+ySource+
				// 		"Z"+
						"M"+xBaseArrowRev+","+yBaseArrowRev+
						"L"+xWBaseArrowS1+","+yWBaseArrowS1+
						"L"+xWBaseArrowS2+","+yWBaseArrowS2+
						"L"+xSource+","+ySource+
						"L"+xWBaseArrowS1+","+yWBaseArrowS1+
						"L"+xWBaseArrowS2+","+yWBaseArrowS2+
						"L"+xBaseArrowRev+","+yBaseArrowRev+
						"L"+target.x+","+target.y+
						"Z";
			}
			else
			{
				var largeurNoeudS = (metaboliteStyle.getWidth()+metaboliteStyle.getHeight())/2/2;
				var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
				var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

				var heightArrow = 5;
				
				

				var xTarget = source.x + dX*((d-largeurNoeudS)/d);
				var yTarget = source.y + dY*((d-largeurNoeudS)/d);

				var heightArrow = 5;
				var xBaseArrowT = source.x + dX*((d-largeurNoeudS-heightArrow)/d);
				var yBaseArrowT = source.y + dY*((d-largeurNoeudS-heightArrow)/d);

				var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
				var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
				var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
				var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

				var xBaseArrowRev =  source.x + dX*((d-largeurNoeudS-heightArrow-heightArrow)/d);
				var yBaseArrowRev =  source.y + dY*((d-largeurNoeudS-heightArrow-heightArrow)/d);


				path = 
				// "M"+xWBaseArrowT1+","+yWBaseArrowT1+
				// 		"L"+xWBaseArrowT2+","+yWBaseArrowT2+
				// 		"L"+xBaseArrowRev+","+yBaseArrowRev+
				// 		"Z"+
						"M"+source.x+","+source.y+
						"L"+xBaseArrowRev+","+yBaseArrowRev+
						"L"+xWBaseArrowT1+","+yWBaseArrowT1+
						"L"+xWBaseArrowT2+","+yWBaseArrowT2+
						"L"+xTarget+","+yTarget+
						"L"+xWBaseArrowT1+","+yWBaseArrowT1+
						"L"+xWBaseArrowT2+","+yWBaseArrowT2+
						"L"+xBaseArrowRev+","+yBaseArrowRev+
						"Z";
			}	
			return path;

		}

		function path(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var largeurNoeudS = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
				
				var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
				var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

				var heightArrow = 5;

				var xPointeS = source.x + dX*(1-(d-largeurNoeudS-heightArrow)/d);
				var yPointeS = source.y + dY*(1-(d-largeurNoeudS-heightArrow)/d);

				var xWBaseArrowS1 = xSource - dY*(3/d);
				var yWBaseArrowS1 = ySource + dX*(3/d);
				var xWBaseArrowS2 = xSource + dY*(3/d);
				var yWBaseArrowS2 = ySource - dX*(3/d);

				return "M"+target.x+","+target.y+
						"L"+xPointeS+","+yPointeS+
						"L"+xWBaseArrowS1+","+yWBaseArrowS1+
						"L"+xSource+","+ySource+
						"L"+xWBaseArrowS2+","+yWBaseArrowS2+
						"L"+xPointeS+","+yPointeS+
						"Z";
			}
			else
			{
				var largeurNoeudS = (metaboliteStyle.getWidth()+metaboliteStyle.getHeight())/2/2;
				var xTarget = source.x + dX*((d-largeurNoeudS)/d);
				var yTarget = source.y + dY*((d-largeurNoeudS)/d);

				var heightArrow = 5;
				var xBaseArrowT = source.x + dX*((d-largeurNoeudS-heightArrow)/d);
				var yBaseArrowT = source.y + dY*((d-largeurNoeudS-heightArrow)/d);

				var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
				var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
				var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
				var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

				
				return "M"+source.x+","+source.y+
						"L"+xBaseArrowT+","+yBaseArrowT+
						"L"+xWBaseArrowT1+","+yWBaseArrowT1+
						"L"+xTarget+","+yTarget+
						"L"+xWBaseArrowT2+","+yWBaseArrowT2+
						"L"+xBaseArrowT+","+yBaseArrowT+
						"Z";
			}
			
			return path;
		}

		

		if(link.getSource().x==undefined){
			var networkData=_metExploreViz.getSessionById(panel).getD3Data();
			var nodes = networkData.getNodes();

			source = nodes[link.getSource()];
			target = nodes[link.getTarget()];
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}	
		}
		else
		{
			source = link.getSource();
			target = link.getTarget();
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}	
		}
				
		return path;
	}, 

	funcPath5 : function(link, panel){
		var source, target, path;

		function pathForReversibleReactions(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var rTW = (Math.abs(d)*reactionStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*reactionStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			else
			{
				var rTW = (Math.abs(d)*metaboliteStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*metaboliteStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			
			var largeurNoeudS = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;

			var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
			var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

			var heightArrow = 5;

			var xBaseArrowS = source.x + dX*(1-(d-largeurNoeudS-heightArrow)/d);
			var yBaseArrowS = source.y + dY*(1-(d-largeurNoeudS-heightArrow)/d);

			var xBaseArrowRevS = source.x + dX*(1-(d-largeurNoeudS-heightArrow-heightArrow)/d);
			var yBaseArrowRevS = source.y + dY*(1-(d-largeurNoeudS-heightArrow-heightArrow)/d);

			var xWBaseArrowS1 = xBaseArrowS - dY*(3/d);
			var yWBaseArrowS1 = yBaseArrowS + dX*(3/d);
			var xWBaseArrowS2 = xBaseArrowS + dY*(3/d);
			var yWBaseArrowS2 = yBaseArrowS - dX*(3/d);


			var xTarget = source.x + dX*((d-largeurNoeudS)/d);
			var yTarget = source.y + dY*((d-largeurNoeudS)/d);

			var xBaseArrowT = source.x + dX*((d-largeurNoeudS-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudS-heightArrow)/d);

			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

			var xBaseArrowRevT =  source.x + dX*((d-largeurNoeudS-heightArrow-heightArrow)/d);
			var yBaseArrowRevT =  source.y + dY*((d-largeurNoeudS-heightArrow-heightArrow)/d);


			return "M"+xSource+","+ySource+
					"L"+xWBaseArrowS1+","+yWBaseArrowS1+
					"L"+xWBaseArrowS2+","+yWBaseArrowS2+
					"M"+xBaseArrowRevT+","+yBaseArrowRevT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"M"+xBaseArrowRevS+","+yBaseArrowRevS+
					"L"+xWBaseArrowS1+","+yWBaseArrowS1+
					"L"+xWBaseArrowS2+","+yWBaseArrowS2+
					"L"+xSource+","+ySource+
					"L"+xWBaseArrowS1+","+yWBaseArrowS1+
					"L"+xWBaseArrowS2+","+yWBaseArrowS2+
					"L"+xBaseArrowRevS+","+yBaseArrowRevS+
					"L"+xBaseArrowRevT+","+yBaseArrowRevT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowRevT+","+yBaseArrowRevT+
					"Z";
		}

		function path(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var largeurNoeudT = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
				var largeurNoeudS = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
			}
			else
			{
				var largeurNoeudT = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
				var largeurNoeudS = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
			}
			var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
			var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);


			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);
			
			var xPointeS = source.x + dX*(1-(d-largeurNoeudS-heightArrow)/d);
			var yPointeS = source.y + dY*(1-(d-largeurNoeudS-heightArrow)/d);

			var xWBaseArrowS1 = xSource - dY*(3/d);
			var yWBaseArrowS1 = ySource + dX*(3/d);
			var xWBaseArrowS2 = xSource + dY*(3/d);
			var yWBaseArrowS2 = ySource - dX*(3/d);

			return "M"+xPointeS+","+yPointeS+
					"L"+xWBaseArrowS1+","+yWBaseArrowS1+
					"L"+xWBaseArrowS2+","+yWBaseArrowS2+
					"L"+xPointeS+","+yPointeS+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"Z";
		}

		

		if(link.getSource().x==undefined){
			var networkData=_metExploreViz.getSessionById(panel).getD3Data();
			var nodes = networkData.getNodes();

			source = nodes[link.getSource()];
			target = nodes[link.getTarget()];
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
		else
		{
			source = link.getSource();
			target = link.getTarget();
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
				
		return path;
	},

	funcPath6 : function(link, panel){
		var source, target, path;

		function pathForReversibleReactions(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var rTW = (Math.abs(d)*reactionStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*reactionStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			else
			{
				var rTW = (Math.abs(d)*metaboliteStyle.getWidth()/2)/Math.abs(dX);
				var rTH = (Math.abs(d)*metaboliteStyle.getHeight()/2)/Math.abs(dY);
				var largeurNoeudT = (rTW<rTH) ? rT=rTW : rt=rTH;
			}
			
			var xSource = source.x + dX*(1-(d-largeurNoeudS)/d);
			var ySource = source.y + dY*(1-(d-largeurNoeudS)/d);

			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

			var xBaseArrowS = source.x + dX*(1-(d-largeurNoeudS-heightArrow)/d);
			var yBaseArrowS = source.y + dY*(1-(d-largeurNoeudS-heightArrow)/d);

			var xWBaseArrowS1 = xBaseArrowS - dY*(3/d);
			var yWBaseArrowS1 = yBaseArrowS + dX*(3/d);
			var xWBaseArrowS2 = xBaseArrowS + dY*(3/d);
			var yWBaseArrowS2 = yBaseArrowS - dX*(3/d);

			return "M"+xSource+","+ySource+
					"L"+xWBaseArrowS1+","+yWBaseArrowS1+
					"L"+xWBaseArrowS2+","+yWBaseArrowS2+
					"M"+xSource+","+ySource+
					"L"+xWBaseArrowS1+","+yWBaseArrowS1+
					"L"+xBaseArrowS+","+yBaseArrowS+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xBaseArrowS+","+yBaseArrowS+
					"L"+xWBaseArrowS2+","+yWBaseArrowS2+
					"L"+xSource+","+ySource+
					"Z";
		}

		function path(source, target){
			var metaboliteStyle = metExploreD3.getMetaboliteStyle();
			var reactionStyle = metExploreD3.getReactionStyle();
			var d = Math.sqrt(Math.pow(target.x - source.x,2) + Math.pow(target.y - source.y,2));
			var dX = (target.x-source.x);
			var dY = (target.y-source.y);
			var diffX = dX/Math.abs(dX);
			var diffY = dY/Math.abs(dY);
			
			if(source.getBiologicalType()=="metabolite"){
				var largeurNoeudT = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
				var largeurNoeudS = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
			}
			else
			{
				var largeurNoeudT = (metaboliteStyle.getHeight()+metaboliteStyle.getWidth())/2/2;
				var largeurNoeudS = (reactionStyle.getWidth()+reactionStyle.getHeight())/2/2;
			}
			
			var xTarget = source.x + dX*((d-largeurNoeudT)/d);
			var yTarget = source.y + dY*((d-largeurNoeudT)/d);

			var heightArrow = 5;
			var xBaseArrowT = source.x + dX*((d-largeurNoeudT-heightArrow)/d);
			var yBaseArrowT = source.y + dY*((d-largeurNoeudT-heightArrow)/d);

			var xWBaseArrowT1 = xBaseArrowT + dY*(3/d);
			var yWBaseArrowT1 = yBaseArrowT - dX*(3/d);
			var xWBaseArrowT2 = xBaseArrowT - dY*(3/d);
			var yWBaseArrowT2 = yBaseArrowT + dX*(3/d);

			
			return "M"+source.x+","+source.y+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"L"+xWBaseArrowT1+","+yWBaseArrowT1+
					"L"+xTarget+","+yTarget+
					"L"+xWBaseArrowT2+","+yWBaseArrowT2+
					"L"+xBaseArrowT+","+yBaseArrowT+
					"Z";
		}

		

		if(link.getSource().x==undefined){
			var networkData=_metExploreViz.getSessionById(panel).getD3Data();
			var nodes = networkData.getNodes();

			source = nodes[link.getSource()];
			target = nodes[link.getTarget()];
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
		else
		{
			source = link.getSource();
			target = link.getTarget();
			if(source.x!=undefined && source.y!=undefined && target.x!=undefined && target.y!=undefined)
			{
				if(source.getReactionReversibility()||target.getReactionReversibility())
					path = pathForReversibleReactions(source, target);
				else
					path = path(source, target);
			}
			else
			{
				path = "M0,0L0,0Z";
			}
		}
				
		return path;
	},


	/*******************************************
	* Init the visualization of links
	* @param {} parent : The panel where the action is launched
	* @param {} session : Store which contains global characteristics of session
	* @param {} linkStyle : Store which contains links style
	* @param {} metaboliteStyle : Store which contains metabolites style
	*/
	refreshLink : function(parent, session, linkStyle, metaboliteStyle) {
		metExploreD3.GraphLink.panelParent = "#"+parent; 
		var networkData=session.getD3Data();

		var size=20;
		// The y-axis coordinate of the reference point which is to be aligned exactly at the marker position.
		var refY = linkStyle.getMarkerWidth() / 2;
		// The x-axis coordinate of the reference point which is to be aligned exactly at the marker position.
		// var refX = linkStyle.getMarkerHeight / 2;

	  // Adding arrow on links
		// d3.select("#"+parent).select("#D3viz").select("#graphComponent").append("svg:defs").selectAll("marker")
		// 	.data(["in", "out"])
		// 	.enter().append("svg:marker")
		// 	.attr("id", String)
		// 	.attr("viewBox", "0 0 "+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight())
		// 	.attr("refY", refY)
		// 	.attr("markerWidth", linkStyle.getMarkerWidth())
		// 	.attr("markerHeight", linkStyle.getMarkerHeight())
		// 	.attr("orient", "auto")
		// 	.append("svg:path")
		// 	.attr("class", String)
		// 	.attr("d", "M0,0L"+linkStyle.getMarkerWidth()+","+linkStyle.getMarkerHeight()/2+"L0,"+linkStyle.getMarkerWidth()+"Z")
		// 	.style("visibility", "hidden");
			// .attr("d", "M"+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight()/2+" L"+linkStyle.getMarkerWidth()/2+" "+(3*linkStyle.getMarkerHeight()/4)+" A"+linkStyle.getMarkerHeight()+" "+linkStyle.getMarkerHeight()+" 0 0 0 "+linkStyle.getMarkerWidth()/2+" "+(1*linkStyle.getMarkerHeight()/4)+" L"+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight()/2+"Z")
		// Append link on panel
		metExploreD3.GraphLink.link=d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("path.link")
			.data(networkData.getLinks())
			.enter()
			.append("svg:path")
			.attr("class", String)
			.attr("d", function(link){return metExploreD3.GraphLink.funcPath3(link, parent);})
			.attr("class", "link")
			.attr("fill-rule", "evenodd")
			.attr("fill", function (d) {
				if (d.interaction=="out")
				 	return linkStyle.getMarkerOutColor();
				else
					return linkStyle.getMarkerInColor(); 
			})
			.style("stroke",linkStyle.getStrokeColor())
			.style("stroke-width",0.5)
			.style("stroke-linejoin", "bevel");
			 
	},

	reloadLinks : function(panel, networkData, linkStyle, metaboliteStyle){
		d3.select("#"+panel).select("#D3viz").select("#graphComponent").selectAll("path.link")
			.data(networkData.getLinks())
			.enter()
			.insert("path",":first-child")
			.attr("class", String)
			.attr("d", function(link){return metExploreD3.GraphLink.funcPath3(link, parent);})
			.attr("class", "link")
			.attr("fill-rule", "evenodd")
			.attr("fill", function (d) {
				if (d.interaction=="out")
				 	return linkStyle.getMarkerOutColor();
				else
					return linkStyle.getMarkerInColor(); 
			})
			.style("stroke",linkStyle.getStrokeColor())
			.style("stroke-width",0.5)
			.style("stroke-linejoin", "bevel");
			 

	},

	// A n'appliquer que sur les petits graphes
	linkTypeOfMetabolite : function(){
		_metExploreViz.setLinkedByTypeOfMetabolite(true);
		var panel = "viz";
		var session = _metExploreViz.getSessionById("viz");

		if(session!=undefined)  
		{
			// We stop the previous animation
			var force = session.getForce();
			if(force!=undefined)  
			{
				force.stop();
			}
		}

		var myMask = metExploreD3.createLoadMask("Link in progress...", panel);
		if(myMask!= undefined){
		  
		  	metExploreD3.showMask(myMask);

			metExploreD3.deferFunction(function() {
				// Hash table definition to create hidden edges
				// Hidden edges are created to put products next to products and substract next to substracts
				var src = {};
				var tgt = {};

				var reacSrc = {};
				var reacTgt = {};

				d3.select("#viz").select("#D3viz").select("#graphComponent")
					.selectAll("path.link")
					.filter(function(link){
						return link.getInteraction()!="hiddenForce";
					})
					.each(function(alink){
						if(alink.getInteraction()=='in'){
							if(src[alink.getTarget()]==null)
								src[alink.getTarget()]=[]

							src[alink.getTarget()][src[alink.getTarget()].length]=alink.getSource();

							if(reacTgt[alink.getSource()]==null)
								reacTgt[alink.getSource()]=[]
							
							reacTgt[alink.getSource()][reacTgt[alink.getSource()].length]=alink.getTarget();
						}
						else{
							if(tgt[alink.getSource()]==null)
								tgt[alink.getSource()]=[];
							tgt[alink.getSource()][tgt[alink.getSource()].length]=alink.getTarget();

							if(reacSrc[alink.getTarget()]==null)
								reacSrc[alink.getTarget()]=[];
							reacSrc[alink.getTarget()][reacSrc[alink.getTarget()].length]=alink.getSource();

						}
				});

				for (var key in src) {    
					var i = -1;        
					src[key].forEach(function(reactantX1){
						i++;
						src[key].forEach(function(reactantX2){
							if(reactantX1!=reactantX2 && reactantX1!=undefined){
								metExploreD3.GraphLink.addHiddenLinkInDrawing(reactantX1+" -- "+reactantX2,reactantX1,reactantX2,'viz');
							}
						 })
						 delete src[key][i];
					})
				}

				  for (var key in tgt) {    
					  var i = -1;        
					  tgt[key].forEach(function(produitX1){
						  i++;
						  tgt[key].forEach(function(produitX2){
							  if(produitX1!=produitX2 && produitX1!=undefined){
								  metExploreD3.GraphLink.addHiddenLinkInDrawing(produitX1+" -- "+produitX2,produitX1,produitX2,'viz');
							  }
						  })
						  delete tgt[key][i];
					  })
				  }

				  for (var key in reacSrc) {    
					  var i = -1;        
					  reacSrc[key].forEach(function(reactantX1){
						  i++;
						  reacSrc[key].forEach(function(reactantX2){
							  if(reactantX1!=reactantX2 && reactantX1!=undefined){
								  metExploreD3.GraphLink.addHiddenLinkInDrawing(reactantX1+" -- "+reactantX2,reactantX1,reactantX2,'viz');
							  }
						  })
						  delete reacSrc[key][i];
					  })
				  }

				  for (var key in reacTgt) {    
					  var i = -1;        
					  reacTgt[key].forEach(function(produitX1){
						  i++;
						  reacTgt[key].forEach(function(produitX2){
							  if(produitX1!=produitX2 && produitX1!=undefined){
								  metExploreD3.GraphLink.addHiddenLinkInDrawing(produitX1+" -- "+produitX2,produitX1,produitX2,'viz');
							  }
						  })
						  delete reacTgt[key][i];
					  })
				  }
				metExploreD3.hideMask(myMask);
				var animLinked=metExploreD3.GraphNetwork.isAnimated(session.getId());
		  		if (animLinked=='true') {
					var force = session.getForce();
					if(force!=undefined)  
					{   
			  			if((metExploreD3.GraphNetwork.isAnimated(session.getId()) == 'true') 
							|| (metExploreD3.GraphNetwork.isAnimated(session.getId()) == null)) {
				  				force.start();
			  			}
			  		}
			  	}
			}, 100);
		}			
	},

	// A n'appliquer que sur les petits graphes
	removeLinkTypeOfMetabolite : function(){
		_metExploreViz.setLinkedByTypeOfMetabolite(false);
		var panel = "viz";
		var session = _metExploreViz.getSessionById("viz");

		if(session!=undefined)  
		{
			// We stop the previous animation
			var force = session.getForce();
			if(force!=undefined)  
			{
				force.stop();
			}
		}

		var myMask = metExploreD3.createLoadMask("Remove hidden link in progress...", panel);
		if(myMask!= undefined){
		  
		  	metExploreD3.showMask(myMask);

			metExploreD3.deferFunction(function() {
				metExploreD3.GraphLink.removeHiddenLinkInDrawing('viz');
					
				metExploreD3.hideMask(myMask);
				var animLinked=metExploreD3.GraphNetwork.isAnimated(session.getId());
		  		if (animLinked=='true') {
					var force = session.getForce();
					if(force!=undefined)  
					{   
			  			if((metExploreD3.GraphNetwork.isAnimated(session.getId()) == 'true') 
							|| (metExploreD3.GraphNetwork.isAnimated(session.getId()) == null)) {
				  				force.start();
			  			}
			  		}
			  	}
			}, 100);
		}			
	},

	/*******************************************
	* Add link in visualization
	* @param {} identifier : Id of this link
	* @param {} source : Source of this link
	* @param {} target : Target of this link
	* @param {} interaction : Interaction beetween nodes of this link
	* @param {} reversible : Reversibility of link
	* @param {} panel : The panel where is the new link
	*/
	addHiddenLinkInDrawing:function(identifier,source,target,panel){
	  var session = _metExploreViz.getSessionById(panel);
	  var networkData = session.getD3Data();
	  networkData.addLink(identifier,source,target,"hiddenForce",false);
	  var metaboliteStyle = metExploreD3.getMetaboliteStyle();
	  var linkStyle = metExploreD3.getLinkStyle();
	  var force = session.getForce();

	  link=d3.select("#"+panel).select("#graphComponent").selectAll("path.link")
			.data(force.links(), function(d) { 
			  	return d.source.id + "-" + d.target.id;
			})
			.enter()
			.insert("path",":first-child")
			.attr("class", "link")//it comes from resources/css/networkViz.css
			.style("stroke",linkStyle.getStrokeColor())
			.style("opacity",0);
	},

	/*******************************************
	* Add link in visualization
	* @param {} identifier : Id of this link
	* @param {} source : Source of this link
	* @param {} target : Target of this link
	* @param {} interaction : Interaction beetween nodes of this link
	* @param {} reversible : Reversibility of link
	* @param {} panel : The panel where is the new link
	*/
	removeHiddenLinkInDrawing:function(panel){
		var session = _metExploreViz.getSessionById(panel);

		var networkData = session.getD3Data();
		var linksToRemove = [];
		var force = session.getForce();

		var link=d3.select("#"+panel).select("#graphComponent").selectAll("path.link")
			.filter(function(link){
				return link.getInteraction()=="hiddenForce";
			})
			.each(function(link){ linksToRemove.push(link); })
			.remove();
		
		setTimeout(
			function() {
				
				for (i = 0; i < linksToRemove.length; i++) {
					var link = linksToRemove[i];

					networkData.removeLink(link);

					var index = force.links().indexOf(link);
					
					if(index!=-1)
						force.links().splice(index, 1);
				}
			}
		, 100);
	},
	
	/*******************************************
	* Tick function of links
	* @param {} panel : The panel where the action is launched
	* @param {} scale = Ext.getStore('S_Scale').getStoreByGraphName(panel);
	*/
	tick : function(panel, scale) {
		  // If you want to use selection on compartments path
		d3.select("#"+metExploreD3.GraphNode.panelParent).select("#D3viz").selectAll("path")
			.filter(function(d){return $(this).attr('class')!="linkCaptionRev" && $(this).attr('class')!="link";})
		    .attr("d", metExploreD3.GraphNode.groupPath)
		    .attr("transform", d3.select("#"+panel).select("#D3viz").select("#graphComponent").attr("transform")); 
	  	d3.select("#"+panel).select("#D3viz").select("#graphComponent")
			.selectAll("path.link")
			.attr("d", function(link){return metExploreD3.GraphLink.funcPath3(link, panel);})
			.style("stroke-linejoin", "bevel");
	},

	displayConvexhulls : function(panel){

        	
		var generalStyle = _metExploreViz.getGeneralStyle();

		var convexHullPath = d3.select("#"+panel).select("#D3viz").selectAll("path")
		  .filter(function(d){return $(this).attr('class')!="linkCaptionRev" && $(this).attr('class')!="link";});


		var isDisplay = generalStyle.isDisplayedConvexhulls();

		if(!isDisplay){

			convexHullPath.remove();
	  	}
	  	else
	  	{
			if(convexHullPath[0].length==0)
				metExploreD3.GraphNode.loadPath(panel, isDisplay);  
				
	  		convexHullPath = d3.select("#"+panel).select("#D3viz").selectAll("path")
				.filter(function(d){return $(this).attr('class')!="linkCaptionRev" && $(this).attr('class')!="link";});

		  	convexHullPath
			  .attr("d", metExploreD3.GraphNode.groupPath)
			  .attr("transform", d3.select("#"+panel).select("#D3viz").select("#graphComponent").attr("transform")); 
	  	}
	}

	// /*******************************************
	// * Init the visualization of links
	// * @param {} parent : The panel where the action is launched
	// * @param {} session : Store which contains global characteristics of session
	// * @param {} linkStyle : Store which contains links style
	// * @param {} metaboliteStyle : Store which contains metabolites style
	// */
	// loadLink : function(parent, session, linkStyle, metaboliteStyle) {
		
	// 	metExploreD3.GraphLink.panelParent = "#"+parent; 
	// 	var networkData=session.getD3Data();

	// 	var size=20;
	// 	// The y-axis coordinate of the reference point which is to be aligned exactly at the marker position.
	// 	var refY = linkStyle.getMarkerWidth() / 2;
	// 	// The x-axis coordinate of the reference point which is to be aligned exactly at the marker position.
	// 	// var refX = linkStyle.getMarkerHeight / 2;

	//   // Adding arrow on links
	// 	d3.select("#"+parent).select("#D3viz").select("#graphComponent").append("svg:defs").selectAll("marker")
	// 		.data(["in", "out"])
	// 		.enter().append("svg:marker")
	// 		.attr("id", String)
	// 		.attr("viewBox", "0 0 "+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight())
	// 		.attr("refY", refY)
	// 		.attr("markerWidth", linkStyle.getMarkerWidth())
	// 		.attr("markerHeight", linkStyle.getMarkerHeight())
	// 		.attr("orient", "auto")
	// 		.append("svg:path")
	// 		.attr("class", String)
	// 		.attr("d", "M0,0L"+linkStyle.getMarkerWidth()+","+linkStyle.getMarkerHeight()/2+"L0,"+linkStyle.getMarkerWidth()+"Z")
	// 		.style("visibility", "hidden");

	// 		// .attr("d", "M"+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight()/2+" L"+linkStyle.getMarkerWidth()/2+" "+(3*linkStyle.getMarkerHeight()/4)+" A"+linkStyle.getMarkerHeight()+" "+linkStyle.getMarkerHeight()+" 0 0 0 "+linkStyle.getMarkerWidth()/2+" "+(1*linkStyle.getMarkerHeight()/4)+" L"+linkStyle.getMarkerWidth()+" "+linkStyle.getMarkerHeight()/2+"Z")
		
	   
	// 	// Append link on panel
	// 	metExploreD3.GraphLink.link=d3.select("#"+parent).select("#D3viz").select("#graphComponent").selectAll("path.link")
	// 		.data(networkData.getLinks())
	// 		.enter()
	// 		.append("path")
	// 		.attr("class", "link")//it comes from resources/css/networkViz.css
	// 		.attr("marker-end", function (d) {
	// 			if (d.interaction=="out")
	// 			{
	// 			   d3.select("#"+parent).select("#D3viz").select("#graphComponent").select("#" + d.interaction)
	// 				.attr("refX", (metaboliteStyle.getWidth()+metaboliteStyle.getHeight())/2/2  + (linkStyle.getMarkerWidth() ))
	// 				.style("fill", linkStyle.getMarkerOutColor())
	// 					.style("stroke",linkStyle.getMarkerStrokeColor())
	// 					.style("stroke-width",linkStyle.getMarkerStrokeWidth());

	// 			   return "url(#" + d.interaction + ")";
	// 			}
	// 			else
	// 			{
	// 			  return "none";             
	// 			}
				
	// 			})
	// 		.attr("marker-start", function (d) {
	// 			if (d.interaction=="out")
	// 			{
	// 			   return "none";
	// 			}
	// 			else
	// 			{
	// 			  d3.select("#"+parent).select("#D3viz").select("#graphComponent").select("#" + d.interaction)
	// 				.attr("refX",-((metaboliteStyle.getWidth()+metaboliteStyle.getHeight())/2/2 ))
	// 				.style("fill", linkStyle.getMarkerInColor())
	// 				.style("stroke",linkStyle.getMarkerStrokeColor())
	// 					.style("stroke-width",linkStyle.getMarkerStrokeWidth());

	// 			  return "url(#" + d.interaction + ")";              
	// 			}  
	// 			})
	// 		.style("stroke",linkStyle.getStrokeColor());

	// 	metExploreD3.GraphLink.link
	// 		.filter(function(link){
	// 			return link.getInteraction()=="hiddenForce";
	// 		})
	// 		.style("opacity",0);
	// }
}