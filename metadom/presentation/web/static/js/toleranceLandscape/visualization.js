var svg = d3.select("svg");
// setting basic variables
margin = {
	top : 20,
	right : 20,
	bottom : 210,
	left : 100
}, margin2 = {
	top : 530,
	right : 20,
	bottom : 100,
	left : 100
}, margin3 = {
	top : 530,
	right : 20,
	bottom : 30,
	left : 100
}, width = +svg.attr("width") - margin.left - margin.right, height = +svg
		.attr("height")
		- margin.top - margin.bottom, height2 = +svg.attr("height")
		- margin2.top - margin2.bottom, height3 = +svg.attr("height")
		- margin3.top - margin3.bottom;

// Scaling axis
var x = d3.scaleLinear().range([ 0, width ]), x2 = d3.scaleLinear().range(
		[ 0, width ]), y = d3.scaleLinear().range([ height, 0 ]), y2 = d3
		.scaleLinear().range([ height2, 0 ]);

// define tooltip for clinvar
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

// define tooltip for pfamdomains
var domainTip = d3.tip().attr('class', 'd3-tip').offset([ -10, 0 ]).html(
		function(d) {
			return "<span style='color:red'>" + d.Name + "</span>";
		});

// the color coding for specific tolerance scores
function tolerance_color(score) {
	if (score > 0.8) {
		return "green";
	} else {
		return "red";
	}
}

