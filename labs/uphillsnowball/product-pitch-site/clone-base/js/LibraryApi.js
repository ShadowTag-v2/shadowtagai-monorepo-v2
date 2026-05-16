// JavaScript Document

var arrLibExists = false;
arrLibExists = !!arrLib

if (typeof iLibInstance === 'undefined' || iLibInstance === null) {
	var iLibInstance=0;
}
iLibInstance+=1;

var oLib = {BizID:"", sKey:"", sDiv:"LibDiv", sStoryDiv:"LibStoryDiv", sAttachDiv:"LibStoryDiv", Output:"0", SiteID:"0", Count:"10", Group:"", Year:"", currentyear:"", Tag:"", Filter:"", Page:"1", sNav:"1", sTools:"", Rss:"1", ShowSummary:"", ShowDate:"1", iDateFormat:"1", UseSameDiv:"0", ShowBack:"", ShowExpand:"", Alink:"", UseTemplate:"", iPopoutDiv:"1", sSearch:"", CSS:"", sPdf:"", sPrint:"", HeadlineLen:"", iStoryWidth:600, iStoryHeight:600, iStoryMaxWidth:0, iStoryMaxHeight:0, iLeftOffset:0, iTopOffset:50, iWidthOffset:40, iHeightOffset:90, Target:"", Instance:"", ViewLink:"", ViewFormat:"", sHttp:"https", sServer:"www.b2i.us", InvID:"", InvKey:"", Offset:"", ForceAtt:"", AutoOpen:"", FixFD:""};

oLib.Instance=iLibInstance;

if(!arrLib){
	var arrLib=[oLib];
}else{
	arrLib.push(oLib);
}

var currItem='';
var currItemID='';

//-----------------------------------
function AutoLoadContent(){
	var sI ='';
	sI=getParameterByName("i", "");
	if(!sI){
	}else{
		if(sI.length>0){
			if(oLib.ShowExpand=="1"){
			}
			if(oLib.iPopoutDiv=="1"){
				sUrl= oLib.sHttp + '://' + oLib.sServer + '/profiles/investor/NewsPrint.asp?v=7&b=' + oLib.BizID + '&ID=' + sI + '&m=rl&g=' + oLib.Group;
				//alert(sUrl);
				OpenApiStory(sUrl,oLib.sDiv);
				//b2iShowApiDownloadPage(sUrl,oLib.sDiv);
			}else{
				var sUrl;
				sUrl= oLib.sHttp + '://' + oLib.sServer + '/profiles/investor/NewsPrint.asp?v=7&b=' + oLib.BizID + '&ID=' + sI + '&m=rl&g=' + oLib.Group;
				OpenApiStory(sUrl,oLib.sDiv);
			}
		}
	}
}


//-----------------------------------
function GetTopURL(){
	var sUrl;
	sUrl=window.top.location.href;
	return sUrl;
}


//-----------------------------------
function getData(){
	//console.log(oLib.Output + ' ' + oLib.sDiv);
	var sb2iClass = 'b2iLibToolsContainer' + oLib.Output;
	var b2ipressdiv = document.getElementById(oLib.sDiv);
	if (b2ipressdiv && !b2ipressdiv.classList.contains(sb2iClass)) {
		b2ipressdiv.classList.add(sb2iClass);
	}
	console.log('Powered by B2i Technologies - www.b2itech.com - DataAnywhere(tm)');

	if(oLib.BizID=='') {
		console.log('Business ID missing. You should have received this from our support team.');
		return;
	}
	
	currItem='';
	//if(parseInt(oLib.Count)<=3){oLib.sTools="0";}
	var sUrl = CreateURL();
	
	GetApiContent('Get', sUrl, null, oLib.sDiv, 0);
	if (oLib.UseSameDiv=="1"){
		oLib.sStoryDiv=oLib.sDiv;
		oLib.iPopoutDiv="0";
	}

	if (oLib.iPopoutDiv=="1"){
		try{
			CheckSize();
		}
		catch(err) {
		}
	}
}


function GoHunting(){
	if(getEmailCookie("cInvID")){
		var sTempInvID = getEmailCookie("cInvID");
		if(sTempInvID!='' && Number.isInteger(sTempInvID) && sTempInvID.toLowerCase()!='undefined'){
			oLib.InvID=sTempInvID;
		}
	}
	
	if(getEmailCookie("cInvKey")){
		var sTempKey = getEmailCookie("cInvKey");
		if(sTempKey!='' && sTempKey.toLowerCase()!='undefined'){
			oLib.InvKey=sTempKey;
		}
	}
}


//---------------------------------------------------------------
function getEmailCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}


