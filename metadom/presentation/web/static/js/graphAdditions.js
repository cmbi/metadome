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
			d3.select(".modal-header").select("svg").remove();
			d3.select(".modal-body").select("svg").remove();
			
			var modal = document.getElementById('myModal');
			var modelText = document.getElementById("modalText");
			$("#pfamID").remove();
			$("#pfamLink").remove();
			$("#modal-hr").remove();
			var a = document.createElement('a');
			var pfamLink = "http://pfam.xfam.org/family/"+d.ID+"";
			var pfamText = d.ID;
			a.setAttribute('id', 'pfamLink')
			a.setAttribute('href', pfamLink);
			a.setAttribute('target', "_blank");
			a.style.color="black";
			a.innerHTML = pfamText+" - "+d.Name;
			
			var hr = document.createElement('hr');
			hr.setAttribute('id', 'modal-hr');
			document.getElementsByClassName('modal-header')[0].appendChild(a);
			document.getElementsByClassName('modal-header')[0].appendChild(hr);
			
			getMetaDomainAlignment(d.ID, d.domID, d.start);
			
			var span = document.getElementsByClassName("close")[0];
				modal.style.display = "block";
				
				window.onclick = function(event){
					if (event.target == modal){
						modal.style.display = "none";
					}
				}
				span.onclick = function() {
					modal.style.display = "none";
				}
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

// adding rects for all positions of a domain to the modal box
function appendAlignmentDomain(alignment, pfamID, start){
	var x = d3.scaleLinear().range([0, '100%']);
	x.domain([0,alignment.length]);									
	d3.select(".modal-header")
		.append("svg")
			.attr("width", '95%')
			.attr("height", 60)
			.attr("align", "center")
		.append("g")
			.attr("transform", "translate(" + 5 + "," + 5 + ")");
	
	d3.select(".modal-header").select("svg").call(metadomPosTip);
	var g = d3.select(".modal-header").select("svg").select("g")
	g.selectAll(".rect")
		.data(alignment)
		.enter().append("rect")
		.attr("x", function(d){ return x(d.dcp);})
		.attr("y", 0)
		.attr("width", x(1))
		.attr("height", 50)
		.attr("class", "alignmentPosition")
		.attr("tolscore", function(d){
			var pathdata = d3.select("svg").select("g.focus").select("path").data();
			for (var i=0; i<pathdata[0].length;i++){
				if ((d.pos+start)==pathdata[0][i].pos){
					return pathdata[0][i].score;
				}
				if (d.pos=="gene doesn't contain this position"){
					return null;
				}
			}
		})
		
		.style("fill", function(d){ return d.color;})
		.on("mouseover", function(d){
			d3.select(this).style("fill", "yellow");
			var score = d3.select(this).attr("tolscore");
			metadomPosTip.show(d, start, score);
		})
		.on("mouseout", function(d){
			d3.select(this).style("fill", d.color);
			metadomPosTip.hide();
		})
		.on("click", function(d){
			d3.selectAll(".alignmentPosition")
				.style("fill", function(e){return e.color;})
				.on("mouseout", function(d){
					d3.select(this).style("fill", d.color);
					metadomPosTip.hide();
				})
				.on("mouseover", function(d){
					d3.select(this).style("fill", "yellow");
					var score = d3.select(this).attr("tolscore");
					metadomPosTip.show(d, start, score);
				})
				
			d3.select(this)
				.style("fill", "orange");
				
			var position = d.dcp;
			getMetaDomainFrequencyInfo(pfamID, position);
			d3.select(this)
				.on("mouseout", function(d){
					metadomPosTip.hide();
				});
			d3.select(this)
				.on("mouseover", null);
		});
	
	d3.select('#dlmetadom').on('click', function(){
		var metadomData = [];
		d3.select(".modal-header").select("svg").selectAll("rect.alignmentPosition")
			.each(function(d){
				var score = d3.select(this).attr("tolscore");
				metadomData.push({"dcp":d.dcp, "genepos":(d.pos+start), "score": score});
			});
		var convertedMetadomData = prepareMetadom(metadomData);
		var selection = document.getElementsByClassName("dropdown")[0];
		var input = selection.options[selection.selectedIndex].text;
		var fileName = input+"_"+pfamID+"_metadomain";
		var blob = new Blob([convertedMetadomData], {type: "text/plain"});
		saveAs(blob, fileName+".tsv");
	})
}

