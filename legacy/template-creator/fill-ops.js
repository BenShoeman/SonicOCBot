var undostack = [];
var examplecolors = [ [228,36,38], [242,143,32], [241,231,13], [10,144,93], [32,114,178], [110,57,141], [255,210,87] ];

var tmp;
function updateJSON()
{
  if (tmp)
  {
    document.getElementById("jsoninfo").innerHTML = JSON.stringify(tmp);
  }
}

function hsl2rgb(h, s, l)
{
  // Get saturation and lightness in range 0..1
  s = s/100.0; l = l/100.0;

  var c = (1 - Math.abs(2*l - 1)) * s;
  var hh = h / 60.0;
  var x = c * (1 - Math.abs(mod(hh, 2) - 1));
  var m = l - c/2;

  var r = 0, g = 0, b = 0;
  if (hh >= 5)
  {
    r = c; b = x;
  }
  else if (hh >= 4)
	{
    r = x; b = c;
  }
  else if (hh >= 3)
	{
    g = x; b = c;
  }
  else if (hh >= 2)
	{
    g = c; b = x;
  }
  else if (hh >= 1)
	{
    r = x; g = c;
  }
  else
  {
    r = c; g = x;
  }

  // Return RGB values in the range 0..255
  return [Math.round((r+m)*255), Math.round((g+m)*255), Math.round((b+m)*255)]
}

function rgb2hsl(r, g, b)
{
  // Get RGB values and put them in range 0..1
  r = r/255.0; g = g/255.0; b = b/255.0;

  var cmax = Math.max(r,g,b);
  var cmin = Math.min(r,g,b);
  var delta = cmax - cmin;

  var l = (cmax + cmin) / 2;

  if (delta == 0)
  {
    return [0.0, 0.0, l*100.0]
  }

  var s = delta / (1 - Math.abs(2*l - 1));

  var h;
  if (cmax == r)
  {
    h = 60 * mod(((g-b) / delta), 6);
  }
  else if (cmax == g)
  {
    h = 60 * (((b-r) / delta) + 2);
  }
  else
  {
    h = 60 * (((r-g) / delta) + 4);
  }

  // Return HSL values in the range 0..360 for hue, 0..100 otherwise
  return [h,s*100.0,l*100.0]
}

function mod(n, m)
{
  return ((n % m) + m) % m;
}

function loadTemplate()
{
  var canvas = document.getElementById("canvas");
  var c = canvas.getContext("2d");
  var template = new Image();

  template.onload = function() {
    canvas.setAttribute("width", template.width);
    canvas.setAttribute("height", template.height);
    canvas.setAttribute("onclick", "fillTemplate(event)");
    c.drawImage(template, 0, 0);
    tmp = {
      image: document.querySelector('input[type=file]').files[0].name,
      species: prompt("Enter species of template.").toLowerCase(),
      gender: prompt("Enter gender of template (man or woman).").toLowerCase(),
      fill: []
    };
    undostack = [];
    document.getElementById("tempinfo").style.display = "block";
    document.getElementById("tempinfo").innerHTML = "<p class='mb-2'>Species: " + tmp.species.replace(/^[a-z]/, function (x) {return x.toUpperCase()}) + "</p><p class='mb-2'>Gender: " + tmp.gender.replace(/^[a-z]/, function (x) {return x.toUpperCase()}) + "</p><p class='mb-2'><a class='btn btn-secondary' href='javascript:;' onclick='undoFill()'>Undo Last Fill</a> <a class='btn btn-danger' href='javascript:;' onclick='loadTemplate()'>Reset Template</a></p>";
    document.getElementById("colorregion").style.display = "block";
    document.getElementById("colorregionh").style.display = "block";
    updateJSON();

    if (document.getElementById("colorregion").children.length > 1)
    {
      document.getElementById("colorregion").innerHTML = '<div id="addregion"><a href="javascript:;" onclick="addColorRegion()">+ Add color region...</a></div>';
    }

    addColorRegion();
  };

  var file = document.querySelector('input[type=file]').files[0];
  var reader = new FileReader();

  reader.onloadend = function () {
    template.src = reader.result;
  };

  if (file)
  {
    reader.readAsDataURL(file); //reads the data as a URL
  }
  else
  {
    template.src = "";
  }
}

