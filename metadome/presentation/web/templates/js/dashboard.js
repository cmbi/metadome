/**
 * Controls all responsiveness for the tolerance.html page
 */

// This function allows clicking events to be raised on d3js elements
jQuery.fn.d3Click = function () {
  this.each(function (i, e) {
    var evt = new MouseEvent("click");
    e.dispatchEvent(evt);
  });
};

$("#geneName").keyup(function(event) {
    if (event.keyCode === 13) {
        $("#getTranscriptsButton").click();
    }
});

function get_query_param(param) {
	var result =  window.location.search.match(
			new RegExp("(\\?|&)" + param + "(\\[\\])?=([^&]*)"));
    return result ? result[3] : false;
}

function show_tour_data_input(index) {
    switch (index) {
    case 0:// reset
    	tour_reset_gene_name();
    	break;
    case 1: // gene input
    	// ensure no interaction is possible
		document.getElementById("retrieve_transcripts_control").setAttribute("style", "pointer-events: none;");
		document.getElementById("start_analysis_control").setAttribute("style", "pointer-events: none;");

    	//reset
    	document.getElementById("geneNameHelpMessage").innerHTML = "";
    	
    	// behaviour
    	tour_fill_gene_name();
    	break;
    case 2: // messages after get transcripts
    	//reset
    	resetDropdown();
    	
    	// behaviour
    	tour_fill_succes_message_transcripts();
    	break;
    case 3: // start analysis
    	// reset
    	$("#loading_overlay").removeClass('is-active');
    	
    	// behaviour
    	tour_fill_transcripts();
    	break;
    case 4: // loading overlay
    	// reset
		$("#toleranceGraphContainer").addClass('is-hidden');
		$("#graph_control_field").addClass('is-hidden');
		$("#selected_positions_information").addClass('is-hidden');
    	
    	// behaviour
    	$("#loading_overlay").addClass('is-active');
    	break;
    case 5: // fill the graph
    	$("#loading_overlay").removeClass('is-active');
    	tour_fill_graph_example();
    	break;
    case 7:
    	// resets
    	resetZoom();
    	break;
    case 8: // zooming explanation
    	// resets
    	resetZoom();
    	tour_turn_clinvar_variants_off();
    	tour_check_default_visualization();toggleToleranceLandscapeOrMetadomainLandscape();
		document.getElementById("graph_control_field_checkboxes").setAttribute("style", "pointer-events: none;");
		break;
    case 9: // landscape modes
    	// resets
    	resetZoom();
    	tour_turn_clinvar_variants_off();
    	
    	// behaviour
    	window.setTimeout(tour_check_alternative_visualization, 500);
    	window.setTimeout(toggleToleranceLandscapeOrMetadomainLandscape,1000);
    	window.setTimeout(tour_check_default_visualization, 2200);
    	window.setTimeout(toggleToleranceLandscapeOrMetadomainLandscape,2200);
		document.getElementById("graph_control_field_checkboxes").removeAttribute("style", "pointer-events: none;");
    	break;
    case 10: // clinvar variants
    	// resets
		document.getElementById("graph_control_field_checkboxes").removeAttribute("style", "pointer-events: none;");
    	resetZoom();
    	
    	// behaviour
    	tour_switch_clinvar_variants();
    	window.setTimeout(tour_switch_clinvar_variants,1200);
    	break;
    case 11: // explanation of schematic protein
    	// resets
    	tour_check_default_visualization();
    	tour_turn_clinvar_variants_off();
    	tour_unselect_position_in_domain();
    	resetZoom();
		document.getElementById("graph_control_field_checkboxes").setAttribute("style", "pointer-events: none;");
    	break;
    case 12: // positional information
    	// resets
    	resetZoom();
    	tour_turn_clinvar_variants_off();
    	
    	// Behaviour
    	window.setTimeout(tour_select_position_in_domain, 500);
    	break;
    }
}

function tour_turn_clinvar_variants_off(){
	if ($('#clinvar_checkbox').is(':checked') == true ){
		tour_switch_clinvar_variants();
	}
}