// call to the server to get all occurrences of a single domain position in all transcripts of genes
function doMetaDomain(pfamID, position){
	var xhttpMD = new XMLHttpRequest();
	xhttpMD.onreadystatechange = function(){
		if (this.readyState == 4 && this.status == 200) {
			var metaDomain = JSON.parse(xhttpMD.responseText);
			if (isEmpty(metaDomain)){
				console.log("metaDomain empty");
			}
			else{
				var headArray = ["Genename","Uniprot ac","Uniprot pos","Codon","Gencode transcription id","Chr","Chr pos","Strand"]
				var modal = document.getElementById('myModal');
				$(".modal-table").remove();
				var table = document.createElement("table");
				table.setAttribute('class', 'modal-table');
				var thead = table.createTHead();
				thead.setAttribute('class', 'modal-th');
				for (var x=0; x<headArray.length; x++){
					thead.appendChild(document.createElement("th")).appendChild(document.createTextNode(headArray[x]));
				}
				for (var i=0; i<metaDomain.length;i++){
					var tr = table.insertRow();
					tr.setAttribute('class', 'modal-tr');
					for (var y=0;y<metaDomain[i].length;y++){
						var td = tr.insertCell();
						td.setAttribute('class', 'modal-td');
						td.appendChild(document.createTextNode(metaDomain[i][y]));
					}
					table.appendChild(tr);
				}
				document.getElementsByClassName('modal-body')[0].appendChild(table);
			}
		}
	}
	xhttpMD.open("GET", "http://localhost:8080/ToleranceLandscape/metaDomainServlet/?pfamID="+pfamID+"&position="+position+"", true);
	xhttpMD.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttpMD.send();
}

// call to the server to check if the positions of a domain are aligned or not
function getMetaDomainAlignment(pfamID, domID, start){
	var xhttpMA = new XMLHttpRequest();
	xhttpMA.onreadystatechange = function(){
		if (this.readyState == 4 && this.status == 200) {
			var alignment = JSON.parse(xhttpMA.responseText);
			appendAlignmentDomain(alignment, pfamID, start);
		}
	}
	xhttpMA.open("GET", "http://localhost:8080/ToleranceLandscape/alignmentServlet/?pfamID="+pfamID+"&domID="+domID+"", false);
	xhttpMA.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttpMA.send();
	
}