// creating the tolerance graph and setting the main elements of the graph
function createGraph(obj) {
	$("#geneName").html(obj.geneName);

	svg.selectAll("*").remove();
	svg = d3.select("svg");
	// setting axis
	var xAxis = d3.axisBottom(x), xAxis2 = d3.axisBottom(x2), xAxis3 = d3
			.axisBottom(x), yAxis = d3.axisLeft(y);

	// 
	var brush = d3.brushX().extent([ [ 0, 0 ], [ width, height2 ] ]).on(
			"brush end", brushed);

	// 
	var zoom = d3.zoom().scaleExtent([ 1, 30 ]).translateExtent(
			[ [ 0, 0 ], [ width, height ] ]).extent(
			[ [ 0, 0 ], [ width, height ] ]);

	// define the tolerance landscape area plot
	var area = d3.area().x(function(d) {
		return x(d.pos);
	}).y0(height).y1(function(d) {
		return y(d.score);
	});

	// define the context area
	var area2 = d3.area().curve(d3.curveMonotoneX).x(function(d) {
		return x2(d.pos);
	}).y0(height2).y1(function(d) {
		return y2(d.score);
	});

	// 
	svg.append("defs").append("clipPath").attr("id", "clip").append("rect")
			.attr("width", width).attr("height", height);

	// append focus view
	var focus = svg.append("g").attr("class", "focus").attr("transform",
			"translate(" + margin.left + "," + margin.top + ")");

	// append context view
	var context = svg.append("g").attr("class", "context").attr("transform",
			"translate(" + margin2.left + "," + margin2.top + ")");

	// append domain view
	var domains = svg.append("g").attr("class", "domains").attr("transform",
			"translate(" + margin3.left + "," + margin3.top + ")");

	// the tolerance data
	var tolerance = obj.sliding_window;

	// setting x/y domain according to data
	x.domain(d3.extent(tolerance, function(d) {
		return d.pos;
	}));
	y.domain([ 0, d3.max(tolerance, function(d) {
		return d.score;
	}) ]);
	x2.domain(x.domain());
	y2.domain(y.domain());

	// Call the tooltips
	svg.call(clinvarTip);
	svg.call(domainTip);

	// create a group from the tolerance data
	var dataGroup = d3.nest().key(function(d) {
		return d.pos;
	}).entries(tolerance);

	// add two consecutive data values per group, so these can be used in
	// drawing rectangles
	dataGroup.forEach(function(group, i) {
		if (i < dataGroup.length - 1) {
			console.log(group);
			console.log(i);

			group.values.push(dataGroup[i + 1].values[0]);
		}
	})

	// draw the tolerance area graph, base on the grouped consecutive data
	// values
	dataGroup.forEach(function(d) {
		focus.append("path").datum(d.values).attr("class", "area").attr("d",
				area);
	});

	// color the area under the curve in contrast to the tolerance score
	focus.selectAll(".area").style("fill", function(d, i) {
		return tolerance_color(d[0].score);
	});

	// append xAxis for focus view
	focus.append("g").attr("class", "axis axis--x").attr("transform",
			"translate(0," + height + ")").call(xAxis);

	// append yAxis for focus view
	focus.append("g").attr("class", "axis axis--y").call(yAxis);

	// append context area
	context.append("path").datum(tolerance).style("fill", "grey").attr("d",
			area2);

	// append xAxis for context view
	context.append("g").attr("class", "axis axis--x").attr("transform",
			"translate(0," + height2 + ")").call(xAxis2);

	// append yAxis for context view
	context.append("g").attr("class", "brush").call(brush).call(brush.move,
			x.range());

	// Adding subview for proteindomains
	domains.append("g").attr("class", "axis axis--x").attr("transform",
			"translate(0," + height3 + ")").call(xAxis3);

	// append rect for zoom
	svg.append("rect").attr("class", "zoom").attr("width", width).attr(
			"height", height).attr("transform",
			"translate(" + margin.left + "," + margin.top + ")").call(zoom);

	// brushed function
	function brushed() {
		if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom")
			return; // ignore brush-by-zoom
		var s = d3.event.selection || x2.range();
		x.domain(s.map(x2.invert, x2));
		focus.selectAll(".area").attr("d", area);
		focus.select(".axis--x").call(xAxis);
		focus.selectAll(".clinvar").attr("x1", function(d) {
			return x(d.pos);
		}).attr("x2", function(d) {
			return x(d.pos);
		});
		domains.select(".axis--x").call(xAxis);
		domains.selectAll(".pfamDomains").attr("x", function(d) {
			return x(d.start);
		}).attr("width", function(d) {
			return x(d.stop) - x(d.start);
		});
		svg.select(".zoom").call(
				zoom.transform,
				d3.zoomIdentity.scale(width / (s[1] - s[0]))
						.translate(-s[0], 0));
	}

	function type(d) {
		d.pos = +d.pos;
		d.score = +d.score;
		return d;
	}

	// append defs for gradient
	var defs = svg.append("defs");

	// append gradient to defs
	var legendGradient = defs.append("linearGradient").attr("id",
			"legendGradient");

	// set legend of the tolerance score
	legendGradient.selectAll("stop").data([ {
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
	} ]).enter().append("stop").attr("offset", function(d) {
		return d.offset;
	}).attr("stop-color", function(d) {
		return d.color;
	});

	// append heatmap legend
	svg.append("rect").attr("transform", "rotate(-90)").attr("x", -490).attr(
			"y", 20).attr("width", 470).attr("height", 40).style("fill",
			"url(#legendGradient)");

	// append legend text
	svg.append("text").attr("text-anchor", "middle").attr("x", -50).attr("y",
			15).attr("dy", 0).attr("font-size", "14px").attr("transform",
			"rotate(-90)").text("Tolerant");

	// append legend text
	svg.append("text").attr("text-anchor", "middle").attr("x", -450).attr("y",
			15).attr("dy", 0).attr("font-size", "14px").attr("transform",
			"rotate(-90)").text("Intolerant");

	svg.append("text").attr("text-anchor", "left").attr("x", 0).attr("y", 575)
			.attr("dy", 0).attr("font-size", "14px").text("Zoom view");

	svg.append("text").attr("text-anchor", "left").attr("x", 0).attr("y", 650)
			.attr("dy", 0).attr("font-size", "14px").text("Pfam domains");

	// var customVariants = [{"pos": 49, "ref": "S", "alt":
	// ["I","N","R"]},{"pos": 50, "ref": "P", "alt": ["T","S","Q","L"]},{"pos":
	// 87, "ref": "R", "alt": ["C"]},{"pos": 88, "ref": "P", "alt":
	// ["S"]},{"pos": 144, "ref": "A", "alt": ["P"]},{"pos": 172, "ref": "H",
	// "alt": ["HX"]},{"pos": 175, "ref": "W", "alt": ["L"]},{"pos": 182, "ref":
	// "N", "alt": ["S"]},{"pos": 216, "ref": "V", "alt": ["G"]},{"pos": 21,
	// "ref": "E", "alt": ["EX"]},{"pos": 23, "ref": "Q", "alt": ["QP"]},{"pos":
	// 29, "ref": "P", "alt": ["L"]}];
	// var customVariants = [{"pos": 13, "ref": "G", "alt": ["A"]}];
	// svg.select("g.focus").selectAll(".lines")
	// .data(customVariants)
	// .enter().append("line")
	// .attr("class", "customVariants")
	// .attr("x1", function(d) { return x(d.pos);})
	// .attr("y1", 0 + margin.top + margin.bottom)
	// .attr("x2", function(d) { return x(d.pos);})
	// .attr("y2", height)
	// .style("stroke", "black")
	// .style("stroke-width", 3)
	// .style("clip-path", "url(#clip)")
	// .on("mouseover", function(d) {
	// hgmdTip.show(d)
	// d3.select(this).style("stroke", "yellow");
	// })
	// .on("mouseout", function(d) {
	// hgmdTip.hide(d)
	// d3.select(this).style("stroke", "black");
	// });

	// Download tsv with tolerance, variants and domains
	d3.select('#dlJSON').on(
			'click',
			function() {
				var selectionWindow = x.domain();
				var startIP = selectionWindow[0];
				var endIP = selectionWindow[1];
				var slidingW = parseInt(tolerance[1].pos);
				var startExport = startIP - slidingW + 1;
				var endExport = endIP - slidingW + 2;
				var variants = [];
				var hgmd = [];
				var protDomain = [];
				if (startIP < slidingW) {
					startExport = 0;
				}

				svg.select("g.focus").selectAll("line.clinvar").each(
						function(d) {
							variants.push(d);
						});

				svg.select("g.focus").selectAll("line.hgmdline").each(
						function(d) {
							hgmd.push(d);
						});

				svg.select("g.domains").selectAll("rect.pfamDomains").each(
						function(d) {
							protDomain.push(d);
						});

				var clinDomArray = convertToArray(variants, hgmd, protDomain,
						startIP, endIP);
				var jsonse = JSON.stringify(tolerance.slice(startExport,
						endExport));
				var convertJS = convertToTSV(jsonse, clinDomArray);
				var blob = new Blob([ convertJS ], {
					type : "text/plain"
				});
				var selection = document.getElementsByClassName("dropdown")[0];
				var fileName = selection.options[selection.selectedIndex].text;
				saveAs(blob, fileName + "_" + startIP + "_" + endIP + ".tsv");
			});

	// Download for the whole svg as svg
	d3.select('#dlSVG').on('click', function() {
		var selection = document.getElementsByClassName("dropdown")[0];
		var fileName = selection.options[selection.selectedIndex].text;
		var config = {
			filename : fileName,
		}
		d3_save_svg.save(d3.select('svg').node(), config);
	});

}

// creating and adding the lines for clinvar variants to the graph
function appendClinvar(variants) {
	svg.select("g.focus").selectAll(".lines").data(variants).enter().append(
			"line").attr("class", "clinvar").attr("x1", function(d) {
		return x(d.pos);
	}).attr("y1", 0 + margin.top + margin.bottom).attr("x2", function(d) {
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

// creating and adding pfamdomains to domain view
// and adding metadomain functions to the onclick function of a domain
function appendPfamDomains(protDomain) {
	svg.select("g.domains").selectAll(".rect").data(protDomain).enter().append(
			"rect").attr("class", "pfamDomains").attr("x", function(d) {
		return x(d.start);
	}).attr("y", height3 - margin3.bottom).attr("width", function(d) {
		return x(d.stop) - x(d.start);
	}).attr("height", margin3.bottom).attr("rx", 10).attr("ry", 10).style(
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