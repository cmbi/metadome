// JSON/array to TSV Converter
function convertToTSV(jsonArray/*tolerance*/, objArray/*clindomhgmd*/) {
	var array = typeof jsonArray != 'object' ? JSON.parse(jsonArray) : jsonArray;
	var str = 'pos:\tscore:\tHGMD:\tclinvar:\tPfam:\r\n';
	
	for (var i = 0; i < array.length; i++) {
		var line = '';
		for (var index in array[i]) {
			if (line != '') line += '\t'

			line += array[i][index];
		}
		line += '\t'
		for (var y=0; y<objArray[2].length; y++){
			if (objArray[2][y][0] == array[i].pos){
				line += objArray[2][y][1] +'>'+objArray[2][y][2]
			}
		}
		line += '\t'
		for (var x=0; x<objArray[0].length; x++){
			if (objArray[0][x][0] == array[i].pos){
				line += objArray[0][x][1] +'>'+objArray[0][x][2]
			}
		}
		line += '\t'
		for (var z=0; z<objArray[1].length; z++){
			if (array[i].pos >= objArray[1][z][0] && array[i].pos <= objArray[1][z][1]){
				
				line += objArray[1][z][2]
			}
		}
		str += line + '\r\n';
	}
	return str;
}

// function to convert the clinvar and domain jsonArrays to a single array
function convertToArray(clinvarJson, hgmdJson, domainJson, start, end){
	var array = [];
	var clinvarArray = [];
	var domainArray = [];
	var hgmdArray = [];
	
	for (var i=0; i<clinvarJson.length; i++){
		if (clinvarJson[i].pos > start && clinvarJson[i].pos < end){
			clinvarArray.push([clinvarJson[i].pos, clinvarJson[i].ref, clinvarJson[i].alt]);
		}
	}
	for (var x=0; x<domainJson.length; x++){
		if (domainJson[x].start < end && domainJson[x].stop > start){
			domainArray.push([domainJson[x].start, domainJson[x].stop, domainJson[x].ID]);
		}
	}
	for (var y=0; y<hgmdJson.length; y++){
		if (hgmdJson[y].pos > start && hgmdJson[y].pos < end){
			hgmdArray.push([hgmdJson[y].pos, hgmdJson[y].ref, hgmdJson[y].alt]);
		}
	}
	
	array.push(clinvarArray);
	array.push(domainArray);
	array.push(hgmdArray);
	return array;
}

function prepareMetadom(metadomData){
	var str = 'dcp:\tproteinpos:\tscore:\r\n';
	
	for (var i=0; i<metadomData.length; i++){
		var line = '';
		
		var dcp = metadomData[i].dcp;
		var proteinpos = metadomData[i].genepos;
		var tolscore = metadomData[i].score;
		
		if (isNaN(proteinpos)){
			proteinpos = NaN;
		}
		
		if (isNaN(tolscore) || tolscore==null){
			tolscore= NaN;
		}
		
		line+=dcp+'\t'+proteinpos+'\t'+tolscore;
		str+=line+ '\r\n';
	}
	return str;
}