/*******************************************************************************
 * Global variables for landscape
 ******************************************************************************/
var selected_positions = 0;

var main_outerWidth = 1300;
var main_outerHeight = 700;
var main_svg = d3.select("#landscape_svg").attr("width", main_outerWidth)
		.attr("height", main_outerHeight);

// Declare margins
var main_marginLandscape = {
	top : 20,
	right : 20,
	bottom : 410,
	left : 80
};
var main_marginLegend = {
	top : 20,
	right : 1240,
	bottom : 410,
	left : 20
};
var main_marginPositionInfo = {
	top : 325,
	right : 20,
	bottom : 335,
	left : 80
};
var main_marginAnnotations = {
	top : 310,
	right : 20,
	bottom : 320,
	left : 80
};
var main_marginContext = {
	top : 410,
	right : 20,
	bottom : 230,
	left : 80
};

// Declare various UI widths and heights
var main_width = main_outerWidth - main_marginLandscape.left - main_marginLandscape.right;
var main_widthLegend = main_outerWidth - main_marginLegend.left - main_marginLegend.right;
var main_heightLandscape = main_outerHeight - main_marginLandscape.top
		- main_marginLandscape.bottom;
var main_heightMarginPositionInfo = main_outerHeight - main_marginPositionInfo.top
		- main_marginPositionInfo.bottom;
var main_heightContext = main_outerHeight - main_marginContext.top - main_marginContext.bottom;
var main_heightAnnotations = main_outerHeight - main_marginAnnotations.top
		- main_marginAnnotations.bottom;

// Scale the axis
var main_x = d3.scaleLinear().range([ 40, main_width -40 ]).nice();
var main_x2 = d3.scaleLinear().range([ 0, main_width ]);
var main_y = d3.scaleLinear().range([ main_heightLandscape, 0 ]);
var main_y2 = d3.scaleLinear().range([ main_heightContext, 0 ]);

// Set axis
var main_xAxis = d3.axisBottom(main_x2).ticks(0);
var main_yAxis = d3.axisLeft(main_y).ticks(0);

/*******************************************************************************
 * Global variables for domain details
 ******************************************************************************/
var domain_details_outerWidth = 1280;
var domain_details_outerHeight = 600;
var domain_details_svg = d3.select("#domain_details_svg").attr("width", domain_details_outerWidth)
.attr("height", domain_details_outerHeight);

//Declare margins
var marginDomainDetailsNormalVar = {
	top : 20,
	right : 20,
	bottom : 320,
	left : 30
};
var marginDomainDetailsPathogenicVar = {
	top : 310,
	right : 20,
	bottom : 20,
	left : 30
};

//Declare various UI widths and heights
var domain_details_width = domain_details_outerWidth - marginDomainDetailsNormalVar.left - marginDomainDetailsNormalVar.right;
var domain_details_heightNormalVar = domain_details_outerHeight - marginDomainDetailsNormalVar.top
		- marginDomainDetailsNormalVar.bottom;
var domain_details_heightPathogenicVar = domain_details_outerHeight - marginDomainDetailsPathogenicVar.top
		- marginDomainDetailsPathogenicVar.bottom;

// Scale the axis
var domain_details_x = d3.scaleBand().rangeRound([ 20, domain_details_width -20 ]).padding(0.1);
var domain_details_normal_y = d3.scaleLinear().rangeRound([ domain_details_heightNormalVar, 0 ]);
var domain_details_pathogenic_y = d3.scaleLinear().rangeRound([ domain_details_heightPathogenicVar, 0 ]);

/*******************************************************************************
 * Global variables for positional meta domain details
 ******************************************************************************/

var metadomain_svg = d3.select("#metadomain_svg").attr("width", 400)
.attr("height", 500);

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
	return main_x (d.protein_pos);
}).y0(main_heightLandscape).y1(function(d) {
	return main_y(d.sw_dn_ds);
});

// Define Line of Tolerance landscape line plot
var toleranceLine = d3.line().x(function(d) {
	return main_x (d.values[0].protein_pos);
}).y(function(d) {
	return main_y(d.values[0].sw_dn_ds);
});

// Define Area of the context area
var contextArea = d3.area().curve(d3.curveMonotoneX).x(function(d) {
	return main_x2(d.protein_pos);
}).y0(main_heightContext).y1(function(d) {
	return main_y2(d.sw_dn_ds);
});

/*******************************************************************************
 * Additional user interface elements
 ******************************************************************************/

// Define tooltip for pfamdomains
var domainTip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([ -10, 0 ])
	.html(function(d) {
	    return "<span><div style='text-align: center;'> Domain " + d.Name + " ("+d.ID+") </br> click for meta-domain annotation</div></span>";
	});

//Define tooltip for pfamdomains
var domain_details_position_tip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([ -10, 0 ])
	.html(function(d) {
	    return "<span> Missense count: " + d + "</span>";
	});