//-----------------------------------
function getData2(){
	currItem='';
	//if(parseInt(oLib.Count)<=3){oLib.sTools="0";}
	var sUrl = CreateURL();
	GetApiContent('Get', sUrl, null, oLib.sDiv, 1);
	
	if (oLib.UseSameDiv=="1"){
		oLib.sStoryDiv=oLib.sDiv;
		oLib.iPopoutDiv="0";
	}
	
	if (oLib.iPopoutDiv=="1"){
		try{
			CheckSize();
		}
		catch(err) {
			console.log(err);
		}
	}
}


//-----------------------------------
function CreateURL(){
	var sUrl = oLib.sHttp + "://" + oLib.sServer + "/b2i/LibraryFeed.asp?b=" + oLib.BizID;
	if(oLib.sKey!='') {sUrl += "&api=" + oLib.sKey};
	if(oLib.SiteID!='') {sUrl += "&s=" + oLib.SiteID};
	if(oLib.Count!='') {sUrl += "&i=" + oLib.Count};
	if(oLib.Group!='') {sUrl += "&g=" + oLib.Group};
	if(oLib.ShowDate!='') {sUrl += "&sd=" + oLib.ShowDate};
	if(oLib.Tag!='') {sUrl += "&t=" + oLib.Tag};
	if(oLib.Filter!='') {sUrl += "&f=" + oLib.Filter};
	if(oLib.sNav!='') {sUrl += "&n=" + oLib.sNav};
	if(oLib.Output!='') {sUrl += "&out=" + oLib.Output};
	if(oLib.Year!='') {sUrl += "&y=" + oLib.Year};
	if(oLib.currentyear!='') {sUrl += "&cy=" + oLib.currentyear};
	if(oLib.sTools!='') {sUrl += "&tl=" + oLib.sTools};
	if(oLib.iDateFormat!='1') { sUrl += "&df=" + oLib.iDateFormat };
	if(oLib.Alink!='') {sUrl += "&a=" + oLib.Alink};
	if(oLib.ViewLink!='') { sUrl += "&vl=1" };
	if(oLib.CSS!='') {sUrl += "&css=" + oLib.CSS};
	if(oLib.RSS!='1') { sUrl += "&rss=0" };
	if(oLib.HeadlineLen!='') {sUrl += "&ln=" + oLib.HeadlineLen};
	if(oLib.Offset!='') { sUrl += "&off=" + oLib.Offset};
	if(oLib.ShowSummary!='') {sUrl += "&su=" + oLib.ShowSummary};

	if(oLib.Page!='') {sUrl += "&p=" + oLib.Page};
	if(oLib.ShowBack!='') {sUrl += "&sb=" + oLib.ShowBack};
	if(oLib.ShowExpand!='') {sUrl += "&se=" + oLib.ShowExpand};
	if(oLib.sPdf!=''){sUrl += "&Pdf=1"};
	if(oLib.sPrint!=''){sUrl += "&Prt=1"};
	if(oLib.UseSameDiv!='0') { sUrl += "&us=1" };
	if(oLib.UseTemplate!='') { sUrl += "&ut=1" };
	if(oLib.Target!='') { sUrl += "&tg=" + oLib.Target };
	if(oLib.Instance!='') { sUrl += "&in=" + oLib.Instance};
	if(oLib.ForceAtt!='') { sUrl += "&att=1"};
	if(oLib.sSearch!='') { sUrl += "&ss=" + oLib.sSearch };
	if(oLib.InvID!='' && oLib.InvKey!='') {
		sUrl += "&i=" + oLib.InvID + "&ik=" + oLib.InvKey
	}

	sUrl += "&div=" + oLib.sDiv;
	return sUrl;
}


//-----------------------------------
function CheckSize(){
	var iNewWidth= window.innerWidth;
	var iNewHeight = window.innerHeight;
	if (oLib.iStoryWidth>iNewWidth){
		oLib.iStoryWidth=iNewWidth-oLib.iWidthOffset;
	}
	if (oLib.iStoryHeight>iNewHeight){
		oLib.iStoryHeight=iNewHeight-oLib.iHeightOffset;
	}
}


//-----------------------------------
function ExpandStory(sUrl,iItemID){
	var oDiv = document.getElementById(iItemID);
	if (currItemID!=iItemID){
		//if (currItemID!='') ShowItemDiv(currItemID);
		ClosePrev();
		GetApiContent('GET', sUrl, null, iItemID, 0);
		//LibScrollTo('Anchor' + iItemID);
		//GotoHash('Anchor' + iItemID);
		currItemID=iItemID;
		currItem=sUrl;
		oDiv.style.display="block";
	}else{
		//LibScrollTo('Anchor' + iItemID);
		//GotoHash('Anchor' + iItemID);
		ShowItemDiv(iItemID);
		currItemID='';
		currItem='';
	}
}


