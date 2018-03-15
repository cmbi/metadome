/**
 * Controls all responsiveness for the index.html page
 */
function updateSlidingwindowPercentage(slider){
	var swpercentage = document.getElementById("swPer");
	swpercentage.innerHTML = Math.round(slider.value * 100) + "%";
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

			if (isEmpty(transcript_id_results.trancript_ids)) {
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
				for (var i = 0; i < transcript_id_results.trancript_ids.length; i++) {
					var opt = new Option();
					opt.value = i;
					opt.text = transcript_id_results.trancript_ids[i];
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

// Function to get the data from the inputfield and send AJAX requests to the
// webserver, returning arrays with json objects.
function loadDoc() {
	var selection = document.getElementsByClassName("dropdown")[0];
	if (isEmpty(selection)) {
	} else {
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
					if (isEmpty(obj)) {
						alert("Error wrong gencode transcription id, please try again");
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
						geneDetails.innerHTML = '<div class="label"><label class="label">'+geneName+' (transcript: <a href="http://grch37.ensembl.org/Homo_sapiens/Transcript/Summary?t='+gtID+'" target="_blank">'+gtID+'</a>)</label></div>';
						
						createGraph(obj);
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
				
				if ($("#hgmd").is(":checked")) {
					var xhttpH = new XMLHttpRequest();
					xhttpH.onreadystatechange = function() {
						if (this.readyState == 4 && this.status == 200) {
							var hgmd = JSON.parse(xhttpH.responseText);
							if (isEmpty(hgmd)) {
								console.log("hgmd array empty");
							} else {
								appendHGMD(hgmd);
							}
						}
					}
					xhttpH.open("GET",
							"{{ url_for('api.get_HGMD_annotation') }}" + "/"
									+ gtID, true);
					xhttpH.setRequestHeader("Content-type",
							"application/x-www-form-urlencoded");
					xhttpH.send();
				}

				if ($("#clinvar").is(":checked")) {
					var xhttpC = new XMLHttpRequest();
					xhttpC.onreadystatechange = function() {
						if (this.readyState == 4 && this.status == 200) {
							var clinvar = JSON.parse(xhttpC.responseText);
							if (isEmpty(clinvar)) {
								console.log("clinvar array empty");
							} else {
								appendClinvar(clinvar);
							}
						}
					}
					xhttpC.open("GET",
							"{{ url_for('api.get_ClinVar_annotation') }}" + "/"
									+ gtID, true);
					xhttpC.setRequestHeader("Content-type",
							"application/x-www-form-urlencoded");
					xhttpC.send();
				}

				if ($("#domain").is(":checked")) {
					var xhttpD = new XMLHttpRequest();
					xhttpD.onreadystatechange = function() {
						if (this.readyState == 4 && this.status == 200) {
							var domains = JSON.parse(xhttpD.responseText);
							if (isEmpty(domains)) {
								console.log("domain array empty");
							} else {
								appendPfamDomains(domains);
							}
						}
					}
					xhttpD.open("GET", "{{ url_for('api.get_pfam_domains') }}"
							+ "/" + gtID, true);
					xhttpD.setRequestHeader("Content-type",
							"application/x-www-form-urlencoded");
					xhttpD.send();
				}

			}
		}
	}

}
function isEmpty(value) {
	return (value == null || value.length === 0);
}