// Define tooltip for positions
var positionTip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([ -10, 0 ])
	.html(function(d, i) {
	    positionTip_str = "<span>";
	    positionTip_str += "Position: p." + d.values[0].protein_pos + " " + d.values[0].cdna_pos + "</br>";
	    positionTip_str += "Codon: " + d.values[0].ref_codon + "</br>";
	    positionTip_str += "Residue: " + d.values[0].ref_aa_triplet;
	    if (d.values[0].domains.length > 0){
		positionTip_str += "</br> In domain(s): ";
		var n_domains_at_position = d.values[0].domains.length;
		for (i = 0; i < n_domains_at_position; i++){
		    if (i+1 == n_domains_at_position){
			positionTip_str+= d.values[0].domains[i].ID;
		    }else{
			positionTip_str+= d.values[0].domains[i].ID+", ";
		    }
		}
	    }
	    positionTip_str += "</span>";
	    return positionTip_str;
	});

/*******************************************************************************
 * Main draw function
 ******************************************************************************/

//Reset all graph elements based on the obj
function resetGraph(){
    	// reset the variables
	selected_positions = 0;
	$("#selected_positions_information").addClass('is-hidden');
	d3.selectAll('.tr').remove();

	selected_positions -= 1;
	if (selected_positions <= 0){
	    $("#selected_positions_information").addClass('is-hidden');
	}

	// reset the svg
	main_svg.selectAll("*").remove();
	main_svg = d3.select("#landscape_svg");

	// reset the metadomain_svg
	metadomain_svg.selectAll("*").remove();
	metadomain_svg = d3.select('#metadomain_svg');
	
	// reset the domain_details_svg
	domain_details_svg.selectAll("*").remove();
	domain_details_svg = d3.select('#domain_details_svg');
	document.getElementById("positional_details_text").innerHTML = '<p>Click on one of the selected positions to obtain more information</p>';
}

// Creates all graph elements based on the obj
function createGraph(obj) {
	$("#geneName").html(obj.geneName);
	
	// reset the Graph
	resetGraph();
	
	// Add defs to the svg
	var defs = main_svg.append("defs")
		.attr('class', 'defs');

	// Add clipping to defs
	main_svg.select('.defs').append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", main_width)
		.attr("height", main_heightLandscape);

	// Extract the various data
	var positional_annotation = obj.positional_annotation;
	var domain_data = obj.domains;

	// setting x/y domain according to data
	main_x.domain(d3.extent(positional_annotation, function(d) {
	    return d.protein_pos;
	}));
	main_y.domain([ 0, maxTolerance ]);
	main_x2.domain(main_x .domain());
	main_y2.domain(main_y.domain());

	// create a group from the tolerance data
	var dataGroup = d3.nest().key(function(d) {
	    return d.protein_pos;
	}).entries(positional_annotation);

	// add two consecutive data values per group, so these can be used in
	// drawing rectangles
	dataGroup.forEach(function(group, i) {
	    	group.values.push([]);
		if (i + 1 < dataGroup.length) {
		    group.values[1].protein_pos = dataGroup[i + 1].values[0].protein_pos;
		    group.values[1].sw_dn_ds = dataGroup[i + 1].values[0].sw_dn_ds;
		} else if (i < dataGroup.length) {
		    group.values[1].protein_pos = dataGroup[i].values[0].protein_pos;
		    group.values[1].sw_dn_ds = dataGroup[i].values[0].sw_dn_ds;
		}
		group.values[0].selected = false;
	})
	
	// Draw all individual user interface elements based on the data
	annotateDomains(domain_data, positional_annotation);
	createToleranceGraph(dataGroup);
	createToleranceGraphLegend();

	// Add schematic protein overview as a custom Axis
	createSchematicProtein(dataGroup);

	// Finally draw the context zoom
	addContextZoomView(positional_annotation);
	
	// Add behaviour according to the settings
	toggleToleranceLandscapeOrMetadomainLandscape();
}

function createClinVarTableHeader(){
    var html_table= '';
    // Define the header
    html_table += '<table class="table is-hoverable is-narrow">';
    html_table += '<thead><tr style="border-style:hidden;">';
    html_table += '<th><abbr title="Chromosome">Chr</abbr></th>';
    html_table += '<th><abbr title="Chromosome poition">Pos</abbr></th>';
    html_table += '<th><abbr title="Change of codon">Codon change</abbr></th>';
    html_table += '<th><abbr title="Change of residue">Residue change</abbr></th>';
    html_table += '<th><abbr title="Type of mutation">Type</abbr></th>';
    html_table += '<th><abbr title="ClinVar Identifier">ClinVar ID</abbr></th>';
    html_table += '</tr></thead><tfoot></tfoot><tbody>';
    return html_table;
}

function createGnomADTableHeader(){
    var html_table= '';
    // Define the header
    html_table += '<table class="table is-hoverable is-narrow">';
    html_table += '<thead><tr style="border-style:hidden;">';
    html_table += '<th><abbr title="Chromosome">Chr</abbr></th>';
    html_table += '<th><abbr title="Chromosome poition">Pos</abbr></th>';
    html_table += '<th><abbr title="Change of codon">Codon change</abbr></th>';
    html_table += '<th><abbr title="Change of residue">Residue change</abbr></th>';
    html_table += '<th><abbr title="Type of mutation">Type</abbr></th>';
    html_table += '<th><abbr title="Allele frequency">Allele Frequency</abbr></th>';
    html_table += '</tr></thead><tfoot></tfoot><tbody>';
    return html_table;
}

function createTableFooter(){
    return '</tbody></table>';
}

