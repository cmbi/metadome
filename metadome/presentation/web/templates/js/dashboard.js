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
    case 2:
    	fill_gene_and_show_transcript_example();
    	break;
    case 3:
    	show_graph_example();
    	break;
    }
}

function fill_gene_and_show_transcript_example(){
	// TODO: Fill the fields with demo data
    // e.g.: $('#pdb_id_div').addClass('hidden');
}

function show_graph_example(){
	// TODO: add testdata for graph
	// e.g.: createGraph(obj);
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
    content: "Welcome to MetaDome. This tour explains the usage of MetaDome." +
             " Once the tour is complete, you can get started!" +
             "<br><br>Click next to begin."
  },
  {
    element: "#geneName",
    title: "Input here your gene name of interest",
    content: "TEST"
  },
  {
    element: "#gtID",
    title: "Select your desired transcript",
    content: "TEST"
  },
  {
    element: "#graph",
    title: "Visualization",
    content: "TEST"
  }
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
					$("#loading_overlay").removeClass('is-active');

					if (typeof obj == 'undefined' || obj == null || obj.length == 0) {
						d3.select("svg").selectAll("*").remove();
						$("#graph_control_field").addClass('is-hidden');
						$("#toleranceGraphContainer").addClass('is-hidden');
					} else {						
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