function tour_switch_clinvar_variants(){
	$('#clinvar_checkbox').trigger( "click" );
}

function tour_switch_clinvar_variants_off(){
	$('#clinvar_checkbox').trigger( "click" );
}

function tour_unselect_position_in_domain(){
	var tour_selected_position;
	d3.select('#toleranceAxisRect_68').attr("element_is_selected",function(d,i){ tour_selected_position = d.values[0].selected});
	
	if (tour_selected_position){
		tour_trigger_position_of_interest();
	}
}

function tour_select_position_in_domain(){
	var tour_selected_position;
	d3.select('#toleranceAxisRect_68').attr("element_is_selected",function(d,i){ tour_selected_position = d.values[0].selected});
	
	if (!tour_selected_position){
		tour_trigger_position_of_interest();
	}
}

function tour_trigger_position_of_interest(){
	$('#toleranceAxisRect_68').d3Click();
}

function tour_check_default_visualization(){
	$('#checkbox_for_landscape_default').prop('checked', true);
}
function tour_check_alternative_visualization(){
	$('#checkbox_for_landscape_alternative').prop('checked', true);
}

function tour_fill_gene_name(){
	$('#geneName').val('T');
}
function tour_reset_gene_name(){
	$('#geneName').val('');
}

function tour_fill_succes_message_transcripts(){
	document.getElementById("geneNameHelpMessage").innerHTML = "Retrieved transcripts for gene 'T'";
	$("#geneNameHelpMessage").removeClass('is-danger');
	$("#geneNameHelpMessage").addClass('is-success');
}

function tour_fill_transcripts(){
	clearDropdown();
	$("#getToleranceButton").addClass('is-info');
	$("#getToleranceButton").removeClass('is-static');
	var dropdown = document.getElementById("gtID");
	dropdown.setAttribute('class', 'dropdown');
	var opt = new Option();
	opt.value = 1;
	opt.text = "ENST00000296946.2 (435aa)";
	dropdown.options.add(opt);
}

function tour_fill_graph_example(){
	// Retrieve the example json to fill in the graph
	$.getJSON("{{ url_for('static', filename='json/example_T_gene.json') }}", function(json) {	    
		document.getElementById("toleranceGraphContainer").setAttribute("style", "pointer-events: none;");
		$("#toleranceGraphContainer").removeClass('is-hidden');
	    $("#graph_control_field").removeClass('is-hidden');
	    var geneName = document.getElementById("geneName").value;
	    var geneDetails = document.getElementById("geneDetails");
	    geneDetails.innerHTML = 'Gene: '+json.gene_name+' (transcript: <a href="http://grch37.ensembl.org/Homo_sapiens/Transcript/Summary?t='+json.transcript_id+'" target="_blank">'+json.transcript_id+'</a>, protein: <a href="https://www.uniprot.org/uniprot/'+json.protein_ac+'" target="_blank">'+json.protein_ac+'</a>)';
	    createGraph(json);
	    // disable any mouse events on the elements
		document.getElementById("graph_control_field_buttons").setAttribute("style", "pointer-events: none;");
		document.getElementById("graph_control_field_checkboxes").setAttribute("style", "pointer-events: none;");
		document.getElementById("selected_positions_information").setAttribute("style", "pointer-events: none;");
	});
}

