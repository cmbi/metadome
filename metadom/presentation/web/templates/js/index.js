/**
 * Controls all responsiveness for the index.html page
 */

var slider = document.getElementById("slidingWindow");
var swpercentage = document.getElementById("swPer");
swpercentage.innerHTML = (slider.value) * 100 + "%";

slider.oninput = function() {
	swpercentage.innerHTML = (this.value) * 100 + "%";
}

// Function to send AJAX request to the webserver to get all transcripts
// belonging to a gene name
function getTranscript() {
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
	document.getElementById("geneNameHelpMessage").innerHTML = "";
	document.getElementById("advanced_checkbox").disabled = true;
	document.getElementById("advanced_checkbox").checked = false;
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
	var go = false;
	var selection = document.getElementsByClassName("dropdown")[0];
	if (isEmpty(selection)) {
		alert("Select a transcript id");
	} else {
		$("#loading_overlay").addClass('is-active');
		var input = selection.options[selection.selectedIndex].text;
		var gtID = input.toUpperCase();
		var startPos = document.getElementById("startPos").value;
		var endPos = document.getElementById("endPos").value;
		var slidingWindow = document.getElementById("slidingWindow").value;
		var frequency = document.getElementById("frequency").value;

		var status = true;
		if (gtID == "" || startPos == "" || endPos == "" || frequency == "") {
			status = false
		}
		if (parseInt(startPos) > parseInt(endPos)) {
			status = false;
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
					} else {
						createGraph(obj);
						go = true;
					}
				}
			};
			if (typeof gtID !== 'undefined' && gtID.length > 0) {
				var _tolerance_api_call = "/" + gtID + "/?slidingwindow="
						+ slidingWindow + "&frequency=" + frequency
				if (typeof startPos !== 'undefined' && startPos.length > 0) {
					_tolerance_api_call += "&startpos=" + startPos;
				}
				if (typeof endPos !== 'undefined' && endPos.length > 0) {
					_tolerance_api_call += "&endpos=" + endPos;
				}

				// the variable is defined
				xhttp.open("GET", "{{ url_for('api.get_default_tolerance') }}"
						+ _tolerance_api_call, true);
				xhttp.setRequestHeader("Content-type",
						"application/x-www-form-urlencoded");
				xhttp.send();

				if ($("#domain").is(":checked") && go) {
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
					// TODO: ensure proper link is retrieved here
					xhttpD.open("GET",
							"http://localhost:8080/ToleranceLandscape/domainServlet/?gtID="
									+ gtID + "&startpos=" + startPos
									+ "&endpos=" + endPos + "&slidingwindow="
									+ slidingWindow + "", true);
					xhttpD.setRequestHeader("Content-type",
							"application/x-www-form-urlencoded");
					xhttpD.send();
				}

				if ($("#hgmd").is(":checked") && go) {
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
					// TODO: ensure proper link is retrieved here
					xhttpH.open("GET",
							"http://localhost:8080/ToleranceLandscape/hgmdServlet/?gtID="
									+ gtID + "&startpos=" + startPos
									+ "&endpos=" + endPos + "&slidingwindow="
									+ slidingWindow + "", true);
					xhttpH.setRequestHeader("Content-type",
							"application/x-www-form-urlencoded");
					xhttpH.send();
				}

				if ($("#clinvar").is(":checked") && go) {
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
					// TODO: ensure proper link is retrieved here
					xhttpC.open("GET",
							"http://localhost:8080/ToleranceLandscape/clinvarServlet/?gtID="
									+ gtID + "&startpos=" + startPos
									+ "&endpos=" + endPos + "&slidingwindow="
									+ slidingWindow + "", true);
					xhttpC.setRequestHeader("Content-type",
							"application/x-www-form-urlencoded");
					xhttpC.send();
				}
			}

		}
	}

}
function isEmpty(value) {
	return (value == null || value.length === 0);
}