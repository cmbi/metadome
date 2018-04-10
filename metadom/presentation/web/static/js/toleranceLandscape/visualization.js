/*******************************************************************************
 * Global variables
 ******************************************************************************/

var svg = d3.select("svg");

// Declare margins
var marginLandscape = {
	top : 20,
	right : 20,
	bottom : 210,
	left : 100
};
var marginContext = {
	top : 530,
	right : 20,
	bottom : 100,
	left : 100
};
var marginAnnotations = {
	top : 530,
	right : 20,
	bottom : 30,
	left : 100
};
var marginLegend = {
	y : 20,
	x : 20,
	height : 470,
	width : 40
};

// Declare various UI widths and heights
var width = +svg.attr("width") - marginLandscape.left - marginLandscape.right;
var height = +svg.attr("height") - marginLandscape.top - marginLandscape.bottom;
var height2 = +svg.attr("height") - marginContext.top - marginContext.bottom;
var height3 = +svg.attr("height") - marginAnnotations.top - marginAnnotations.bottom;

// Scale the axis
var x = d3.scaleLinear().range([ 0, width ]);
var x2 = d3.scaleLinear().range([ 0, width ]);
var y = d3.scaleLinear().range([ height, 0 ]);
var y2 = d3.scaleLinear().range([ height2, 0 ]);

// Set axis
var xAxis = d3.axisBottom(x);
var yAxis = d3.axisLeft(y);

/*******************************************************************************
 * Config variables for visuals
 ******************************************************************************/

// indicates the maximum tolerance score
var maxTolerance = 1.8;

// indicates the various colors to indicate the tolerance
var toleranceColorGradient = [ {
	offset : "0%",
	color : "#d7191c"
}, {
	offset : "12.5%",
	color : "#e76818"
}, {
	offset : "25%",
	color : "#f29e2e"
}, {
	offset : "37.5%",
	color : "#f9d057"
}, {
	offset : "50%",
	color : "#ffff8c"
}, {
	offset : "62.5%",
	color : "#90eb9d"
}, {
	offset : "75%",
	color : "#00ccbc"
}, {
	offset : "87.5%",
	color : "#00a6ca"
}, {
	offset : "100%",
	color : "#2c7bb6"
} ]

/*******************************************************************************
 * Basic user interface elements
 ******************************************************************************/

// Define Area of Tolerance landscape graph
var toleranceArea = d3.area().x(function(d) {
	return x(d.pos);
}).y0(height).y1(function(d) {
	return y(d.score);
});

// Define Line of Tolerance landscape line plot
var toleranceLine = d3.line().x(function(d) {
	return x(d.pos);
}).y(function(d) {
	return y(d.score);
});

// Define Area of the context area
var contextArea = d3.area().curve(d3.curveMonotoneX).x(function(d) {
	return x2(d.pos);
}).y0(height2).y1(function(d) {
	return y2(d.score);
});

/*******************************************************************************
 * Additional user interface elements
 ******************************************************************************/

// Define tooltip for clinvar
var clinvarTip = d3.tip().attr('class', 'd3-tip').offset([ -10, 0 ]).html(
		function(d) {
			var variantString = "Clinvar<br>";
			var i = 0;
			while (i < d.alt.length) {
				variantString = variantString
						+ ("p." + d.pos + d.ref + ">" + d.alt[i] + "<br>");
				i++;
			}
			return "<span style='color:red'>" + variantString + "</span>";
		});

// Define tooltip for pfamdomains
var domainTip = d3.tip().attr('class', 'd3-tip').offset([ -10, 0 ]).html(
		function(d) {
			return "<span style='color:red'>" + d.Name + "</span>";
		});

/*******************************************************************************
 * Main draw function
 ******************************************************************************/

// Creates all graph elements based on the obj
function createGraph(obj) {
	$("#geneName").html(obj.geneName);

	svg.selectAll("*").remove();
	svg = d3.select("svg");

	// Add defs to the svg
	var defs = svg.append("defs").attr('class', 'defs');

	// Add clipping to defs
	svg.select('.defs').append("clipPath").attr("id", "clip").append("rect")
			.attr("width", width).attr("height", height);

	// Extract the various data
	var tolerance_data = obj.sliding_window;
	var domain_data = obj.domains;
	var variant_data = obj.clinvar;

	// Draw all individual user interface elements based on the data
	createToleranceGraph(tolerance_data);
	createToleranceGraphLegend();
	annotateDomains(domain_data);
	appendClinvar(variant_data);

	// Finally draw the context zoom
	addContextZoomView(tolerance_data);
}

/*******************************************************************************
 * Drawing user interface component
 ******************************************************************************/