//Setup tour
var tour = new Tour({
  backdrop: true,
  orphan: true,
  storage: false,
  onNext: function (tour) {
    show_tour_data_input(tour.getCurrentStep() + 1)
  },
  onPrev: function (tour) {
    show_tour_data_input(tour.getCurrentStep() - 1)
  },
  onEnd: function (tour) {  window.location.reload(true); window.location.replace("{{ url_for('web.dashboard') }}");},
  steps: [
	  {
		element: "",
		title: "Start Tour",
		content: "Welcome to MetaDome.<br><br>"+
				"This tour explains the usage of MetaDome "+
				"via an example.<br><br>"+
				"You can click 'end tour' any time to start "+
				"analysing your own gene of interest. " +
				"<br><br>Click next to begin."
	  },
	  {
	    element: "#retrieve_transcripts_control",
	    title: "Gene of interest",
	    content: "Input here your gene name of interest Then you" +
	    		" can click the 'Get Transcripts' button to " +
	    		"retrieve all the transcripts for your gene of " +
	    		"interest.<br><br> For this example we fill in " +
	    		"the 'T' gene."
	  },
	  {
		element: "#geneNameHelpMessage",
		title: "Get Transcripts",			
		content: "After clicking the 'Get Transcripts' button, we "+
				"check if there are any transcripts available for "+
				"your gene of interest.<br><br>"+
				"If the gene was not present in our database you " +
				"would have seen the following message:<br><br>" +
				"<div class='help is-danger'>No transcripts " +
				"available in database for gene 'T'</div>"				
	  },
	  {
		element: "#start_analysis_control",
		title: "Select transcript & analyse your protein",
		content: "Select the transcript of your interest from this "+
				"dropdown menu. You can than click the 'Analyse " +
				"Protein' button to start the analysis."
	  },
	  {
		element: "#loading_overlay",
		title: "Loading screen",
		content: "This analysis may take between 5 minutes and up " +
				"to an hour to complete, but in this example: <br><br>" +
				"<b>you can click next to continue</b>. <br><br> " +
				"Luckily all results are stored after they "+
				"complete, so the next time you query the same " +
				"transcript it will load in a matter of seconds."
	  },
	  {
		element: "#content",
		title: "Analysis results",
		content: "When the analysis completes, you obtain a "+
				"wealth of information. <br><br> But don't worry, " +
				"we will now go over each part in detail.",
	  },
	  {
		element: "#graph_control_field",
		title: "Graph Control",
		content: "Here, you may switch between different " +
				"representations of the analysis result visualizations," +
				" download the current view as an '.svg', reset any " +
				"zooming of the graph or select, or display any known " +
				"ClinVar variants.",
	  },
	  {
		element: "#landscape_svg",
		title: "Visualization",
		content: "Here you may find the visualization of your results." +
				"It is a graphic representation of the protein of your " +
				"transcript of interest.<br><br> By default the " +
				"metadomain variants are displayed.",
	  },
	  {
		element: "#schematic_protein_zoom_text",
		title: "Zooming in",
		content: "You can zoom in on regions of your interest by " +
				"clicking anywhere in the gray area and dragging " +
				"the mouse. If you just click on any part in the " +
				"protein the zooming is reset.<br><br> Go ahead " +
				"and try for yourself",
		placement: 'left',
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#checkbox_for_landscape",
		title: "Switching between visualizations",
		content: "Here you can switch between the 'Meta-domain " +
				"Landscape' and the 'Tolerance Landscape' " +
				"visualization modes.<br><br> Go ahead " +
				"and try for yourself",
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#clinvar_checkbox",
		title: "Switching ClinVar variants",
		content: "Here you can toggle the display of any ClinVar " +
				"variants for your gene of interest. <br><br> Go ahead " +
				"and try for yourself",
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#tolerance_axis",
		title: "Schematic protein representation",
		content: "For each gene a schematic protein is displayed for " +
				"all the positions and the presence of any Pfam protein " +
				"domains is annotated.<br><br> Here each position is " +
				"hoverable and selectable. If you click a position you " +
				"obtain much more information about it.",
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#toleranceAxisRect_68",
		title: "Selecting positions of interest",
		content: "If you click a position it will become highlighted. " +
				"And you may view more detailed information for that " +
				"position.",
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#selected_positions_information",
		title: "More info for a selected position",
		content: "All the highlighted positions that you have selected " +
				"will be put into this list. Here a short overview is " +
				"displayed on any known gnomAD or ClinVar variants " +
				"present at this position. Also variants that are " +
				"homologously related to this position are displayed " +
				"if the position is part of a Pfam protein domain." +
				"<br><br> Clicking a selected position provides a " +
				"pop-up with even more details.",
	  },
]});
tour.init();