function fillTemplate(evt)
{
  var canvas = document.getElementById("canvas");
  var c = canvas.getContext("2d");

  var colornum = document.forms.colorregion.colorarea.value;
  if (tmp.fill[colornum].region == "skin") colornum = 6;
  var colormode = document.forms.colormode.colormode.value;

  switch (colormode)
  {
    case "":
      c.fillStyle = "rgb(" + examplecolors[colornum][0] + "," + examplecolors[colornum][1] + "," + examplecolors[colornum][2] + ")";
      break;
    case "shade":
      c.fillStyle = "rgb(" + Math.max(0,examplecolors[colornum][0]-30) + "," + Math.max(0,examplecolors[colornum][1]-30) + "," + Math.max(examplecolors[colornum][2]-30) + ")";
      break;
    case "tint":
      c.fillStyle = "rgb(" + Math.min(255,examplecolors[colornum][0]+45) + "," + Math.min(255,examplecolors[colornum][1]+45) + "," + Math.min(255,examplecolors[colornum][2]+45) + ")";
      break;
    case "complement":
      var hsl = rgb2hsl(examplecolors[colornum][0], examplecolors[colornum][1], examplecolors[colornum][2]);
      var newhsl = [mod(hsl[0] + 180, 360), hsl[1], hsl[2]];
      var rgb = hsl2rgb(newhsl[0], newhsl[1], newhsl[2]);
      c.fillStyle = "rgb(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + ")";
      break;
    case "analogccw":
      var hsl = rgb2hsl(examplecolors[colornum][0], examplecolors[colornum][1], examplecolors[colornum][2]);
      var newhsl = [mod(hsl[0] + 30, 360), hsl[1], hsl[2]];
      var rgb = hsl2rgb(newhsl[0], newhsl[1], newhsl[2]);
      c.fillStyle = "rgb(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + ")";
      break;
    case "analogcw":
      var hsl = rgb2hsl(examplecolors[colornum][0], examplecolors[colornum][1], examplecolors[colornum][2]);
      var newhsl = [mod(hsl[0] - 30, 360), hsl[1], hsl[2]];
      var rgb = hsl2rgb(newhsl[0], newhsl[1], newhsl[2]);
      c.fillStyle = "rgb(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + ")";
      break;
  }

  var coord = [evt.offsetX, evt.offsetY];
  var coordtype = "coords" + (colormode == "" ? "-norm" : "-" + colormode);
  var regionnum = document.forms.colorregion.colorarea.value;
  if (!tmp.fill[regionnum][coordtype])
  {
    tmp.fill[regionnum][coordtype] = [];
  }
  tmp.fill[regionnum][coordtype].push(coord);
  updateJSON();

  // var prevfilldata = c.getImageData(evt.offsetX, evt.offsetY, 1, 1).data
  undostack.push({
    // coord: coord,
    // lastcolor: [prevfilldata[0], prevfilldata[1], prevfilldata[2]],
    lastimage: c.getImageData(0,0,c.canvas.width,c.canvas.height),
    regionnum: regionnum,
    coordtype: coordtype
  });

  c.fillFlood(evt.offsetX, evt.offsetY, 0);
}

function undoFill()
{
  if (undostack.length)
  {
    var canvas = document.getElementById("canvas");
    var c = canvas.getContext("2d");

    undoevt = undostack.pop();

    // Remove that coord from the JSON
    tmp.fill[undoevt.regionnum][undoevt.coordtype].pop();
    if (tmp.fill[undoevt.regionnum][undoevt.coordtype].length == 0)
    {
      delete tmp.fill[undoevt.regionnum][undoevt.coordtype]
    }
    updateJSON();

    c.putImageData(undoevt.lastimage,0,0);
    // c.fillStyle = "rgb(" + undoevt.lastcolor[0] + "," + undoevt.lastcolor[1] + "," + undoevt.lastcolor[2] + ")";
    // c.fillFlood(undoevt.coord[0], undoevt.coord[1], 0);
  }
}