//-----------------------------------
function ClosePrev(){
	if (currItemID!=''){
		ShowItemDiv(currItemID);
		currItemID='';
		currItem='';
	}
}


//-----------------------------------
function ShowItemDiv(iItemID){
	var oDiv = document.getElementById(iItemID);
	if (oDiv.style.display=="block"){
		oDiv.style.display="none";
	}else{
		oDiv.style.display="block";
	}
}


//-----------------------------------
function OpenApiStory(sUrl,sDiv){
	var oLibObj = FindLib(sDiv);
	SetLib(oLibObj);

	if(currItem=='' || currItem!=sUrl){
		var iHash;

		iHash=4;
		//if(oLibObj.ShowExpand=="" && oLibObj.UseSameDiv=="0"){iHash=0;}
		
		GetApiContent('GET', sUrl, null, oLibObj.sStoryDiv, iHash);
		currItem=sUrl;
	}
	
	if(oLibObj.iPopoutDiv=="1"){
		b2iShowApiDownloadPage(sUrl,sDiv);
	}
	
	if(FixFD=="1"){
		var LibStoryContainer = document.getElementById("LibStoryContainer")
		document.body.appendChild(LibStoryContainer);
	}
}


//-----------------------------------
function OpenLibWindow(sURL) {
	window.open(sURL,'Lib','titlebar=yes,location=yes,status=yes, scrollbars=yes,width=1200,height=700');
}


//-----------------------------------
function OpenApiWin(theURL,winName) {
	var h = screen.height;
	var w = screen.width;
	var myWin = window.open(theURL,winName,'toolbar=no ,location=0,status=no,titlebar=no,menubar=no,width=' + w + ',height=' + h);
	myWin.focus()
}


//-----------------------------------
function b2iShowApiDownloadPage(sUrl,sDiv){
	var tDiv = document.getElementById('LibStoryContainer');
	tDiv.style.display="block";

	var oLibObj = FindLib(sDiv);
	SetLib(oLibObj);
	ResizeApiViewer();
	
	//hide div
	if(currItem==sUrl){
//		tDiv.style.display="none";
//		tDiv.innerHTML='';
//		currItem='';
	}else{
		currItem=sUrl;
	}

}



//-----------------------------------
function GetApiContent(requestType, sURL, varString, myDiv, iHash){
	// requestType:  	1 = get 0 = post
	// sURL: 			page requested
	// varString: 		null if none
	// myDiv:			where to put returned value
	var xmlHttp;
	var PostOrGet;
    try  {  // Firefox, Opera 8.0+, Safari
        xmlHttp=new XMLHttpRequest();
    } catch (e) {  // Internet Explorer  
        try {
            xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
        } catch (e) {
            try {
                xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
            } catch (e){
                alert("Your browser does not support this function.\n\nPlease have your IT department configure your computer to work with AJAX.");
                return false;
            }
        }
    }
	
	if(requestType==1){
		PostOrGet = "GET"
	}else{
		PostOrGet = "POST"
	}
	

	xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState==4) {
            var sReturn = xmlHttp.responseText;
			if(oLib.sPdf!='') sReturn = sReturn.replace(/=PDF=/gi, oLib.sPdf);
			if(oLib.sPrint!='') sReturn = sReturn.replace(/=PRINT=/gi, oLib.sPrint);
			if(oLib.ViewLink!="") sReturn = sReturn.replace(/=URL=/gi, oLib.ViewLink);

			var oStoryDiv = document.getElementById(myDiv);
            oStoryDiv.innerHTML=sReturn;
			//oStoryDiv.scrollTop = 0;
			
			if(oLib.iPopoutDiv=="0" && currItem!=''){
				//ShowDisplayListIcon();
			}
			
			if(iHash==2){
				GotoHash('b2iLibScrollTo' + oLib.Instance);
			}else if(iHash==3){
				GotoHash('b2iLibScrollTo' + oLib.Instance);
			}else if(iHash==4){
				GotoHash('b2iLibScrollTo');
			}else if(iHash==1){
				GotoHash('b2iLibScrollTo' + oLib.Instance);
			}else if(iHash==0){
			}
			
			var sI ='';
			sI=getParameterByName("i", "");

			if (oLib.BizID=="2478"){oLib.AutoOpen="1"; oLib.ShowBack="1";}

			if (oLib.AutoOpen!='' && sI!=''){
				AutoLoadContent();
				removeParam("i");
			}
        }
    }
	
	xmlHttp.open(PostOrGet, sURL, true);
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlHttp.send(varString);
}