// Start the tour automatically if redirected to the index page via the
// help button.
if (get_query_param('tour')) {
	tour.restart();
}

// Function to send AJAX request to the webserver to get all transcripts
// belonging to a gene name
function getTranscript() {
	clearTranscripts();
	var geneName = document.getElementById("geneName").value;
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var transcript_id_results = JSON.parse(xhttp.responseText);
			document.getElementById("geneNameHelpMessage").innerHTML = transcript_id_results.message;

			if (typeof transcript_id_results == 'undefined' || transcript_id_results == null || transcript_id_results.trancript_ids.length == 0) {
				$("#geneName").addClass('is-danger');
				$("#geneName").removeClass('is-success');
				$("#geneNameHelpMessage").addClass('is-danger');
				$("#geneNameHelpMessage").removeClass('is-success');
				$("#getToleranceButton").addClass('is-static');
				$("#getToleranceButton").removeClass('is-info');
				resetDropdown()
			} else {
				clearDropdown();
				$("#geneName").addClass('is-success');
				$("#geneName").removeClass('is-danger');
				$("#geneNameHelpMessage").addClass('is-success');
				$("#geneNameHelpMessage").removeClass('is-danger');
				$("#getToleranceButton").addClass('is-info');
				$("#getToleranceButton").removeClass('is-static');
				var dropdown = document.getElementById("gtID");
				dropdown.setAttribute('class', 'dropdown');
				// Sort the results by sequence length
				transcript_id_results.trancript_ids.sort(function(a,b){return (a.aa_length<b.aa_length) ? 1 : ((b.aa_length<a.aa_length) ? -1: 0);});
				
				// Add the transcripts as options
				for (i = 0; i < transcript_id_results.trancript_ids.length; i++) {
					var opt = new Option();
					opt.value = i;
					opt.text = transcript_id_results.trancript_ids[i].gencode_id + " ("+ transcript_id_results.trancript_ids[i].aa_length +"aa)" ;
					
					if (!transcript_id_results.trancript_ids[i].has_protein_data){
						opt.disabled = true;
					}
					
					dropdown.options.add(opt);
				}
			}
		}
	};
	if (typeof geneName !== 'undefined' && geneName.length > 0) {
		// the variable is defined
		xhttp.open("GET", "{{ url_for('api.get_default_transcript_ids') }}"
				+ "/" + geneName, true);
		xhttp.setRequestHeader("Content-type",
				"application/x-www-form-urlencoded");
		xhttp.send();
	}
}

// function to clear all items in the transcript dropdown
function clearDropdown() {
	var dropdown = document.getElementById("gtID");
	for (var i = dropdown.options.length - 1; i >= 0; i--) {
		dropdown.remove(i);
	}
	dropdown.disabled = false;
}

function resetDropdown() {
	clearDropdown()

	var dropdown = document.getElementById("gtID");
	dropdown.disabled = true;

	var opt = new Option();
	opt.value = "";
	opt.disabled = true;
	opt.selected = true;
	opt.hidden = true;
	opt.text = "Please first retrieve the transcripts";
	dropdown.options.add(opt);
}

function resetGraphControl(){
	document.getElementById("clinvar_checkbox").checked = false;
	document.getElementById("checkbox_for_landscape_default").checked = true;
}

function clearTranscripts() {
	resetDropdown();
	resetGraph();
	resetGraphControl();
	$("#getToleranceButton").addClass('is-static');
	$("#getToleranceButton").removeClass('is-info');
	$("#geneName").removeClass('is-success');
	$("#advanced_options").addClass("is-hidden");
	$("#toleranceGraphContainer").addClass('is-hidden');
    	document.getElementById("geneNameHelpMessage").innerHTML = "";
	$("#graph_control_field").addClass('is-hidden');
}

