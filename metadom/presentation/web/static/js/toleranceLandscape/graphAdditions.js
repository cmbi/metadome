// creating and adding the lines for clinvar variants to the graph
function appendClinvar(variants){
	svg.select("g.focus").selectAll(".lines")
		.data(variants)
		.enter().append("line")
		.attr("class", "pathline")
		.attr("x1", function(d) { return x(d.pos);})
		.attr("y1", 0 + margin.top + margin.bottom)
		.attr("x2", function(d) { return x(d.pos);})
		.attr("y2", height)
		.style("stroke", "green")
		.style("stroke-width", 3)
		.style("clip-path", "url(#clip)")
		.on("mouseover", function(d) {		
			clinvarTip.show(d)
			d3.select(this).style("stroke", "blue");
		})
		.on("mouseout", function(d) {		
			clinvarTip.hide(d)
			d3.select(this).style("stroke", "green");
		});
}
// creating and adding hgmd variant lines to the graph
function appendHGMD(hgmdVariants){
	svg.select("g.focus").selectAll(".lines")
		.data(hgmdVariants)
		.enter().append("line")
		.attr("class", "hgmdline")
		.attr("x1", function(d) { return x(d.pos);})
		.attr("y1", 0 + margin.top + margin.bottom)
		.attr("x2", function(d) { return x(d.pos);})
		.attr("y2", height)
		.style("stroke", "grey")
		.style("stroke-width", 3)
		.style("clip-path", "url(#clip)")
		.on("mouseover", function(d) {		
			hgmdTip.show(d)
			d3.select(this).style("stroke", "blue");
		})
		.on("mouseout", function(d) {		
			hgmdTip.hide(d)
			d3.select(this).style("stroke", "grey");
		});	
}

// creating and adding pfamdomains to domain view
// and adding metadomain functions to the onclick function of a domain
function appendPfamDomains(protDomain){
	svg.select("g.domains").selectAll(".rect")
		.data(protDomain)
		.enter().append("rect")
		.attr("class", "pfamDomains")
		.attr("x", function(d){ return x(d.start);})
		.attr("y", height3-margin3.bottom)
		.attr("width", function(d){ return x(d.stop) - x(d.start);})
		.attr("height", margin3.bottom)
		.attr("rx", 10)
		.attr("ry", 10)
		.style('opacity', 0.5)
		.style('fill', '#c014e2')
		.style('stroke', 'black')
		.style("clip-path", "url(#clip)")
		.on("mouseover", function(d){		
			domainTip.show(d)
			d3.select(this).style("fill", "yellow");
			d3.select(this).moveToFront();
		})
		.on("mouseout", function(d){
			domainTip.hide(d)
			d3.select(this).style("fill", "#c014e2");
			d3.select(this).moveToBack();
		})
		.on("click", function(d){
			window.open("http://pfam.xfam.org/family/"+d.ID+"", "_blank");
		});
	
	// function to move item to front of svg
	d3.selection.prototype.moveToFront = function() {
		return this.each(function(){
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