function removeParam(key) {
    // Get current URL without the parameters
    let baseUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;

    // Get current query string parameters
    let queryParams = new URLSearchParams(window.location.search);

    // Remove the parameter if it exists
    if (queryParams.has(key)) {
        queryParams.delete(key);
    }

    // Construct the new URL
    let newUrl = baseUrl + "?" + queryParams.toString();

    // Update the URL
    window.history.replaceState({}, document.title, newUrl);
}


//-----------------------------------
function GotoHash(sHash){
	location.hash = '';
	location.hash="#" + sHash;
}


//-----------------------------------
function ShowDisplayListIcon(){
	var oDisplayListDiv1 = document.getElementById("DisplayListDiv1");
	oDisplayListDiv1.style.display="block";
	var oDisplayListDiv2 = document.getElementById("DisplayListDiv2");
	oDisplayListDiv2.style.display="block";
}


//-----------------------------------
function LibScrollTo(name) {
  //init thread
  LibScrollToResolver(document.getElementById(name));
}


//-----------------------------------
function LibScrollToResolver(elem) {
  var jump = parseInt(elem.getBoundingClientRect().top) -100 -oLib.iTopOffset;
  document.body.scrollTop += jump;
  document.documentElement.scrollTop += jump;
  //lastjump detects anchor unreachable, also manual scrolling to cancel animation if scroll > jump
//  if (!elem.lastjump || elem.lastjump > Math.abs(jump)) {
//   elem.lastjump = Math.abs(jump);
//    setTimeout(function() {
//      LibScrollToResolver(elem);
//    }, "100");
//  } else {
//    elem.lastjump = null;
//  }
}


//-----------------------------------
function SetLib(oLibObj){
	oLib=oLibObj;
}


//-----------------------------------
function FindLib(sDivSearch){
	if (arrLib.length>1){
		var arrlen = arrLib.length;
		var i;
		for(i=0; i<arrlen; i++){
			itemLib = arrLib[i];
			if(itemLib.sDiv==sDivSearch){
				return itemLib;
			}
		}
	}else{
		itemLib = arrLib[0];
		return itemLib;
	}
}


//-----------------------------------
function UpdateApiPage(sPage,sDiv){
	var oLibObj = FindLib(sDiv);
	CloseApiDiv();
	oLibObj.Page = sPage;
	SetLib(oLibObj);
	getData2();
}


//-----------------------------------
function UpdateApiYear(sYear,sDiv){
	var oLibObj = FindLib(sDiv);
	SetLib(oLibObj);
	CloseApiDiv();
	//oLibObj.sSearch = '';
	oLibObj.Year = sYear;
	oLibObj.Page = 1;
	getData();
}


function getYear(selectObject) {
	var value = selectObject.value;  
	console.log(value);
  }


//-----------------------------------
function DoSearch(sSearch, sDiv){
	var oLibObj;
	oLibObj= FindLib(sDiv);
	SetLib(oLibObj);

	if(sSearch!=''){
		oLibObj.sSearch=sSearch;
		oLibObj.Page = 1;
		//SetLib(oLibObj);
		getData();
	}else{
		oLibObj.sSearch='';
		getData();
	}
}



//-----------------------------------
function HandleKey(e, sSearch, sDiv){
	if(e.keyCode === 13){
		e.preventDefault(); // Ensure it is only this code that runs
		DoSearch(sSearch,sDiv)
	}
}


//-----------------------------------
// reserved
function UpdateApiTag(sTag){
	var oLibObj = FindLib(sDiv);
	CloseApiDiv();
	oLibObj.Tag = sTag;
	oLibObj.Page = 1;
	SetLib(oLibObj);
	getData();
}


//-----------------------------------
var popUpWin=0;
function popUpWindow(URLStr, left, top, width, height){
	if(popUpWin) {
		if(!popUpWin.closed) popUpWin.close();
	}
	popUpWin = window.open(URLStr,'popUpWin','menubar,scrollbars,resizable,toolbar,location=no,directories=no,status=no,copyhistory=yes,width='+width+',height='+height+',left='+left+', top='+top+',screenX='+left+',screenY='+top+'');
}


//-----------------------------------
// reserved
function OpenAttach(sUrl){
	GetApiContent('GET', sUrl, null, oLib.sAttachDiv, 0);
	b2iShowApiDownloadPage(sUrl);
	currItem='';
}


