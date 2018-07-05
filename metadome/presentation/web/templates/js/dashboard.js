/**
 * Controls all responsiveness for the tolerance.html page
 */

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
    case 1:
    	tour_fill_gene_name();
    	break;
    case 3:
    	tour_fill_succes_message_transcripts();
    	break;
    case 4:
    	tour_fill_fail_message_transcripts();
    	break;
    case 5:
    	tour_fill_succes_message_transcripts();
    	tour_fill_transcripts();
    	break;
    case 7:
    	$("#loading_overlay").addClass('is-active');
    	break;
    case 8:
    	$("#loading_overlay").removeClass('is-active');
    	tour_fill_graph_example();
    	break;
    case 11:
    	window.setTimeout(tour_check_alternative_visualization, 500);
    	window.setTimeout(toggleToleranceLandscapeOrMetadomainLandscape,1000);
    	window.setTimeout(tour_check_default_visualization, 2000);
    	window.setTimeout(toggleToleranceLandscapeOrMetadomainLandscape,2000);
    	break;
    case 12:
    	tour_switch_clinvar_variants();
    	window.setTimeout(tour_switch_clinvar_variants,2000);
    	
    	break;
    }
}

function tour_switch_clinvar_variants(){
	$('#clinvar_checkbox').trigger( "click" );
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

function tour_fill_succes_message_transcripts(){
	document.getElementById("geneNameHelpMessage").innerHTML = "Retrieved transcripts for gene 'T'";
	$("#geneNameHelpMessage").removeClass('is-danger');
	$("#geneNameHelpMessage").addClass('is-success');
}

function tour_fill_fail_message_transcripts(){
	document.getElementById("geneNameHelpMessage").innerHTML = "No transcripts available in database for gene 'T'";
	$("#geneNameHelpMessage").removeClass('is-success');
	$("#geneNameHelpMessage").addClass('is-danger');
}

function tour_fill_transcripts(){
	clearDropdown();
	$("#getToleranceButton").addClass('is-info');
	$("#getToleranceButton").removeClass('is-static');
	var dropdown = document.getElementById("gtID");
	dropdown.setAttribute('class', 'dropdown');
	var opt = new Option();
	opt.value = 1;
	opt.text = "ENST00000296946.2";
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
				" This tour explains the usage of MetaDome "+
				"through the use of an example.<br><br>"+
				"You can click 'end tour' any time to start "+
				"analysing your own gene of interest. " +
				"<br><br>Click next to begin."
	  },
	  {
	    element: "#geneName",
	    title: "Gene of interest",
	    content: "Input here your gene name of interest<br><br>"+
	    		"For this example we fill in the 'T' gene"
	  },
	  {
		element: "#getTranscriptsButton",
		title: "Get Transcripts",
		content: "Click the 'Get Transcripts' button to retrieve"+
				" all the transcripts for your gene of interest"
	  },
	  {
		element: "#geneNameHelpMessage",
		title: "Get Transcripts (Succeeded)",			
		content: "After clicking the 'Get Transcripts' button, we "+
				"check if there are any transcripts available for "+
				"your gene of interest.<br><br>"+
				"This is the message you see when the retrieval is "+
				"succesful."
	  },
	  {
		element: "#geneNameHelpMessage",
		title: "Get Transcripts (Failed)",	
		content: "This is the message you see when the retrieval is "+
				"unsuccesful."
	  },
	  {
		element: "#gtID",
		title: "Select Transcript",
		content: "Select the transcript of your interest from the "+
				"dropdown menu."
	  },
	  {
		element: "#getToleranceButton",
		title: "Analyse Protein",
		content: "Click the 'Analyse Protein' button to perform the "+
				" analysis."
	  },
	  {
		element: "#loading_overlay",
		title: "Loading screen <br>(Click next to continue)",
		content: "This analysis may take between 5 "+
				"minutes and up to an hour to complete. <br><br>"+
				"For now you can just Click next to continue.<br><br> "+
				"Luckily all results are stored after they "+
				"complete, so the next time you query this "+
				"transcript it will load in a matter of seconds."
	  },
	  {
		element: "#content",
		title: "Analysis results",
		content: "When the analyses complete, you obtain a "+
				"wealth of information. <br><br> We will now " +
				"go over each part in detail.",
	  },
	  {
		element: "#graph_control_field",
		title: "Graph Control",
		content: "This is called the graph control field. Here, " +
				"you may switch between different representations " +
				"of your result visualization, download the " +
				"visualization and and select if you would like " +
				"to display any known ClinVar variants.",
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
		element: "#checkbox_for_landscape",
		title: "Switching between visualizations",
		content: "Here you can switch between the 'Meta-domain " +
				"Landscape' and the 'Tolerance Landscape' " +
				"visualization modes.",
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#clinvar_checkbox",
		title: "Switching ClinVar variants",
		content: "Here you can toggle the display of any ClinVar " +
				"variants for your gene of interest.",
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#tolerance_axis",
		title: "Visualization",
		content: "test",
		backdropContainer: "#landscape_svg"
	  },
	  {
		element: "#schematic_protein_zoom_text",
		title: "Zoom",
		content: "test",
		placement: 'left',
		backdropContainer: "#landscape_svg"
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
				var i = 0
				for (; i < transcript_id_results.trancript_ids.length; i++) {
					var opt = new Option();
					opt.value = i;
					opt.text = transcript_id_results.trancript_ids[i];
					dropdown.options.add(opt);
				}
				for (var j = 0; i < transcript_id_results.trancript_ids.length + transcript_id_results.no_protein_data.length; i++) {
					var opt = new Option();
					opt.value = i;
					opt.text = transcript_id_results.trancript_ids[j];
					opt.disabled = true;
					dropdown.options.add(opt);
					j++;
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
				xhttp.open("GET",
						"{{ url_for('api.submit_gene_analysis_job_stub') }}" + "/"
								+ gtID + "/", true);
				xhttp.setRequestHeader("Content-type",
						"application/x-www-form-urlencoded");
				xhttp.send();
			}
		}
	}
}
