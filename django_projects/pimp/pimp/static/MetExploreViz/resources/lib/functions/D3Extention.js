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

