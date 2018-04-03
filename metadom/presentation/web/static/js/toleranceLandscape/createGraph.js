// creating the tolerance graph and setting the main elements of the graph
function createGraph(obj){	
	$("#geneName").html(obj.geneName);
	
	svg.selectAll("*").remove();
	svg = d3.select("svg");
	// setting axis
	var xAxis = d3.axisBottom(x),
		xAxis2 = d3.axisBottom(x2),
		xAxis3 = d3.axisBottom(x),
		yAxis = d3.axisLeft(y);
	
	// 
	var brush = d3.brushX()
		.extent([[0, 0], [width, height2]])
		.on("brush end", brushed);
	
	// 
	var zoom = d3.zoom()
		.scaleExtent([1, 30])
		.translateExtent([[0, 0], [width, height]])
		.extent([[0, 0], [width, height]])
		.on("zoom", zoomed);

	// define the focus area
	var	area = d3.area()	
		.x(function(d) { return x(d.pos); })	
		.y0(height)					
		.y1(function(d) { return y(d.score); });
	
	// define the context area
	var area2 = d3.area()
		.curve(d3.curveMonotoneX)
		.x(function(d) { return x2(d.pos); })
		.y0(height2)
		.y1(function(d) { return y2(d.score); });
	
	// 
	svg.append("defs").append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", width)
		.attr("height", height);
	
	// append focus view
	var focus = svg.append("g")
		.attr("class", "focus")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	// append context view
	var context = svg.append("g")
		.attr("class", "context")
		.attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");
	
	// append domain view
	var domains = svg.append("g")
		.attr("class", "domains")
		.attr("transform", "translate(" + margin3.left + "," + margin3.top + ")");
	
	svg.call(clinvarTip);
	svg.call(domainTip);
	
	
	// the tolerance data
	var tolerance = obj.sliding_window;
	
	// setting x/y domain according to data
	x.domain(d3.extent(tolerance, function(d) { return d.pos; }));
	y.domain([0, d3.max(tolerance, function(d) { return d.score; })]);
	x2.domain(x.domain());
	y2.domain(y.domain());
	
	// setting the legend and heatmap to correct mean
	if (parseFloat($("#frequency").val()) >= 0.0001){
		var  ymax = 0.85;
	}
	else{
		var ymax = 1.3;
	}
	
	// set the gradient
	svg.append("linearGradient")				
		.attr("id", "area-gradient")			
		.attr("gradientUnits", "userSpaceOnUse")
		.attr("x1", 0).attr("y1", y(0))			
		.attr("x2", 0).attr("y2", y(ymax))		
		.selectAll("stop")						
		.data([
			{offset: "0%", color: "#d7191c"}, 
			{offset: "12.5%", color: "#e76818"},  
			{offset: "25%", color: "#f29e2e"}, 
			{offset: "37.5%", color: "#f9d057"}, 
			{offset: "50%", color: "#ffff8c"}, 
			{offset: "62.5%", color: "#90eb9d"}, 
			{offset: "75%", color: "#00ccbc"},      
			{offset: "87.5%", color: "#00a6ca"},        
			{offset: "100%", color: "#2c7bb6"}
			])					
		.enter().append("stop")
		.attr("offset", function(d) { return d.offset; })
		.attr("stop-color", function(d) { return d.color; });
	
	// append tolerance area
	focus.append("path")
		.datum(tolerance)
		.attr("class", "area")
		.attr("fill", "none")
		.attr("stroke", "#006991")
		.attr("stroke-linejoin", "round")
		.attr("stroke-linecap", "round")
		.attr("stroke-width", 1.5)
		.style("clip-path", "url(#clip)")
		.attr("d", area);
	
	// append xAxis for focus view
	focus.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);
	
	// append yAxis for focus view
	focus.append("g")
		.attr("class", "axis axis--y")
		.call(yAxis);
	
	// append context area
	context.append("path")
		.datum(tolerance)
		.style("fill", "grey")
		.attr("d", area2);
	
	// append xAxis for context view
	context.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," + height2 + ")")
		.call(xAxis2);
	
	// append yAxis for context view
	context.append("g")
		.attr("class", "brush")
		.call(brush)
		.call(brush.move, x.range());
	
	//Adding subview for proteindomains
	domains.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," +height3+ ")")
		.call(xAxis3);
	
	// append rect for zoom
	svg.append("rect")
		.attr("class", "zoom")
		.attr("width", width)
		.attr("height", height)
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
		.call(zoom);

	// brushed function	
	function brushed() {
		if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom") return; // ignore brush-by-zoom
		var s = d3.event.selection || x2.range();
		x.domain(s.map(x2.invert, x2));
		focus.select(".area").attr("d", area);
		focus.select(".axis--x").call(xAxis);
		focus.selectAll(".clinvar").attr("x1", function(d){ return x(d.pos);}).attr("x2", function(d){ return x(d.pos);});
		domains.select(".axis--x").call(xAxis);
		domains.selectAll(".pfamDomains").attr("x", function(d){ return x(d.start);}).attr("width", function(d){ return x(d.stop) - x(d.start);});
		svg.select(".zoom").call(zoom.transform, d3.zoomIdentity
			.scale(width / (s[1] - s[0]))
			.translate(-s[0], 0));
	}
	
	// zoomed function
	function zoomed() {
		if (d3.event.sourceEvent && d3.event.sourceEvent.type === "brush") return; // ignore zoom-by-brush
		var t = d3.event.transform;
		x.domain(t.rescaleX(x2).domain());
		focus.select(".area").attr("d", area);
		focus.select(".axis--x").call(xAxis);
		focus.selectAll(".clinvar").attr("x1", function(d){ return x(d.pos);}).attr("x2", function(d){ return x(d.pos);});
		domains.select(".axis--x").call(xAxis);
		domains.selectAll(".pfamDomains").attr("x", function(d){ return x(d.start);}).attr("width", function(d){ return x(d.stop) - x(d.start);});
		context.select(".brush").call(brush.move, x.range().map(t.invertX, t));
	}

	function type(d) {
		d.pos = +d.pos;
		d.score = +d.score;
		return d;
	}
	
	// append defs for gradient
	var defs = svg.append("defs");
	
	// append gradient to defs
	var linearGradient = defs.append("linearGradient")
		.attr("id", "legendGradient");
	
	// set gradient
	linearGradient.selectAll("stop") 
		.data([                             
			{offset: "0%", color: "#d7191c"}, 
			{offset: "12.5%", color: "#e76818"},  
			{offset: "25%", color: "#f29e2e"}, 
			{offset: "37.5%", color: "#f9d057"}, 
			{offset: "50%", color: "#ffff8c"}, 
			{offset: "62.5%", color: "#90eb9d"}, 
			{offset: "75%", color: "#00ccbc"},      
			{offset: "87.5%", color: "#00a6ca"},        
			{offset: "100%", color: "#2c7bb6"}   
		  ])                  
		.enter().append("stop")
		.attr("offset", function(d) { return d.offset; })   
		.attr("stop-color", function(d) { return d.color; });
	
	// append heatmap legend
	svg.append("rect")
		.attr("transform", "rotate(-90)")
		.attr("x", -490)
		.attr("y", 20)
		.attr("width", 470)
		.attr("height", 40)
		.style("fill","url(#legendGradient)") ;
	
	// append legend text
	svg.append("text")
		.attr("text-anchor", "middle")
		.attr("x",-50)
		.attr("y",15)
		.attr("dy",0)
		.attr("font-size", "14px")
		.attr("transform", "rotate(-90)")
		.text("Tolerant");
	
	// append legend text
	svg.append("text")
		.attr("text-anchor", "middle")
		.attr("x",-450)
		.attr("y",15)
		.attr("dy",0)
		.attr("font-size", "14px")
		.attr("transform", "rotate(-90)")
		.text("Intolerant");
	
	svg.append("text")
		.attr("text-anchor", "left")
		.attr("x", 0)
		.attr("y", 575)
		.attr("dy", 0)
		.attr("font-size", "14px")
		.text("Zoom view");

	svg.append("text")
		.attr("text-anchor", "left")
		.attr("x", 0)
		.attr("y", 650)
		.attr("dy", 0)
		.attr("font-size", "14px")
		.text("Pfam domains");
	
	//var customVariants = [{"pos": 49, "ref": "S", "alt": ["I","N","R"]},{"pos": 50, "ref": "P", "alt": ["T","S","Q","L"]},{"pos": 87, "ref": "R", "alt": ["C"]},{"pos": 88, "ref": "P", "alt": ["S"]},{"pos": 144, "ref": "A", "alt": ["P"]},{"pos": 172, "ref": "H", "alt": ["HX"]},{"pos": 175, "ref": "W", "alt": ["L"]},{"pos": 182, "ref": "N", "alt": ["S"]},{"pos": 216, "ref": "V", "alt": ["G"]},{"pos": 21, "ref": "E", "alt": ["EX"]},{"pos": 23, "ref": "Q", "alt": ["QP"]},{"pos": 29, "ref": "P", "alt": ["L"]}];
	//var customVariants = [{"pos": 13, "ref": "G", "alt": ["A"]}];