function createClinVarTableBody(chr, chr_pos, ref_codon, ref_residue, ClinvarVariants){
    var html_table= '';
    // here comes the data
    for (index = 0; index < ClinvarVariants.length; index++){
	variant = ClinvarVariants[index];
	html_table += '<tr>';
	html_table += '<td>'+chr+'</td>';
	html_table += '<td>'+chr_pos+'</td>';
	html_table += '<td>'+ref_codon+'>'+variant.alt_codon+'</td>';
	html_table += '<td>'+ref_residue+'>'+variant.alt_aa_triplet+'</td>';
	html_table += '<td>'+variant.type+'</td>';
	html_table += '<td><a href="https://www.ncbi.nlm.nih.gov/clinvar/variation/' + variant.clinvar_ID + '/" target="_blank">' + variant.clinvar_ID + '</a></td>';
	html_table += '</tr>';
    }
    	
    return html_table;
}

function createGnomADTableBody(chr, chr_pos, ref_codon, ref_residue, gnomADVariants){
    var html_table= '';
    // here comes the data
    for (index = 0; index < gnomADVariants.length; index++){
	variant = gnomADVariants[index];
	html_table += '<tr>';
	html_table += '<td>'+chr+'</td>';
	html_table += '<td>'+chr_pos+'</td>';
	html_table += '<td>'+ref_codon+'>'+variant.alt_codon+'</td>';
	html_table += '<td>'+ref_residue+'>'+variant.alt_aa_triplet+'</td>';
	html_table += '<td>'+variant.type+'</td>';
	html_table += '<td>' + parseFloat(variant.allele_count/variant.allele_number).toFixed(6) + '</td>';
	html_table += '</tr>';
    }
    	
    return html_table;
}

// Adds positional information for a selected position
function createPositionalInformation(position_data){
    // Reset the positional information 
    metadomain_svg.selectAll("*").remove();
    metadomain_svg = d3.select('#metadomain_svg');
    document.getElementById("positional_details_text").innerHTML = '';
    
    // Add information on position to the HTML
    document.getElementById("positional_details_text").innerHTML += '<label class="label">Chr: '+position_data.values[0].chr+', strand: '+position_data.values[0].strand+'</label>';
    document.getElementById("positional_details_text").innerHTML += '<label class="label">Gene: '+ position_data.values[0].chr_positions +'</label>';
    document.getElementById("positional_details_text").innerHTML += '<label class="label">Protein: p.'+ position_data.values[0].protein_pos +' '+ position_data.values[0].ref_aa_triplet+'</label>';
    document.getElementById("positional_details_text").innerHTML += '<label class="label">cDNA: '+ position_data.values[0].cdna_pos +' '+ position_data.values[0].ref_codon +'</label>';
    
    // Add clinvar at position information
    document.getElementById("positional_details_text").innerHTML += '<hr>';
    if ("ClinVar" in position_data.values[0]){
	document.getElementById("positional_details_text").innerHTML += '<label class="label">ClinVar SNVs at position:</label>';
	
	// Add ClinVar variant table
	document.getElementById("positional_details_text").innerHTML += createClinVarTableHeader()+ createClinVarTableBody(position_data.values[0].chr, position_data.values[0].chr_positions, position_data.values[0].ref_codon, position_data.values[0].ref_aa_triplet, position_data.values[0].ClinVar)+ createTableFooter();
    }
    else{
	document.getElementById("positional_details_text").innerHTML += '<label class="label">No ClinVar SNVs found at position</label>';
    }
    
    // Add meta domain variants
    document.getElementById("positional_details_text").innerHTML += '<hr>';
    var domain_information = "";
    var meta_domain_information = "";
    if (Object.keys(position_data.values[0].domains).length > 0){
	var domain_ids = '';
	var domain_id_list = Object.keys(position_data.values[0].domains);
	var n_domains_at_position = Object.keys(position_data.values[0].domains).length;
	
	for (i = 0; i < n_domains_at_position; i++){
	    if (i+1 == n_domains_at_position){
		domain_ids += '<a href="http://pfam.xfam.org/family/' + domain_id_list[i] + '" target="_blank">'+domain_id_list[i]+"</a>";
	    }	
	    else{
		domain_ids += '<a href="http://pfam.xfam.org/family/' + domain_id_list[i] + '" target="_blank">'+domain_id_list[i]+", </a>";
	    }
	    
	    // add meta domain information
	    if (!(position_data.values[0].domains[domain_id_list[i]] == null)){
		meta_domain_information += '<label class="label">Meta-domain information for domain '+domain_id_list[i]+':</label>';
		meta_domain_information += '<label class="label">Aligned to consensus position '+ position_data.values[0].domains[domain_id_list[i]].consensus_pos+', related to '+ position_data.values[0].domains[domain_id_list[i]].other_codons.length+' other codons throughout the genome</label>';
		
		
		var gnomAD_table = '<label class="label">Variants in gnomAD found in other codons throughout the genome:</label>';
		gnomAD_table += createGnomADTableHeader();
		var clinvar_table = '<label class="label">Pathogenic variants in ClinVar found in other codons throughout the genome:</label>';
		clinvar_table += createClinVarTableHeader();
		for (j = 0; j < position_data.values[0].domains[domain_id_list[i]].other_codons.length; j++){
		    var other_codon = position_data.values[0].domains[domain_id_list[i]].other_codons[j];
		    if (other_codon.normal_variants.length>0){
			gnomAD_table += createGnomADTableBody(other_codon.chr, other_codon.chr_positions+' ('+other_codon.strand+')', other_codon.ref_codon, other_codon.ref_aa_triplet, other_codon.normal_variants);
		    }
		    if (other_codon.pathogenic_variants.length>0){
			clinvar_table += createClinVarTableBody(other_codon.chr, other_codon.chr_positions+' ('+other_codon.strand+')', other_codon.ref_codon, other_codon.ref_aa_triplet, other_codon.pathogenic_variants);
		    }
		}
		
		// Add the footers
		clinvar_table += createTableFooter();
		gnomAD_table += createTableFooter();
		
		// Reset the tables if there are no variants
		if (position_data.values[0].domains[domain_id_list[i]].normal_variant_count == 0){
		    gnomAD_table = "";
		}
		if (position_data.values[0].domains[domain_id_list[i]].pathogenic_variant_count == 0){
		    clinvar_table = "";
		}
		
		// Add the meta-domain information to the domain information
		meta_domain_information += clinvar_table + gnomAD_table;
	    }
	    else{
		meta_domain_information += '<label class="label">No meta-domain information at position for domain '+domain_id_list[i]+'</label>';
	    }
	}
	
	// Add the domain info to the html element
	domain_information += '<label class="label">Position is part of protein domain(s): '+domain_ids+'</label>'
    }
    else{
	// Add the domain
	domain_information += '<label class="label">No protein domain information at position</label>';
    }
    
    // Add the domain and meta-domain information to the html element
    document.getElementById("positional_details_text").innerHTML += domain_information + meta_domain_information;
//  "(pos: "+d.values[0].metadomain.consensus_pos+")"
//    metadomain_svg.append("text")
//	.attr("class", "postionalInformation")
//	.attr("text-anchor", "right")
//		.attr("x", 0)
//		.attr("y", 50)
//		.attr("dy", 0)
//		.attr("font-size", "14px")
//	.style("fill", "black")
//	.text(function(d, i) {
//	    return position_data.values[0].chr_positions;
//	});
}