// Draw the tolerance graph
function createToleranceGraph(tolerance) {
	// append focus view
	var focus = svg.append("g").attr("class", "focus").attr("id",
			"tolerance_graph").attr("transform",
			"translate(" + marginLandscape.left + "," + marginLandscape.top + ")");

	// setting x/y domain according to data
	x.domain(d3.extent(tolerance, function(d) {
		return d.pos;
	}));
	y.domain([ 0, maxTolerance ]);
	x2.domain(x.domain());
	y2.domain(y.domain());

	// create a group from the tolerance data
	var dataGroup = d3.nest().key(function(d) {
		return d.pos;
	}).entries(tolerance);

	// add two consecutive data values per group, so these can be used in
	// drawing rectangles
	dataGroup.forEach(function(group, i) {
		if (i + 1 < dataGroup.length) {
			group.values.push(dataGroup[i + 1].values[0]);
		} else if (i < dataGroup.length) {
			group.values.push(dataGroup[i].values[0]);
		}
	})

	// draw the tolerance area graph, base on the grouped consecutive data
	// values
	dataGroup.forEach(function(d) {
		// add the area specific for this position
		focus.append("path").datum(d.values).attr("class", "area").attr("d",
				toleranceArea);

		// create a linear gradient, specific for this position
		var lineargradient = svg.append("linearGradient").attr("id",
				"area-gradient_" + d.values[0].pos + "-" + d.values[1].pos)
				.attr("x1", "0%").attr("y1", "0%").attr("x2", "100%").attr(
						"y2", "0%");

		// calculate the offset start score
		lineargradient.append("stop").attr("class", "start").attr("offset",
				"0%").attr("stop-color", tolerance_color(d.values[0].score));

		// calculate the offset stop score
		lineargradient.append("stop").attr("class", "end").attr("offset",
				"100%").attr("stop-color", tolerance_color(d.values[1].score));
	});

	// color the area under the curve in contrast to the tolerance score
	focus.selectAll(".area").style("fill", function(d, i) {
		return "url(#area-gradient_" + d[0].pos + "-" + d[1].pos + ")";
	});

	// add tolerance line
	focus.append('path').datum(tolerance).attr('class', 'line').attr('id',
			'toleranceLine').attr('fill', 'none').attr("stroke", "steelblue")
			.attr('stroke-width', "2px").style("clip-path", "url(#clip)").attr(
					'd', toleranceLine);

	// append xAxis for focus view
	focus.append("g").attr("class", "axis axis--x").attr("transform",
			"translate(0," + height + ")").call(xAxis);

	// append yAxis for focus view
	focus.append("g").attr("class", "axis axis--y").call(yAxis);
}

// Draw the domain annotation
function annotateDomains(protDomain) {
	// append domain view
	var domains = svg.append("g").attr("class", "domains").attr("id",
			"domain_annotation").attr("transform",
			"translate(" + marginAnnotations.left + "," + marginAnnotations.top + ")");

	// Adding subview for proteindomains
	domains.append("g").attr("class", "axis axis--x").attr("transform",
			"translate(0," + height3 + ")").call(xAxis);

	// Add text to the ui element
	svg.append("text").attr("text-anchor", "left").attr("x", 0).attr("y", 650)
			.attr("dy", 0).attr("font-size", "14px").text("Pfam domains");

	// Call the tooltips
	svg.call(domainTip);

	// Fill the ui element
	domains.selectAll(".rect").data(protDomain).enter().append("rect").attr(
			"class", "pfamDomains").attr("x", function(d) {
		return x(d.start);
	}).attr("y", height3 - marginAnnotations.bottom).attr("width", function(d) {
		return x(d.stop) - x(d.start);
	}).attr("height", marginAnnotations.bottom).attr("rx", 10).attr("ry", 10).style(
			'opacity', 0.5).style('fill', '#c014e2').style('stroke', 'black')
			.style("clip-path", "url(#clip)").on("mouseover", function(d) {
				domainTip.show(d)
				d3.select(this).style("fill", "yellow");
				d3.select(this).moveToFront();
			}).on("mouseout", function(d) {
				domainTip.hide(d)
				d3.select(this).style("fill", "#c014e2");
				d3.select(this).moveToBack();
			}).on(
					"click",
					function(d) {
						window.open("http://pfam.xfam.org/family/" + d.ID + "",
								"_blank");
					});

	// function to move item to front of svg
	d3.selection.prototype.moveToFront = function() {
		return this.each(function() {
			this.parentNode.appendChild(this);
		});
	};

	// function to move item to back of svg
	d3.selection.prototype.moveToBack = function() {
		return this.each(function() {
			var firstChild = this.parentNode.firstChild;
			if (firstChild) {
				this.parentNode.insertBefore(this, firstChild);
			}
		});
	};
}