//	svg.select("g.focus").selectAll(".lines")
//		.data(customVariants)
//		.enter().append("line")
//		.attr("class", "customVariants")
//		.attr("x1", function(d) { return x(d.pos);})
//		.attr("y1", 0 + margin.top + margin.bottom)
//		.attr("x2", function(d) { return x(d.pos);})
//		.attr("y2", height)
//		.style("stroke", "black")
//		.style("stroke-width", 3)
//		.style("clip-path", "url(#clip)")
//		.on("mouseover", function(d) {		
//			hgmdTip.show(d)
//			d3.select(this).style("stroke", "yellow");
//		})
//		.on("mouseout", function(d) {		
//			hgmdTip.hide(d)
//			d3.select(this).style("stroke", "black");
//		});
	
	// Download tsv with tolerance, variants and domains
	d3.select('#dlJSON').on('click', function() {
		var selectionWindow = x.domain();
		var startIP = selectionWindow[0];
		var endIP = selectionWindow[1];
		var slidingW = parseInt(tolerance[1].pos);
		var startExport = startIP - slidingW + 1;
		var endExport = endIP - slidingW + 2;
		var variants = [];
		var hgmd = [];
		var protDomain = [];
		if (startIP < slidingW){
			startExport = 0;
		}
		
		svg.select("g.focus").selectAll("line.clinvar")
			.each(function (d){
				variants.push(d);
			});
		
		svg.select("g.focus").selectAll("line.hgmdline")
		.each(function (d){
			hgmd.push(d);
		});
	
		svg.select("g.domains").selectAll("rect.pfamDomains")
			.each(function (d){
				protDomain.push(d);
			});
		
		var clinDomArray = convertToArray(variants, hgmd, protDomain, startIP, endIP);
		var jsonse = JSON.stringify(tolerance.slice(startExport,endExport));
		var convertJS = convertToTSV(jsonse, clinDomArray);
		var blob = new Blob([convertJS], {type: "text/plain"});
		var selection = document.getElementsByClassName("dropdown")[0];
		var fileName = selection.options[selection.selectedIndex].text;
		saveAs(blob, fileName+"_"+startIP+"_"+endIP+".tsv");
	});
	
	// Download for the whole svg as svg
	d3.select('#dlSVG').on('click', function() {
		var selection = document.getElementsByClassName("dropdown")[0];
		var fileName = selection.options[selection.selectedIndex].text;
		var config = {
			filename: fileName,
		}
			d3_save_svg.save(d3.select('svg').node(), config);
	});
	
}