function drawMetaDomainInformation(domain_name, domain_id, start, stop, data){
    // reset the domain_details_svg
    domain_details_svg.selectAll("*").remove();
    domain_details_svg = d3.select('#domain_details_svg');
    
    // set the selected domain
    data.selected_domain = domain_id;
    
    // Call the tooltips
    domain_details_svg.call(domain_details_position_tip);
    
    // Activate the overlay
    $("#domain_information_overlay").addClass('is-active');
    
    // Format the HTML in the correct format
    document.getElementById("domain_information_overlay_title").innerHTML = '<label class="label" >'+document.getElementById("geneDetails").innerHTML +'</label><label class="label"> Domain: ' + domain_name+' (<a href="http://pfam.xfam.org/family/' + domain_id + '" target="_blank">' + domain_id + '</a>), located at p.'+start+' - p.'+stop+' </label><label class="label"> Meta-domain information</label>';
    
    // Add barplot for the normal variation
    var domain_details_BarPlotNormalVar = domain_details_svg.append("g")
    	.attr("transform", "translate(" + marginDomainDetailsNormalVar.left + "," + marginDomainDetailsNormalVar.top + ")");
    
    // Add barplot for the pathogenic variation
    var domain_details_BarPlotPathogenicVar = domain_details_svg.append("g")
	.attr("transform", "translate(" + marginDomainDetailsPathogenicVar.left + "," + marginDomainDetailsPathogenicVar.top + ")");
    
    // Define the axes domain based on the data
    domain_details_x.domain(data.map(function(d) { if (d.protein_pos >= start && d.protein_pos <= stop){ return d.protein_pos; }}));
    domain_details_normal_y.domain([0, d3.max(data, function(d) { if (d.protein_pos >= start && d.protein_pos <= stop && d.domains[domain_id] != null){ return d.domains[domain_id].normal_missense_variant_count;}})]);
    domain_details_pathogenic_y.domain([0, d3.max(data, function(d) {if (d.protein_pos >= start && d.protein_pos <= stop && d.domains[domain_id] != null){ return d.domains[domain_id].pathogenic_missense_variant_count; }})]);
    
    // Add the x-axis to the normal variation barplot
    domain_details_BarPlotNormalVar.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + domain_details_heightNormalVar + ")")
    .call(d3.axisBottom(domain_details_x));
    
    // Add the x-axis to the pathogenic variation barplot
    domain_details_BarPlotPathogenicVar.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + domain_details_heightPathogenicVar + ")")
    .call(d3.axisBottom(domain_details_x));

    // Add the y-axis to the normal variation barplot
    domain_details_BarPlotNormalVar.append("g")
        .attr("class", "axis axis--y")
        .call(d3.axisLeft(domain_details_normal_y))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("Missense Count");
    
    // Add the y-axis to the pathogenic variation barplot
    domain_details_BarPlotPathogenicVar.append("g")
        .attr("class", "axis axis--y")
        .call(d3.axisLeft(domain_details_pathogenic_y))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("Missense Count");
    
    // Draw the normal variation barplot
    domain_details_BarPlotNormalVar.selectAll(".bar")
      .data(data)
      .enter()
      .filter(function(d) { if (d.protein_pos >= start && d.protein_pos <= stop && d.domains[domain_id] != null){ return true } else {return false}})
      .append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return domain_details_x(d.protein_pos); })
        .attr("y", function(d) { return domain_details_normal_y(d.domains[domain_id].normal_missense_variant_count);})
        .attr("width", domain_details_x.bandwidth())
        .attr("height", function(d) { return domain_details_heightNormalVar - domain_details_normal_y(d.domains[domain_id].normal_missense_variant_count); })
        .style("fill", "green")
        .on("mouseover", function(d) {
              // show the tooltip
              domain_details_position_tip.show(d.domains[domain_id].normal_missense_variant_count);
              // amplify the element
              d3.select(this).style("fill", "orange");
              // move the element to front
              d3.select(this).moveToFront();
          })
          .on("mouseout", function(d) {
              // hide the tooltip
              domain_details_position_tip.hide(d);
              // reset the color
              d3.select(this).style("fill", "green");
              // move the element to the back
              d3.select(this).moveToBack();
          });
    
    // Draw the pathogenic variation barplot
    domain_details_BarPlotPathogenicVar.selectAll(".bar")
        .data(data)
        .enter()
        .filter(function(d) { if (d.protein_pos >= start && d.protein_pos <= stop && d.domains[domain_id] != null){ return true } else {return false}})
        .append("rect")
          .attr("class", "bar")
          .attr("x", function(d) { return domain_details_x(d.protein_pos); })
          .attr("y", function(d) { return domain_details_pathogenic_y(d.domains[domain_id].pathogenic_missense_variant_count); })
          .attr("width", domain_details_x.bandwidth())
          .attr("height", function(d) { return domain_details_heightPathogenicVar - domain_details_pathogenic_y(d.domains[domain_id].pathogenic_missense_variant_count); })
          .style("fill", "red")
          .on("mouseover", function(d) {
              // show the tooltip
              domain_details_position_tip.show(d.domains[domain_id].pathogenic_missense_variant_count);
              // amplify the element
              d3.select(this).style("fill", "orange");
              // move the element to front
              d3.select(this).moveToFront();
          })
          .on("mouseout", function(d) {
              // hide the tooltip
              domain_details_position_tip.hide(d);
              // reset the color
              d3.select(this).style("fill", "red");
              // move the element to the back
              d3.select(this).moveToBack();
          });    
}