//-----------------------------------
function DoApiCenter(Fwidth, Fheight){
	var tDiv = document.all ? document.all['LibStoryContainer'] : document.getElementById('LibStoryContainer');
	/*	var iScrollTop = document.body.scrollTop;
		if (iScrollTop == 0){
			if (window.pageYOffset)
				iScrollTop = window.pageYOffset;
			else
				iScrollTop = (document.body.parentElement) ? document.body.parentElement.scrollTop : 0;
		}
	*/	
	if (window.innerWidth)
		theWidth=window.innerWidth;
	else if (document.documentElement && document.documentElement.clientWidth)
		theWidth=document.documentElement.clientWidth;
	else if (document.body)
		theWidth=document.body.clientWidth;
	
	if (window.innerHeight)
		theHeight=window.innerHeight;
	else if (document.documentElement && document.documentElement.clientHeight)
		theHeight=document.documentElement.clientHeight;
	else if (document.body)
		theHeight=document.body.clientHeight;
	theHeight-=parseInt(oLib.iTopOffset);
	var centerX = theWidth/2 - (Fwidth / 2);
	var centerY = theHeight/2 - (Fheight / 2);
	
	tDiv.style.left= centerX + parseInt(oLib.iLeftOffset) + 'px';
	tDiv.style.display="block";
	tDiv.style.top = centerY + parseInt(oLib.iTopOffset) + 'px';
}


//-----------------------------------
function ResizeApiViewer(){
	var iNewWidth= window.innerWidth-oLib.iWidthOffset;
	var iNewHeight = window.innerHeight-oLib.iHeightOffset;
	
	if(oLib.iTopOffset!=0) iNewHeight =iNewHeight-parseInt(oLib.iTopOffset);
	
	if (oLib.iStoryMaxWidth!=0 && oLib.iStoryMaxWidth<iNewWidth){
		iNewWidth = parseInt(oLib.iStoryMaxWidth);
	}
	if (oLib.iStoryMaxHeight!=0 && oLib.iStoryMaxHeight<iNewHeight) {
		iNewHeight = parseInt(oLib.iStoryMaxHeight);
	}
	

	document.getElementById('LibStoryContainer').style.width = iNewWidth +'px';
	document.getElementById('LibStoryContainer').style.height = iNewHeight +'px';
	
	DoApiCenter(iNewWidth,iNewHeight);
	SwitchApiImage('Expand','Reduce');
}


//-----------------------------------
function ResetApiSize(){
	var iNewWidth = oLib.iStoryWidth;
	var iNewHeight = oLib.iStoryHeight;
	document.getElementById('LibStoryContainer').style.width = iNewWidth +'px';
	document.getElementById('LibStoryContainer').style.height = iNewHeight +'px';
	DoApiCenter(iNewWidth,iNewHeight);
	SwitchApiImage('Reduce','Expand');
}


//-----------------------------------
function CloseApiDiv(){
    try {
		var tDiv = document.getElementById('LibStoryContainer');
		if (tDiv) {
			tDiv.style.display="none";
		}
		currItemID='';
		currItem='';
		
		var oStoryDiv = document.getElementById(oLib.sStoryDiv);
		oStoryDiv.innerHTML="Loading...";
    } catch (error) {
        //console.log("Error in CloseApiDiv:", error);
    }
}


//-----------------------------------
function SwitchApiImage(HideID,ShowID){
	var oHideID = document.getElementById(HideID);
	var oShowID = document.getElementById(ShowID);
	oHideID.style.display="none";
	oShowID.style.display="";
}


//-----------------------------------
var startpos;
function dragboxstart(ev) {
    startpos = [ev.screenX, ev.screenY];
    ev.dataTransfer.setData("text/plain", ev.target.id);
}


//-----------------------------------
function dragboxend(ev) {
    var el = document.querySelector("#LibStoryContainer");
    var style = window.getComputedStyle(el, null);    
    var endpos = [ev.screenX, ev.screenY];
           
    el.style.top = Number(style.top.replace("px", '')) + (endpos[1] - startpos[1]) + "px";
    el.style.left = Number(style.left.replace("px", '')) + (endpos[0] - startpos[0]) + "px"; 
}


//-----------------------------------
function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}


var iSize=1;
function BiggerFont(){
	var x = document.getElementById("b2iNewsContainer");
	iSize=iSize+.3
	x.style.zoom=iSize;
	//-moz-transform:x.style.scale(2);
}


function SmallerFont(){
	var x = document.getElementById("b2iNewsContainer");
	iSize=iSize-.3
	x.style.zoom=iSize;
	//-moz-transform:x.style.scale(2);
}
