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

var metadomTip = d3.tip().attr('class', 'd3-tip').offset([ -10, 0 ]).html(
		function(d) {
			return "<span style='color:red'> Frequency:<br>" + d.freq
					+ "</span>";
		});

var metadomPosTip = d3.tip().attr('class', 'd3-tip').offset([ -10, 0 ]).html(
		function(d, start, score) {
			if (d.pos != "gene doesn't contain this position") {
				return "<span style='color:red'> DCP*: " + d.dcp
						+ "<br> Gene pos: " + (d.pos + start) + "<br> Score: "
						+ score + "</span>";
			} else {
				return "<span style='color:red'> DCP*: " + d.dcp
						+ "<br> Gene pos: " + d.pos + "<br> Score: " + score
						+ "</span>";
			}
		});