/*******************************************************************************
 * Drawing user interface component
 ******************************************************************************/

// Draw the tolerance graph
function createToleranceGraph(dataGroup) {
	// append focus view
	var focus = main_svg.append("g")
		.attr("class", "focus")
		.attr("id", "tolerance_graph")
		.attr("transform", "translate(" + main_marginLandscape.left + "," + main_marginLandscape.top + ")");
	
	// draw the tolerance area graph, base on the grouped consecutive data
	// values
	dataGroup.forEach(function(d) {
	    // add the area specific for this position
	    focus.append("path").datum(d.values)
	    	.attr("class", "area")
	    	.attr("d", toleranceArea);

	    // create a linear gradient, specific for this position
	    var lineargradient = main_svg.append("linearGradient")
	    	.attr("id", "area-gradient_" + d.values[0].protein_pos + "-" + d.values[1].protein_pos)
	    	.attr("x1", "0%")
		.attr("y1", "0%")
		.attr("x2", "100%")
		.attr("y2", "0%");

	    // calculate the offset start score
	    lineargradient.append("stop")
	    	.attr("class", "start")
	    	.attr("offset", "0%")
	    	.attr("stop-color", tolerance_color(d.values[0].sw_dn_ds));

	    // calculate the offset stop score
	    lineargradient.append("stop")
	    	.attr("class", "end")
	    	.attr("offset", "100%")
	    	.attr("stop-color", tolerance_color(d.values[1].sw_dn_ds));
	});

	// color the area under the curve in contrast to the tolerance score
	focus.selectAll(".area")
		.style("fill", function(d, i) {
		    return "url(#area-gradient_" + d[0].protein_pos + "-" + d[1].protein_pos + ")";
		});

	// add tolerance line
	focus.append('path').datum(dataGroup)
		.attr('class', 'line')
		.attr('id', 'toleranceLine')
		.attr('fill', 'none')
		.attr("stroke", "steelblue")
		.attr('stroke-width', "2px")
		.style("clip-path", "url(#clip)")
		.attr('d', toleranceLine);

	// append yAxis for focus view
	focus.append("g").attr("class", "axis axis--y").call(main_yAxis);
}

