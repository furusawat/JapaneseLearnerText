const xslc = document.getElementById("xaxisdata");
const yslc = document.getElementById("yaxisdata");
for(let i = 0; i < jsondata[0].length; i++){
	const xoptions = document.createElement("option");
	xoptions.textContent = jsondata[0][i];
	xoptions.value = i;
	xslc.appendChild(xoptions);
	xslc.selectedIndex = 0;
	const yoptions = document.createElement("option");
	yoptions.textContent = jsondata[0][i];
	yoptions.value = i;
	yslc.appendChild(yoptions);
	yslc.selectedIndex = 1;
}

const divcheckbox = document.getElementById("datacheckbox");
for(let i = 0; i < jsondata[1].length; i++){
	const inputs = document.createElement("input");
	inputs.type = "checkbox";
	inputs.id = jsondata[1][i][0];
	inputs.name = jsondata[1][i][0];
	if(i == 0){
		inputs.checked = "checked";
	}
	divcheckbox.appendChild(inputs);
	divcheckbox.appendChild(document.createTextNode(jsondata[1][i][0]));
}

var mychart = echarts.init(document.getElementById("main"));

function datachange(){
	rightdata = [];
	wrongdata = [];
	for(let i = 0; i < jsondata[1].length; i++){
		for(let ii = 0; ii < jsondata[1][i][1].length; ii++){
			rightdata.push([jsondata[1][i][1][ii][1][xslc.selectedIndex],
				jsondata[1][i][1][ii][1][yslc.selectedIndex],
				jsondata[1][i][1][ii][0],
				divcheckbox.children[i].checked
			])
		}
		for(let ii = 0; ii < jsondata[1][i][2].length; ii++){
			wrongdata.push([jsondata[1][i][2][ii][1][xslc.selectedIndex],
				jsondata[1][i][2][ii][1][yslc.selectedIndex],
				jsondata[1][i][2][ii][0],
				divcheckbox.children[i].checked
			])
		}
	}

	const option = {
		xAxis:{},
		yAxis:{},
		series:[{type: "scatter", data: rightdata,
			symbol: function(data){
				if(data[3] == true){return "circle";}else{return "none";}},
			label: {formatter: function (param) {return param.data[2];}, position: "top", show: true}},
			{type: "scatter", data: wrongdata,
			symbol: function(data){
				if(data[3] == true){return "circle";}else{return "none";}},
			label: {formatter: function (param) {return param.data[2];}, position: "top", show: true}}]
	};
	mychart.setOption(option);
};

datachange();

xslc.addEventListener("change", datachange);
yslc.addEventListener("change", datachange);
divcheckbox.addEventListener("change", datachange);