function addColorRegion()
{
  var newregionnode = document.createElement("DIV");
  var colorregionchoices = document.getElementById("colorregion");
  var lastcolregionel = colorregionchoices.children.length-1;
  newregionnode.id = "region" + lastcolregionel; // Has the Add color region... node too, so don't count that
  newregionnode.className = "jsontemp radio";

  var newnode = document.createElement("INPUT");
  newnode.type = "radio"; newnode.name = "colorarea";
  newnode.value = lastcolregionel; newnode.checked = lastcolregionel == 0;
  newregionnode.appendChild(newnode);

  var newnode = document.createElement("SPAN");
  newnode.style.color = "rgb(" + examplecolors[lastcolregionel][0] + "," + examplecolors[lastcolregionel][1] + "," + examplecolors[lastcolregionel][2] + ")";
  newnode.textContent = " " + lastcolregionel + " ";
  newregionnode.appendChild(newnode);

  var newnode = document.createElement("INPUT");
  newnode.style.color = "rgb(" + examplecolors[lastcolregionel][0] + "," + examplecolors[lastcolregionel][1] + "," + examplecolors[lastcolregionel][2] + ")";
  newnode.placeholder = "Name of color region...";
  newnode.setAttribute("onchange", "checkIfSkinRegion(this);updateRegionName(this)");
  newregionnode.appendChild(newnode);

  colorregionchoices.insertBefore(newregionnode, colorregionchoices.children[lastcolregionel]);
  newregionnode.lastChild.focus()

  tmp.fill.push({
    region: ""
  });
  updateJSON();

  if (colorregionchoices.children.length > 6)
  {
    colorregionchoices.removeChild(colorregionchoices.children[colorregionchoices.children.length-1]);
  }
}

function checkIfSkinRegion(field)
{
  var fieldParent = field.parentNode;
  if (field.value == "skin")
  {
    var regionnum = 6;
    fieldParent.children[1].style.color = "rgb(" + examplecolors[regionnum][0] + "," + examplecolors[regionnum][1] + "," + examplecolors[regionnum][2] + ")";
    field.style.color = "rgb(" + examplecolors[regionnum][0] + "," + examplecolors[regionnum][1] + "," + examplecolors[regionnum][2] + ")";
  }
  else if (field.style.color == "rgb(255, 210, 87)")
  {
    var regionnum = parseInt(fieldParent.firstChild.value);
    fieldParent.children[1].style.color = "rgb(" + examplecolors[regionnum][0] + "," + examplecolors[regionnum][1] + "," + examplecolors[regionnum][2] + ")";
    field.style.color = "rgb(" + examplecolors[regionnum][0] + "," + examplecolors[regionnum][1] + "," + examplecolors[regionnum][2] + ")";
  }
}

function updateRegionName(field)
{
  var fieldParent = field.parentNode;
  var regionnum = parseInt(fieldParent.children[1].textContent);
  tmp.fill[regionnum].region = field.value;
  updateJSON();
  fieldParent.firstChild.checked = true;
}