// Draw the axis and labels
function createSchematicProtein(groupedTolerance) {
	// Add the Axis
	var focusAxis = main_svg.append("g")
		.attr("class", "focusAxis")
		.attr("id", "tolerance_axis");

	// Add the elements that will be drawn
	var focusAxiselements = focusAxis.selectAll("g")
		.data(groupedTolerance).enter()
		.append("g")
		.attr("class", "focusAxisElement")
		.attr("transform", "translate(" + main_marginPositionInfo.left + ","	+ main_marginPositionInfo.top + ")")
		.style("fill", "none");

	// Call the tooltips
	main_svg.call(positionTip);

	focusAxiselements.append("rect")
	.attr("class", "toleranceAxisTickBackground")
	.attr("x", function(d, i) {
	    return main_x(d.values[0].protein_pos - 0.5);
	}).attr("y", 0).attr("width", function(d, i) {
	    if (d.values[1].protein_pos != d.values[0].protein_pos){
		return main_x(d.values[1].protein_pos) - main_x(d.values[0].protein_pos);
	    } else {
		return main_x(d.values[1].protein_pos +1) - main_x(d.values[0].protein_pos);
	    }
	})
	.attr("height", main_heightMarginPositionInfo)
	.style("fill", "white")
	.style("clip-path","url(#clip)");
	
	// Add a text per position
	focusAxiselements.append("text")
		.attr("class", "toleranceAxisTickLabel")
		.attr("id", function(d, i) {
		    return "toleranceAxisText_" + d.values[0].protein_pos;
		})
		.attr("x", function(d, i) {
		    return main_x(d.values[0].protein_pos);
		})
		.attr("y", main_heightMarginPositionInfo / 2)
		.attr("dy", ".35em")
		.style('pointer-events', 'none')
		.style('user-select', 'none')
		.attr("text-anchor", "middle")
		.style("fill", "black")
		.style("clip-path", "url(#clip)")
		.text(function(d, i) {
		    return d.values[0].protein_pos;
		});

	// Add a rectangle per position
	focusAxiselements.append("rect")
		.attr("class", "toleranceAxisTick")
		.attr("id", function(d, i) {
		    return "toleranceAxisRect_" + d.values[0].protein_pos;
		})
		.attr("x", function(d, i) {
		    return main_x(d.values[0].protein_pos - 0.5);
		}).attr("y", 0).attr("width", function(d, i) {
		    if (d.values[1].protein_pos != d.values[0].protein_pos){
			return main_x(d.values[1].protein_pos) - main_x(d.values[0].protein_pos);
		    } else {
			return main_x(d.values[1].protein_pos +1) - main_x(d.values[0].protein_pos);
		    }
		})
		.attr("height", main_heightMarginPositionInfo)
		.style("fill-opacity", 0.2)
		.style("fill", "grey")
		.style("clip-path","url(#clip)")
		.on("mouseover", function(d, i) {
		    if (!d.values[0].selected) {
			d3.select(this).style("fill", "orange").style("fill-opacity", 0.5);
		    }
		    // show the tooltip
		    positionTip.show(d);
		    // change the cursor
		    d3.select(this).style("cursor", "pointer");
		}).on("mouseout", function(d, i) {
		    if (!d.values[0].selected) {
			d3.select(this).style("fill-opacity", 0.2);
			d3.select(this).style("fill", "grey");
		    }
		    // hide the tooltip
		    positionTip.hide(d);
		}).on("click", function(d, i) {
		    if (!d.values[0].selected) {
			d3.select(this).style("fill", "red").style("fill-opacity", 0.7);
			d.values[0].selected = true;			
			addRowToPositionalInformationTable(d);
			selected_positions += 1;
			$("#selected_positions_information").removeClass('is-hidden');
		    } else {
			d3.select(this).style("fill", "orange").style("fill-opacity", 0.5);
			d.values[0].selected = false;
			d3.select("#positional_table_info_" + d.values[0].protein_pos).remove();

			selected_positions -= 1;
			if (selected_positions <= 0){
			    $("#selected_positions_information").addClass('is-hidden');
			}
		    }
		});
}