// call to the server to get the frequencies of the metadomain
// And showing the results in de modal popup
function getMetaDomainFrequencyInfo(pfamID, position){
	var xhttpMV = new XMLHttpRequest();
	xhttpMV.onreadystatechange = function(){
		if (this.readyState == 4 && this.status == 200){
			var metaDomVariants = JSON.parse(xhttpMV.responseText);
			if (isEmpty(metaDomVariants)){
				console.log("metaDomVariants empty");
			}
			else{
				var modal = document.getElementById('myModal');
				var modelText = document.getElementById("modalText");
				modalText.innerHTML = ""+pfamID+" domain consensus position: "+position+"<br>";
				
				$("#metadomInfo").remove();
				$("#metaDomInfoLink").remove();
				$(".modal-table").remove();
				d3.select(".modal-body").select("svg").remove();
				
				var modalWidth = document.getElementsByClassName("modal-body")[0].offsetWidth;
				var svgWidth = modalWidth*0.95;
				var svgItemWidth = modalWidth*0.90;
				
				//[x, y] = combi frequencies
				//[xr, yr] = reference frequencies
				//[xa, ya] = alternative frequencies
				var x = d3.scaleBand().rangeRound([0, svgItemWidth]).padding(0.1),
					y = d3.scaleLinear().rangeRound([110, 0])
					xr = d3.scaleBand().rangeRound([0, svgItemWidth]).padding(0.1),
					yr = d3.scaleLinear().rangeRound([110, 0])
					xa = d3.scaleBand().rangeRound([0, svgItemWidth]).padding(0.1),
					ya = d3.scaleLinear().rangeRound([110, 0]);
			
				d3.select(".modal-body")
					.append("svg")
						.attr("width", svgWidth)
						.attr("height", 450)
						.attr("align", "center")
					.append("g")
						.attr("transform", "translate(" + 50 + "," + 20 + ")")
						.attr("class", "combi");
				d3.select(".modal-body").select("svg")
					.append("g")
						.attr("transform", "translate(" + 50 + "," + 170 + ")")
						.attr("class", "ref");
				d3.select(".modal-body").select("svg")	
					.append("g")	
						.attr("transform", "translate(" + 50 + "," + 320 + ")")
						.attr("class", "alt");
					
				x.domain(metaDomVariants[2].map(function(d) { return d.AA; }));
				y.domain([0, d3.max(metaDomVariants[2], function(d) { return d.freq; })]);
				xr.domain(metaDomVariants[0].map(function(d) { return d.ref; }));
				yr.domain([0, d3.max(metaDomVariants[0], function(d) { return d.freq; })]);
				xa.domain(metaDomVariants[1].map(function(d) { return d.alt; }));
				ya.domain([0, d3.max(metaDomVariants[1], function(d) { return d.freq; })]);
				
				d3.select(".modal-body").select("svg").call(metadomTip);
				
				d3.select(".modal-body").select("svg").append("text")
					.attr("text-anchor", "left")
					.attr("x", 0)
					.attr("y", 10)
					.attr("font-size", "11px")
					.text("Combi");
				d3.select(".modal-body").select("svg").append("text")
					.attr("text-anchor", "left")
					.attr("x", 0)
					.attr("y", 160)
					.attr("font-size", "11px")
					.text("Ref");
				d3.select(".modal-body").select("svg").append("text")
					.attr("text-anchor", "left")
					.attr("x", 0)
					.attr("y", 310)
					.attr("font-size", "11px")
					.text("Alt");
				
				//gc = combi
				var gc = d3.select(".modal-body").select("svg").select("g.combi")
				gc.append("g")
					.attr("class", "axis axis--x")
					.attr("transform", "translate(0,110)")
					.call(d3.axisBottom(x));
			
				gc.append("g")
					.attr("class", "axis axis--y")
					.call(d3.axisLeft(y))
				  .append("text")
				  	.attr("transform", "rotate(-90)")
				  	.attr("y", -40)
				  	.attr("dy", "0.71em")
				  	.attr("text-anchor", "end")
					.style("fill", "black")
				  	.text("Frequency");
				
				gc.selectAll(".bar")
					.data(metaDomVariants[2])
					.enter().append("rect")
						.attr("class", "bar")
						.attr("x", function(d){return x(d.AA);})
						.attr("y", function(d){return y(d.freq);})
						.attr("width", x.bandwidth())
						.attr("height", function(d){ return 110 - y(d.freq);})
						.on("mouseover", function(d){
							metadomTip.show(d);
						})
						.on("mouseout", function(d){
							metadomTip.hide(d);
						});
				//gr = reference
				var gr = d3.select(".modal-body").select("svg").select("g.ref")
				gr.append("g")
					.attr("class", "axis axis--x")
					.attr("transform", "translate(0,110)")
					.call(d3.axisBottom(xr));
			
				gr.append("g")
					.attr("class", "axis axis--y")
					.call(d3.axisLeft(yr))
				  .append("text")
				  	.attr("transform", "rotate(-90)")
				  	.attr("y", -40)
				  	.attr("dy", "0.71em")
				  	.attr("text-anchor", "end")
					.style("fill", "black")
				  	.text("Frequency");
				
				gr.selectAll(".bar")
					.data(metaDomVariants[0])
					.enter().append("rect")
						.attr("class", "bar")
						.attr("x", function(d){return xr(d.ref);})
						.attr("y", function(d){return yr(d.freq);})
						.attr("width", xr.bandwidth())
						.attr("height", function(d){ return 110 - yr(d.freq);})
						.on("mouseover", function(d){
							metadomTip.show(d);
						})
						.on("mouseout", function(d){
							metadomTip.hide(d);
						});
				//ga = alternative
				var ga = d3.select(".modal-body").select("svg").select("g.alt")
				ga.append("g")
					.attr("class", "axis axis--x")
					.attr("transform", "translate(0,110)")
					.call(d3.axisBottom(xa));
			
				ga.append("g")
					.attr("class", "axis axis--y")
					.call(d3.axisLeft(ya))
				  .append("text")
				  	.attr("transform", "rotate(-90)")
				  	.attr("y", -40)
				  	.attr("dy", "0.71em")
				  	.attr("text-anchor", "end")
					.style("fill", "black")
				  	.text("Frequency");
				
				ga.selectAll(".bar")
					.data(metaDomVariants[1])
					.enter().append("rect")
						.attr("class", "bar")
						.attr("x", function(d){return xa(d.alt);})
						.attr("y", function(d){return ya(d.freq);})
						.attr("width", xa.bandwidth())
						.attr("height", function(d){ return 110 - ya(d.freq);})
						.on("mouseover", function(d){
							metadomTip.show(d);
						})
						.on("mouseout", function(d){
							metadomTip.hide(d);
						});
				
				
				var p = document.createElement('p');
				p.setAttribute('id', 'metaDomInfoLink');
				p.onclick = function(){
					doMetaDomain(pfamID, position);
				}
				p.innerHTML = "Click to get matching domain positions";
				document.getElementsByClassName('modal-body')[0].appendChild(p);
				
				var span = document.getElementsByClassName("close")[0];
				modal.style.display = "block";
				
				window.onclick = function(event){
					if (event.target == modal){
						modal.style.display = "none";
						$("#metadomInfo").remove();
						$("#metaDomInfoLink").remove();
						$(".modal-table").remove();
						document.getElementById("modalText").innerHTML = "Click on a position to get the metadomain position information";
					}
				}
				span.onclick = function() {
					modal.style.display = "none";
					$("#metadomInfo").remove();
					$("#metaDomInfoLink").remove();
					$(".modal-table").remove();
					document.getElementById("modalText").innerHTML = "Click on a position to get the metadomain position information";
				}
			}
		}
	}
	xhttpMV.open("GET", "http://localhost:8080/ToleranceLandscape/metaDomainVariantServlet/?pfamID="+pfamID+"&position="+position+"", true);
	xhttpMV.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttpMV.send();
}