// draw the ClinVar variants
function appendClinvar(variants) {
	// Call the tooltips
	svg.call(clinvarTip);

	// Fill the ui element
	svg.select("g.focus").selectAll(".lines").data(variants).enter().append(
			"line").attr("class", "clinvar").attr("x1", function(d) {
		return x(d.pos);
	}).attr("y1", 0 + marginLandscape.top + marginLandscape.bottom).attr("x2", function(d) {
		return x(d.pos);
	}).attr("y2", height).style("stroke", "green").style("stroke-width", 3)
			.style("clip-path", "url(#clip)").on("mouseover", function(d) {
				clinvarTip.show(d)
				d3.select(this).style("stroke", "blue");
			}).on("mouseout", function(d) {
				clinvarTip.hide(d);
				d3.select(this).style("stroke", "green");
			});
}

// Draw the context area for zooming
function addContextZoomView(tolerance) {
	// add the brush element
	var brush = d3.brushX().extent([ [ 0, 0 ], [ width, height2 ] ]).on(
			"brush end", brushed);

	// append context view
	var context = svg.append("g").attr("class", "context").attr("id",
			"zoom_landscape").attr("transform",
			"translate(" + marginContext.left + "," + marginContext.top + ")");

	// append context area
	context.append("path").datum(tolerance).style("fill", "grey").style(
			"clip-path", "url(#clip)").attr("d", contextArea);

	// append xAxis for context view
	context.append("g").attr("class", "axis axis--x").attr("transform",
			"translate(0," + height2 + ")").call(xAxis);

	// append yAxis for context view
	context.append("g").attr("class", "brush").call(brush).call(brush.move,
			x.range());

	svg.append("text").attr("text-anchor", "left").attr("x", 0).attr("y", 575)
			.attr("dy", 0).attr("font-size", "14px").text("Zoom view");

	// Define the brushed function
	function brushed() {
		var s = d3.event.selection || x2.range();
		x.domain(s.map(x2.invert, x2));
		var focus = d3.select("#tolerance_graph");
		focus.selectAll(".area").attr("d", toleranceArea);
		focus.select(".line").attr("d", toleranceLine);
		focus.select(".axis--x").call(xAxis);
		focus.selectAll(".clinvar").attr("x1", function(d) {
			return x(d.pos);
		}).attr("x2", function(d) {
			return x(d.pos);
		});

		var domains = d3.select("#domain_annotation")

		domains.select(".axis--x").call(xAxis);
		domains.selectAll(".pfamDomains").attr("x", function(d) {
			return x(d.start);
		}).attr("width", function(d) {
			return x(d.stop) - x(d.start);
		});
	}
}

// Draw the legend for the Tolerance graph
function createToleranceGraphLegend() {
	// append gradient to defs
	var legendGradient = svg.select('.defs').append("linearGradient").attr(
			"id", "legendGradient")
		    .attr("x1", "0%")
		    .attr("y1", "0%")
		    .attr("x2", "0%")
		    .attr("y2", "100%");

	// set legend of the tolerance score
	legendGradient.selectAll("stop")
			.data(toleranceColorGradient).enter()
			.append("stop").attr("offset", function(d) {
				return d.offset;
			}).attr("stop-color", function(d) {
				return d.color;
			});
	
	// append heatmap legend
	svg.append("rect").attr("x", marginLegend.x).attr(
			"y", marginLegend.y).attr("width", marginLegend.width).attr("height", marginLegend.height).style("fill",
			"url(#legendGradient)");

	var context = svg.append("g").attr("class", "context").attr("id",
			"zoom_landscape").attr("transform",
			"translate(" + marginContext.left + "," + marginContext.top + ")");

	// append legend text
	svg.append("text").attr("text-anchor", "middle").attr("x", -50).attr("y",
			15).attr("dy", 0).attr("font-size", "14px").attr("transform",
			"rotate(-90)").text("Tolerant");

	// append legend text
	svg.append("text").attr("text-anchor", "middle").attr("x", -450).attr("y",
			15).attr("dy", 0).attr("font-size", "14px").attr("transform",
			"rotate(-90)").text("Intolerant");
}

/*******************************************************************************
 * Static interface functions
 ******************************************************************************/

// the color coding for specific tolerance scores
// color #f29e2e indicates the average dn/ds tolerance score over all genes
function tolerance_color(score) {
	if (score <= 0.175) {
		return toleranceColorGradient[0].color;
	} else if (score <= 0.35) {
		return toleranceColorGradient[1].color;
	} else if (score <= 0.525) {
		return toleranceColorGradient[2].color;
	} else if (score <= 0.7) {
		return toleranceColorGradient[3].color;
	} else if (score <= 0.875) {
		return toleranceColorGradient[4].color;
	} else if (score <= 1.025) {
		return toleranceColorGradient[5].color;
	} else if (score <= 1.2) {
		return toleranceColorGradient[6].color;
	} else if (score <= 1.375) {
		return toleranceColorGradient[7].color;
	} else {
		return toleranceColorGradient[8].color;
	}
}