// Draw the domain annotation
function annotateDomains(protDomain, tolerance_data) {
	// append domain view
	var domains = main_svg.append("g")
		.attr("class", "domains")
		.attr("id", "domain_annotation")
		.attr("transform", "translate(" + main_marginAnnotations.left + "," + main_marginAnnotations.top + ")");

	// Add text to the ui element
	main_svg.append("text")
		.attr("text-anchor", "left")
		.attr("x", 0).attr("y", main_marginAnnotations.top + (main_heightAnnotations*(3/5))).attr("dy", 0)
		.attr("class", "label")
		.text("Protein")
		.style('pointer-events', 'none')
		.style('user-select', 'none');

	// Call the tooltips
	main_svg.call(domainTip);

	// Fill the ui element
	domains.selectAll(".rect")
		.data(protDomain).enter()
		.append("rect").attr("class", "pfamDomains")
		.attr("x", function(d) {
		    return main_x(d.start - 0.5);
		})
		.attr("y", 0)
		.attr("width", function(d) {
		    return main_x(d.stop + 1) - main_x(d.start);
		})
		.attr("height", main_heightAnnotations)
		.attr("rx", 10)
		.attr("ry", 10)
		.style('opacity', 0.5)
		.style('fill', '#c014e2')
		.style('stroke', 'black')
		.style("clip-path", "url(#clip)")
		.on("mouseover", function(d) {
		    // show the tooltip
		    domainTip.show(d);
		    // amplify the element
		    d3.select(this).style("fill", "yellow");
		    // move the element to front
		    d3.select(this).moveToFront();
		    // change the cursor
		    d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function(d) {
		    // hide the tooltip
		    domainTip.hide(d);
		    // reset the color
		    d3.select(this).style("fill", "#c014e2");
		    // move the element to the back
		    d3.select(this).moveToBack();
		    // change the cursor
		    d3.select(this).style("cursor", "default");
		})
		.on("click", function(d) {
		    drawMetaDomainInformation(d.Name, d.ID, d.start, d.stop, tolerance_data)
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

// Draw the context area for zooming
function addContextZoomView(tolerance) {
	// add the brush element
	var brush = d3.brushX()
		.extent([ [ 0, 0 ], [ main_width, main_heightContext ] ])
		.on("brush end", brushed);

	// append context view
	var context = main_svg.append("g")
		.attr("class", "context")
		.attr("id", "zoom_landscape")
		.attr("transform", "translate(" + main_marginContext.left + "," + main_marginContext.top + ")");

	// append context area
	context.append("path")
		.datum(tolerance)
		.style("fill", "grey")
		.style("clip-path", "url(#clip)")
		.attr("d", contextArea);

	// append xAxis for context view
	context.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," + main_heightContext + main_marginContext.top + ")")
		.call(main_xAxis);

	// append yAxis for context view
	context.append("g")
		.attr("class", "brush")
		.call(brush)
		.call(brush.move, main_x2.range());

	main_svg.append("text")
		.attr("text-anchor", "left")
		.attr("x", 0)
		.attr("y", main_marginContext.top + 50)
		.attr("dy", 0)
		.attr("class", "label")
		.text("Zoom-in")
		.style('pointer-events', 'none')
		.style('user-select', 'none');

	// Define the brushed function
	function brushed() {
		var s = d3.event.selection || main_x2.range();
		main_x.domain(s.map(main_x2.invert, main_x2));
		rescaleLandscape();
	}
}

// Draw the legend for the Tolerance graph
function createToleranceGraphLegend() {
	// append gradient to defs
	var legendGradient = main_svg.select('.defs')
		.append("linearGradient")
		.attr("id", "legendGradient")
		.attr("x1", "0%")
		.attr("y1", "100%")
		.attr("x2", "0%")
		.attr("y2", "0%");

	// set legend of the tolerance score
	legendGradient.selectAll("stop").data(toleranceColorGradient).enter()
		.append("stop")
		.attr("offset", function(d) {
		    return d.offset;
		})
		.attr("stop-color", function(d) {
		    return d.color;
		});

	// append heatmap legend
	main_svg.append("rect")
		.attr("id", "legendGradientRect")
		.attr("width", main_widthLegend)
		.attr("height", main_heightLandscape)
		.attr("transform", "translate(" + main_marginLegend.left + "," + main_marginLegend.top + ")")
		.style("fill", "url(#legendGradient)");

	var context = main_svg.append("g")
		.attr("class", "context")
		.attr("id", "zoom_landscape")
		.attr("transform", "translate(" + main_marginContext.left + "," + main_marginContext.top + ")");

	// append legend text
	main_svg.append("text")
		.attr("text-anchor", "middle")
		.attr("x", -50)
		.attr("y", 15)
		.attr("dy", 0)
		.attr("class", "label legendGradientText")
		.attr("transform", "rotate(-90)")
		.text("Tolerant")
		.style('pointer-events', 'none')
		.style('user-select', 'none');

	// append legend text
	main_svg.append("text")
		.attr("text-anchor", "middle")
		.attr("x", -150)
		.attr("y", 15)
		.attr("dy", 0)
		.attr("class", "label legendGradientText")
		.attr("transform", "rotate(-90)")
		.text("Neutral")
		.style('pointer-events', 'none')
		.style('user-select', 'none');

	// append legend text
	main_svg.append("text")
		.attr("text-anchor", "middle")
		.attr("x", -250)
		.attr("y", 15)
		.attr("dy", 0)
		.attr("class", "label legendGradientText")
		.attr("transform", "rotate(-90)")
		.text("Intolerant")
		.style('pointer-events', 'none')
		.style('user-select', 'none');
}

/*******************************************************************************
 * Interactive behaviour functions
 ******************************************************************************/

// Allows toggling between the tolerance landscape and metadomain landscape
function toggleToleranceLandscapeOrMetadomainLandscape(){
    var tolerance_graph = d3.select("#tolerance_graph");
    var legend = d3.select("#legendGradientRect");
    var legend_text = d3.selectAll(".legendGradientText");

    switch($('input[name=landscape_checkbox]:checked', '#checkbox_for_landscape').val()){
        case "metadomain_landscape":
            tolerance_graph.style("opacity", 0);
            legend.style("opacity", 0);
            legend_text.style("opacity", 0);
            break;
        case "tolerance_landscape":
            tolerance_graph.style("opacity", 1);
            legend.style("opacity", 1);
            legend_text.style("opacity", 1);
            break;
	default:
	    break;
    }
}

// Update the positional information table with new values
function addRowToPositionalInformationTable(d) {
	var new_row = d3.select('#position_information_tbody').append('tr').attr('class', 'tr').attr("id", "positional_table_info_" + d.values[0].protein_pos);
	
	new_row.append('th').text(d.values[0].protein_pos);
	new_row.append('td').text(d.values[0].ref_aa_triplet);

	var domain_ids = "-";
	var clinvar_at_pos = "-";
	var related_gnomad = "-";
	var related_clinvar = "-";
	
	// Add clinvar at position information
	if ("ClinVar" in d.values[0]){
	    clinvar_at_pos = ""+d.values[0].ClinVar.length;
	}
	else{
	    clinvar_at_pos = "0";
	}
	
	// add domain and metadomain information to the information
	if (Object.keys(d.values[0].domains).length > 0){
	    var domain_id_list = Object.keys(d.values[0].domains);
	    var n_domains_at_position = Object.keys(d.values[0].domains).length;
	    domain_ids = "";
	    related_gnomad = 0;
	    related_clinvar = 0;
	    for (i = 0; i < n_domains_at_position; i++){
		if (i+1 == n_domains_at_position){
		    domain_ids += domain_id_list[i];
		}	
		else{
		    domain_ids += domain_id_list[i]+", ";
		}
		// append normal and pathogenic variant count
		if (!(d.values[0].domains[domain_id_list[i]] == null)){
    		    related_gnomad += d.values[0].domains[domain_id_list[i]].normal_variant_count;
    		    related_clinvar += d.values[0].domains[domain_id_list[i]].pathogenic_variant_count;
		}
	    }
	}
	new_row.append('td').text(domain_ids);
	new_row.append('td').text(clinvar_at_pos);
	new_row.append('td').text(related_gnomad);
	new_row.append('td').text(related_clinvar);
	
	// Add interactiveness to the rows
	new_row.on("click", function() {
	    d3.selectAll('.tr').classed("is-selected", false);
	    d3.select(this).classed("is-selected", true);
	    createPositionalInformation(d);
	}).on("mouseover", function(d, i) {
	    d3.select(this).style("cursor", "pointer");
	});
		
	// Sort the table to the protein positions
	sortTable();
}

function sortTable(){
    var rows = $('#position_information_tbody tr').get();

    rows.sort(function(a, b) {
        var A = parseInt($(a).children('th').eq(0).text());
        var B = parseInt($(b).children('th').eq(0).text());
    
        if(A < B) {
          return -1;
        }
    
        if(A > B) {
          return 1;
        }
    
        return 0;
    });

    $.each(rows, function(index, row) {
      $('#position_information_tbody').append(row);
    });
  }

// Rescale the landscape for zooming or brushing purposes
function rescaleLandscape(){
    var focus = d3.select("#tolerance_graph");
    focus.selectAll(".area").attr("d", toleranceArea);
    focus.select(".line").attr("d", toleranceLine);
    focus.select(".axis--x").call(main_xAxis).selectAll("text").remove();

    var focusAxis = d3.select("#tolerance_axis");

    focusAxis.selectAll(".toleranceAxisTick").attr("x", function(d, i) {
	return main_x(d.values[0].protein_pos - 0.5);
    	})
    	.attr("width", function(d, i) {
    	    if (d.values[1].protein_pos != d.values[0].protein_pos){
		return main_x(d.values[1].protein_pos) - main_x(d.values[0].protein_pos);
    	    } else {
    		return main_x(d.values[1].protein_pos +1) - main_x(d.values[0].protein_pos);
    	    }
	});

    focusAxis.selectAll(".toleranceAxisTickBackground").attr("x", function(d, i) {
	return main_x(d.values[0].protein_pos - 0.5);
    	})
    	.attr("width", function(d, i) {
    	    if (d.values[1].protein_pos != d.values[0].protein_pos){
		return main_x(d.values[1].protein_pos) - main_x(d.values[0].protein_pos);
    	    } else {
    		return main_x(d.values[1].protein_pos +1) - main_x(d.values[0].protein_pos);
    	    }
	});
    
    focusAxis.selectAll(".toleranceAxisTickLabel")
    	.attr("x", function(d, i) {
    	    return main_x(d.values[0].protein_pos);
	})
	.attr("text-anchor", "middle")
	.style("opacity", function(d, i) {
	    var textwidth = d3.select('#toleranceAxisText_' + d.values[0].protein_pos).node().getComputedTextLength();
	    var rectwidth = d3.select('#toleranceAxisRect_' + d.values[0].protein_pos).node().width.animVal.value;
	    if ((textwidth *0.75) >= rectwidth) {
		return 0;
	    } else if ((textwidth * 0.9) >= rectwidth) {
		return 0.1;
	    } else if ((textwidth * 1.0) >= rectwidth) {
		return 0.4;
	    } else if ((textwidth * 1.25) >= rectwidth) {
		return 0.5;
	    } else if ((textwidth * 1.5) >= rectwidth) {
		return 0.7;
	    }
	    return 1;
	});

    var domains = d3.select("#domain_annotation");
    domains.select(".axis--x").call(main_xAxis);
    domains.selectAll(".pfamDomains")
    	.attr("x", function(d) {
    	    return main_x(d.start - 0.5);
    	})
    	.attr("width", function(d) {
    	    return main_x(d.stop + 1) - main_x(d.start);
	});
    domains.selectAll(".clinvar")
    	.attr("x1", function(d) { 
    	    return main_x(d.protein_pos);
	})
	.attr("x2", function(d) {
	    return main_x(d.protein_pos);
	});
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