// context.fillFlood is Copyright (c) 2015 Max Irwin under The MIT License
var floodfill = (function() {

	//Copyright(c) Max Irwin - 2011, 2015, 2016
	//MIT License

	function floodfill(data,x,y,fillcolor,tolerance,width,height) {

		var length = data.length;
		var Q = [];
		var i = (x+y*width)*4;
		var e = i, w = i, me, mw, w2 = width*4;

		var targetcolor = [data[i],data[i+1],data[i+2],data[i+3]];

		if(!pixelCompare(i,targetcolor,fillcolor,data,length,tolerance)) { return false; }
		Q.push(i);
		while(Q.length) {
			i = Q.pop();
			if(pixelCompareAndSet(i,targetcolor,fillcolor,data,length,tolerance)) {
				e = i;
				w = i;
				mw = parseInt(i/w2)*w2; //left bound
				me = mw+w2;             //right bound
				while(mw<w && mw<(w-=4) && pixelCompareAndSet(w,targetcolor,fillcolor,data,length,tolerance)); //go left until edge hit
				while(me>e && me>(e+=4) && pixelCompareAndSet(e,targetcolor,fillcolor,data,length,tolerance)); //go right until edge hit
				for(var j=w+4;j<e;j+=4) {
					if(j-w2>=0     && pixelCompare(j-w2,targetcolor,fillcolor,data,length,tolerance)) Q.push(j-w2); //queue y-1
					if(j+w2<length && pixelCompare(j+w2,targetcolor,fillcolor,data,length,tolerance)) Q.push(j+w2); //queue y+1
				}
			}
		}
		return data;
	};

	function pixelCompare(i,targetcolor,fillcolor,data,length,tolerance) {
		if (i<0||i>=length) return false; //out of bounds
		if (data[i+3]===0 && fillcolor.a>0) return true;  //surface is invisible and fill is visible

		if (
			Math.abs(targetcolor[3] - fillcolor.a)<=tolerance &&
			Math.abs(targetcolor[0] - fillcolor.r)<=tolerance &&
			Math.abs(targetcolor[1] - fillcolor.g)<=tolerance &&
			Math.abs(targetcolor[2] - fillcolor.b)<=tolerance
		) return false; //target is same as fill

		if (
			(targetcolor[3] === data[i+3]) &&
			(targetcolor[0] === data[i]  ) &&
			(targetcolor[1] === data[i+1]) &&
			(targetcolor[2] === data[i+2])
		) return true; //target matches surface

		if (
			Math.abs(targetcolor[3] - data[i+3])<=(255-tolerance) &&
			Math.abs(targetcolor[0] - data[i]  )<=tolerance &&
			Math.abs(targetcolor[1] - data[i+1])<=tolerance &&
			Math.abs(targetcolor[2] - data[i+2])<=tolerance
		) return true; //target to surface within tolerance

		return false; //no match
	};

	function pixelCompareAndSet(i,targetcolor,fillcolor,data,length,tolerance) {
		if(pixelCompare(i,targetcolor,fillcolor,data,length,tolerance)) {
			//fill the color
			data[i]   = fillcolor.r;
			data[i+1] = fillcolor.g;
			data[i+2] = fillcolor.b;
			data[i+3] = fillcolor.a;
			return true;
		}
		return false;
	};

	function fillUint8ClampedArray(data,x,y,color,tolerance,width,height) {
		if (!data instanceof Uint8ClampedArray) throw new Error("data must be an instance of Uint8ClampedArray");
		if (isNaN(width)  || width<1)  throw new Error("argument 'width' must be a positive integer");
		if (isNaN(height) || height<1) throw new Error("argument 'height' must be a positive integer");
		if (isNaN(x) || x<0) throw new Error("argument 'x' must be a positive integer");
		if (isNaN(y) || y<0) throw new Error("argument 'y' must be a positive integer");
		if (width*height*4!==data.length) throw new Error("width and height do not fit Uint8ClampedArray dimensions");

		var xi = Math.floor(x);
		var yi = Math.floor(y);

		if (xi!==x) console.warn("x truncated from",x,"to",xi);
		if (yi!==y) console.warn("y truncated from",y,"to",yi);

		//Maximum tolerance of 254, Default to 0
		tolerance = (!isNaN(tolerance)) ? Math.min(Math.abs(Math.round(tolerance)),254) : 0;

		return floodfill(data,xi,yi,color,tolerance,width,height);
	};

	var getComputedColor = function(c) {
		var temp = document.createElement("div");
		var color = {r:0,g:0,b:0,a:0};
		temp.style.color = c;
		temp.style.display = "none";
		document.body.appendChild(temp);
		//Use native window.getComputedStyle to parse any CSS color pattern
		var style = window.getComputedStyle(temp,null).color;
		document.body.removeChild(temp);

		var recol = /([\.\d]+)/g;
		var vals  = style.match(recol);
		if (vals && vals.length>2) {
			//Coerce the string value into an rgba object
			color.r = parseInt(vals[0])||0;
			color.g = parseInt(vals[1])||0;
			color.b = parseInt(vals[2])||0;
			color.a = Math.round((parseFloat(vals[3])||1.0)*255);
		}
		return color;
	};

	function fillContext(x,y,tolerance,left,top,right,bottom) {
		var ctx  = this;

		//Gets the rgba color from the context fillStyle
		var color = getComputedColor(this.fillStyle);

		//Defaults and type checks for image boundaries
		left     = (isNaN(left)) ? 0 : left;
		top      = (isNaN(top)) ? 0 : top;
		right    = (!isNaN(right)&&right) ? Math.min(Math.abs(right),ctx.canvas.width) : ctx.canvas.width;
		bottom   = (!isNaN(bottom)&&bottom) ? Math.min(Math.abs(bottom),ctx.canvas.height) : ctx.canvas.height;

		var image = ctx.getImageData(left,top,right,bottom);

		var data = image.data;
		var width = image.width;
		var height = image.height;

		if(width>0 && height>0) {
			fillUint8ClampedArray(data,x,y,color,tolerance,width,height);
			ctx.putImageData(image,left,top);
		}
	};

	if (typeof CanvasRenderingContext2D != 'undefined') {
		CanvasRenderingContext2D.prototype.fillFlood = fillContext;
	};

	return fillUint8ClampedArray;

})();