d3.selection.enter.prototype =

	d3.selection.prototype.addNodeForm = function(width, height, rx, ry, stroke, strokewidth) {
	    this.append("rect")
				.attr("class", function(d) { return d.getBiologicalType(); })
				.attr("id", function(d) { return d.getId(); })
				.attr("identifier", function(d) { return d.getId(); })
				.attr("width", width)
				.attr("height", height)
				.attr("rx", rx)
				.attr("ry", ry)
				.attr("transform", "translate(-" + width/2 + ",-"
										+ height/2
										+ ")")
				.style("stroke", stroke)
				.style("stroke-width", strokewidth);

		this.append("rect").attr("class","fontSelected")
			.attr("width", width)
			.attr("height", height)
			.attr("rx", rx)
			.attr("ry", ry)
			.attr( "transform", "translate(-" + width/2 + ",-" + height/2 + ")")
			.style("fill-opacity", '0')
			.style("fill", '#000');
	};

	d3.selection.prototype.setNodeForm = function(width, height, rx, ry, stroke, strokewidth) {
		this.style("opacity", 1)
	    	.select("rect")
			.attr("width", width)
			.attr("height", height)
			.attr("rx", rx)
			.attr("ry", ry)
			.attr("transform", "translate(-" + width/2 + ",-"
									+ height/2
									+ ")")
			.style("stroke", stroke)
			.style("stroke-width", strokewidth);

		this.select(".fontSelected")
			.attr("width", width)
			.attr("height", height)
			.attr("rx", rx)
			.attr("ry", ry)
			.attr( "transform", "translate(-" + width/2 + ",-" + height/2 + ")")
			.style("stroke-width", strokewidth);
	};

	d3.selection.prototype.addNodeText = function(style) {

		var minDim = Math.min(style.getWidth(),style.getHeight());
			
		this
			.append("svg:text")
	        .attr("fill", "black")
	        .attr("class", function(d) { return d.getBiologicalType(); })
			.each(function(d) { 
				var el = d3.select(this);
			    var name = style.getDisplayLabel(d, style.getLabel());
				name = name.split(' ');
				el.text('');
				for (var i = 0; i < name.length; i++) {
					var nameDOMFormat = $("<div/>").html(name[i]).text();
			        var tspan = el.append('tspan').text(nameDOMFormat);
			        if (i > 0)
			            tspan.attr('x', 0).attr('dy', '5');
			    }
			})
			.style("font-size",style.getFontSize())
			.style("paint-order","stroke")
			.style("stroke-width", 1)
			.style("stroke", "white")
			.style("stroke-opacity", "0.7")
			.attr("dy", ".4em")
			.style("font-weight", 'bold')
			.style("pointer-events", 'none')
			.attr("y",minDim/2+5);

	};