function saveSvg(svgEl, name) {
    svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    var svgData = svgEl.outerHTML;
    var preface = '<?xml version="1.0" standalone="no"?>\r\n';
    var svgBlob = new Blob([preface, svgData], {type:"image/svg+xml;charset=utf-8"});
    var svgUrl = URL.createObjectURL(svgBlob);
    var downloadLink = document.createElement("a");
    downloadLink.href = svgUrl;
    downloadLink.download = name+'.svg';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Function to get the data from the inputfield and send AJAX requests to the
// webserver, returning arrays with json objects.
function loadDoc() {
    resetGraphControl();
	var selection = document.getElementsByClassName("dropdown")[0];

	if (typeof selection !== 'undefined' && selection !== null && selection.length > 0) {
		$("#loading_overlay").addClass('is-active');
		var input = selection.options[selection.selectedIndex].text;
		var gtID = input.toUpperCase();

		var status = true;
		if (gtID == "") {
			status = false
		}
		if (status) {

			var xhttp = new XMLHttpRequest();
			xhttp.onreadystatechange = function() {
				if (this.readyState == 4 && this.status == 200) {
					var obj = JSON.parse(xhttp.responseText);
					if (typeof obj == 'undefined' || obj == null || obj.length == 0) {
						d3.select("svg").selectAll("*").remove();
						$("#graph_control_field").addClass('is-hidden');
						$("#toleranceGraphContainer").addClass('is-hidden');
						$("#loading_overlay").removeClass('is-active');
					} else {
						// check if the job is done or we are retrieving the results of a job
						if( obj.job_id != null && obj.job_name != null){
							if (obj.status == 'SUCCESS'){
								// if the status is SUCCESS, retrieve the results
								xhttp.open("GET",
										"{{ url_for('api.get_job_result_stub') }}" + "/"
												+ obj.job_name + "/"
												+ obj.job_id + "/", true);
								xhttp.setRequestHeader("Content-type",
										"application/x-www-form-urlencoded");
								xhttp.send();
							}
							else{								
								// check status
								xhttp.open("GET",
										"{{ url_for('api.get_job_status_stub') }}" + "/"
												+ obj.job_name + "/"
												+ obj.job_id + "/", true);
								xhttp.setRequestHeader("Content-type",
										"application/x-www-form-urlencoded");
								xhttp.send();
							}
						}
						else{
							$("#loading_overlay").removeClass('is-active');
							
							$("#toleranceGraphContainer").removeClass('is-hidden');
							$("#graph_control_field").removeClass('is-hidden');
							var geneName = document.getElementById("geneName").value;
							var geneDetails = document.getElementById("geneDetails");
							geneDetails.innerHTML = 'Gene: '+obj.gene_name+' (transcript: <a href="http://grch37.ensembl.org/Homo_sapiens/Transcript/Summary?t='+obj.transcript_id+'" target="_blank">'+obj.transcript_id+'</a>, protein: <a href="https://www.uniprot.org/uniprot/'+obj.protein_ac+'" target="_blank">'+obj.protein_ac+'</a>)';
							
							// Draw the graph
							createGraph(obj);
	
							// Download for the whole svg as svg
							d3.select('#dlSVG').on('click', function() {
								var fileName = 'Gene_'+obj.gene_name+'_transcript_'+obj.transcript_id+'_protein_'+obj.protein_ac+'_metadome';
								saveSvg(document.getElementById('landscape_svg'), fileName);
							});
						}
					}
				}
			};
			if (typeof gtID !== 'undefined' && gtID.length > 0) {
				// the variable is defined
				// retrieve only the gt_id
				var gencode_id = gtID.split(" ")[0];
				xhttp.open("GET",
						"{{ url_for('api.submit_gene_analysis_job_stub') }}" + "/"
								+ gencode_id + "/", true);
				xhttp.setRequestHeader("Content-type",
						"application/x-www-form-urlencoded");
				xhttp.send();
			}
		}
	}
}

// annotates meta domain information for a position
function createPositionalInformation(domain_metadomain_coverage, transcript_id, position_json){
	// Retrieve the needed information for the GET request
	protein_position = position_json.values[0].protein_pos;
	
	// Construct the request for this domain and the aligned positions
	domain_request = "";
	domain_ids = Object.keys(position_json.values[0].domains);
	for (i = 0; i < domain_ids.length; i++){
		domain_id = domain_ids[i];
		domain_request += domain_id + ":[";
		
		// append the consensus positions
		for (j = 0; j < position_json.values[0].domains[domain_id].consensus_pos.length; j ++) {
			domain_request += position_json.values[0].domains[domain_id].consensus_pos[j];
			if (j+1 < position_json.values[0].domains[domain_id].consensus_pos.length) {
				domain_request += ",";
			}
		}
		domain_request += "]";
		if (i+1 < domain_ids.length) {
			domain_request += ",";
		}
	}
	
	if (domain_request == ""){
		// No domain request, so we can fill in the information without performing a GET request
		FillPositionalInformation(domain_metadomain_coverage, position_json, {});
	    $("#positional_information_overlay").addClass('is-active');
	}
	else{
		// Execute the GET request
		$.get("{{ url_for('api.get_metadomain_annotation_stub') }}" + "/" + transcript_id + "/" + protein_position + "/" + domain_request, function(data){
			FillPositionalInformation(domain_metadomain_coverage, position_json, data);
		    $("#positional_information_overlay").addClass('is-active');
		} );
	}
}

//Adds positional information for a selected position
function FillPositionalInformation(domain_metadomain_coverage, position_data, data){
    // Reset the positional information
    document.getElementById("positional_information_overlay_title").innerHTML = '<div class="label"><label class="title">Positional information (p.'+ position_data.values[0].protein_pos+')</label></div><label class="label" >'+document.getElementById("geneDetails").innerHTML +'</label>';
    document.getElementById("positional_information_overlay_body").innerHTML = '';

    
    // Add information on position to the HTML
    document.getElementById("positional_information_overlay_body").innerHTML +='<label class="label">Location details</label>'
    document.getElementById("positional_information_overlay_body").innerHTML += '<p>Chr: '+position_data.values[0].chr+', strand: '+position_data.values[0].strand+'</p>';
    document.getElementById("positional_information_overlay_body").innerHTML += '<p>Gene: '+ position_data.values[0].chr_positions +'</p>';
    document.getElementById("positional_information_overlay_body").innerHTML += '<p>Protein: p.'+ position_data.values[0].protein_pos +' '+ position_data.values[0].ref_aa_triplet+'</p>';
    document.getElementById("positional_information_overlay_body").innerHTML += '<p>cDNA: '+ position_data.values[0].cdna_pos +' '+ position_data.values[0].ref_codon +'</p>';
    
    // retrieve domain information
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
		    	// retrieve the domain_information from the data object
		    	meta_domain = data[domain_id_list[i]];
		    	
		    	// compute coverage
		    	position_coverage = Math.round(((meta_domain.alignment_depth/domain_metadomain_coverage[domain_id_list[i]])*100)*10)/10;
		    	
		    	// Add information to the report
				meta_domain_information += '<hr><label class="label">Meta-domain information for domain '+domain_id_list[i]+':</label>';
				meta_domain_information += '<p>Aligned to consensus position '+ position_data.values[0].domains[domain_id_list[i]].consensus_pos+', related to '+ (meta_domain.alignment_depth-1) +' other codons throughout the genome (with a '+position_coverage+'\% alignment coverage).</p>';
				
				
				var gnomAD_table = '<hr><label class="label">Variants in gnomAD SNVs at homologous positions:</label>';
				gnomAD_table += createGnomADTableHeader();
				var clinvar_table = '<hr><label class="label">Pathogenic ClinVar SNVs at homologous positions:</label>';
				clinvar_table += createClinVarTableHeader();
				
				// Append gnomad
				gnomAD_table += createGnomADTableBody(meta_domain.normal_variants);
				
				// Append clinvar
		    	clinvar_table += createClinVarTableBody(meta_domain.pathogenic_variants);
				
				// Add the footers
				clinvar_table += createTableFooter();
				gnomAD_table += createTableFooter();
				
				// Reset the tables if there are no variants
				if (meta_domain.normal_variants.length == 0){
				    gnomAD_table = "";
				}
				if (meta_domain.pathogenic_variants.length == 0){
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
		domain_information += '<p>Position is part of protein domain(s): '+domain_ids+'</p>'
    }
    
    // Add the domain information to the html element
    document.getElementById("positional_information_overlay_body").innerHTML += domain_information

    // Add clinvar at position information
    document.getElementById("positional_information_overlay_body").innerHTML += '<hr>';
	document.getElementById("positional_information_overlay_body").innerHTML += '<label class="label">Known pathogenic ClinVar SNVs at position</label>';
    if ("ClinVar" in position_data.values[0]){
		// Add ClinVar variant table
    	clinvar_variants = position_data.values[0].ClinVar;
    	
    	// Add the positional information
        for (index = 0; index < clinvar_variants.length; index++){
        	clinvar_variants[index].chr = position_data.values[0].chr;
        	clinvar_variants[index].chr_positions = position_data.values[0].chr_positions;
        	clinvar_variants[index].ref_codon = position_data.values[0].ref_codon;
        	clinvar_variants[index].ref_aa_triplet = position_data.values[0].ref_aa_triplet;
        }
        
        // Add the clinvar variant information
    	document.getElementById("positional_information_overlay_body").innerHTML += createClinVarTableHeader()+ createClinVarTableBody(clinvar_variants)+ createTableFooter();
    }
    else{
    	document.getElementById("positional_information_overlay_body").innerHTML += '<p>No ClinVar SNVs found at position</p>';
    }
    
    // Add the meta-domain information to the html element
    document.getElementById("positional_information_overlay_body").innerHTML += meta_domain_information;
}

//Update the positional information table with new values
function addRowToPositionalInformationTable(domain_metadomain_coverage, d, transcript_id) {
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
		else{
			related_gnomad = "-";
			related_clinvar = "-";
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
	    
	    // Call this method found in dashboard.js
	    createPositionalInformation(domain_metadomain_coverage, transcript_id, d)
	}).on("mouseover", function(d, i) {
	    d3.select(this).style("cursor", "pointer");
	});
		
	// Sort the table to the protein positions
	sortTable();
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

function createClinVarTableBody(ClinvarVariants){
    var html_table= '';
    // here comes the data
    for (index = 0; index < ClinvarVariants.length; index++){
		variant = ClinvarVariants[index];
		html_table += '<tr>';
		html_table += '<td>'+variant.chr+'</td>';
		html_table += '<td>'+variant.chr_positions+'</td>';
		html_table += '<td>'+variant.ref_codon+'>'+variant.alt_codon+'</td>';
		html_table += '<td>'+variant.ref_aa_triplet+'>'+variant.alt_aa_triplet+'</td>';
		html_table += '<td>'+variant.type+'</td>';
		html_table += '<td><a href="https://www.ncbi.nlm.nih.gov/clinvar/variation/' + variant.clinvar_ID + '/" target="_blank">' + variant.clinvar_ID + '</a></td>';
		html_table += '</tr>';
    }
    	
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

function createGnomADTableBody(gnomADVariants){
    var html_table= '';
    // here comes the data
    for (index = 0; index < gnomADVariants.length; index++){
	variant = gnomADVariants[index];
	html_table += '<tr>';
	html_table += '<td>'+variant.chr+'</td>';
	html_table += '<td>'+variant.chr_positions+'</td>';
	html_table += '<td>'+variant.ref_codon+'>'+variant.alt_codon+'</td>';
	html_table += '<td>'+variant.ref_aa_triplet+'>'+variant.alt_aa_triplet+'</td>';
	html_table += '<td>'+variant.type+'</td>';
	html_table += '<td>' + parseFloat(variant.allele_count/variant.allele_number).toFixed(6) + '</td>';
	html_table += '</tr>';
    }
    	
    return html_table;
}

function createTableFooter(){
    return '</tbody></table>';
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