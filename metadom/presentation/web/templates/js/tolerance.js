/**
 * Controls all responsiveness for the tolerance.html page
 */

$("#geneName").keyup(function(event) {
    if (event.keyCode === 13) {
        $("#getTranscriptsButton").click();
    }
});

function updateSlidingwindowPercentage(slider){
	var swpercentage = document.getElementById("swPer");
	swpercentage.innerHTML = slider.value;
}

function updateExACFrequencySlider(slider){
	var exacFreq = document.getElementById("exacFreq");
	exacFreq.innerHTML = Math.round(slider.value * 10000)/100 + "%";
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
				document.getElementById("advanced_checkbox").disabled = false;
				$("#advanced_checkbox_control").removeClass('is-hidden');
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

function clearTranscripts() {
	resetDropdown();
	$("#getToleranceButton").addClass('is-static');
	$("#getToleranceButton").removeClass('is-info');
	$("#geneName").removeClass('is-success');
	$("#advanced_options").addClass("is-hidden");
	$("#toleranceGraphContainer").addClass('is-hidden');
	document.getElementById("geneNameHelpMessage").innerHTML = "";
	document.getElementById("advanced_checkbox").disabled = true;
	document.getElementById("advanced_checkbox").checked = false;
	$("#advanced_checkbox_control").addClass('is-hidden');
	$("#download_tsv_button").addClass('is-hidden');
	$("#download_svg_button").addClass('is-hidden');
}

function toggleAdvancedOpions(checkbox) {
	// toggle between showing and hidding the advanced section
	if (checkbox.checked == true) {
		$("#advanced_options").removeClass("is-hidden");
	} else {
		$("#advanced_options").addClass("is-hidden");
	}
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
	var selection = document.getElementsByClassName("dropdown")[0];

	if (typeof selection !== 'undefined' && selection !== null && selection.length > 0) {
		$("#loading_overlay").addClass('is-active');
		var input = selection.options[selection.selectedIndex].text;
		var gtID = input.toUpperCase();
		var slidingWindow = document.getElementById("slidingWindow").value;
		var frequency = document.getElementById("frequency").value;

		var status = true;
		if (gtID == "" || frequency == "") {
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
						$("#download_tsv_button").addClass('is-hidden');
						$("#download_svg_button").addClass('is-hidden');
						$("#toleranceGraphContainer").addClass('is-hidden');
					} else {
						$("#toleranceGraphContainer").removeClass('is-hidden');
						$("#download_tsv_button").removeClass('is-hidden');
						$("#download_svg_button").removeClass('is-hidden');
						var geneName = document.getElementById("geneName").value;
						var geneDetails = document.getElementById("geneDetails");
						geneDetails.innerHTML = 'Gene: '+obj.geneName+' (transcript: <a href="http://grch37.ensembl.org/Homo_sapiens/Transcript/Summary?t='+gtID+'" target="_blank">'+gtID+'</a>, protein: <a href="https://www.uniprot.org/uniprot/'+obj.protein_ac+'" target="_blank">'+obj.protein_ac+'</a>)';
						
						createGraph(obj);
						// Download tsv with tolerance, variants and domains
						d3.select('#dlJSON').on(
								'click',
								function() {
									var selectionWindow = x.domain();
									var startIP = selectionWindow[0];
									var endIP = selectionWindow[1];
									var slidingW = parseInt(obj.sliding_window[1].pos);
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

									svg.select("g.domains").selectAll("rect.pfamDomains").each(
											function(d) {
												protDomain.push(d);
											});

									var clinDomArray = convertToArray(variants, hgmd, protDomain,
											startIP, endIP);
									var jsonse = JSON.stringify(obj.sliding_window.slice(startExport,
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
							saveSvg(document.getElementById('landscape_svg'), fileName);
						});
					}
				}
			};
			if (typeof gtID !== 'undefined' && gtID.length > 0) {
				// the variable is defined
				xhttp.open("GET",
						"{{ url_for('api.get_tolerance_landscape') }}" + "/"
								+ gtID + "/?slidingwindow=" + slidingWindow
								+ "&frequency=" + frequency, true);
				xhttp.setRequestHeader("Content-type",
						"application/x-www-form-urlencoded");
				xhttp.send();
			}
		}
	}
}
