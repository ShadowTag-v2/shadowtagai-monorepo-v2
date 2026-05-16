
// JavaScript Document

var oQuote = {BizID:"", sKey:"", sDiv:"QuoteDiv", sHttp:"https", Symbol:"", SymbolDisplay:"", Exchange:"", Format:"1", Dollar:"1", DollarR:"", DecLen:"2", DateFormat:"0", CSS:"", sServer:"www.b2i.us", Upimage:"", Downimage:"", Centseperator:"", Numseperator:""};
var currItem='';


function getQuoteData(){
	currItem='';
	if(oQuote.BizID=='' || oQuote.sKey==''){
		console.log('Missing Business ID or API key. Please contact support at: support@b2itech.com so we can activate your account.');
		return;
	}
	if(oQuote.Symbol==''){console.log('Missing Symbol.');}
	var sUrl = oQuote.sHttp + "://" + oQuote.sServer + "/b2i/QuoteFeed.asp?b=" + oQuote.BizID + "&sdiv=" + oQuote.sDiv;
	if(oQuote.sKey!='') {sUrl += "&api=" + oQuote.sKey};
	if(oQuote.Symbol!='') {sUrl += "&s=" + oQuote.Symbol};
	if(oQuote.SymbolDisplay!='') {sUrl += "&sd=" + oQuote.SymbolDisplay};
	if(oQuote.Format!='') {sUrl += "&f=" + oQuote.Format};
	if(oQuote.Dollar!='') {sUrl += "&d=" + oQuote.Dollar};
	if(oQuote.DollarR!='') {sUrl += "&dr=" + oQuote.DollarR};
	if(oQuote.DecLen!='') {sUrl += "&dl=" + oQuote.DecLen};
	if(oQuote.DateFormat!='0') {sUrl += "&df=" + oQuote.DateFormat};
	if(oQuote.Exchange!='') {sUrl += "&e=1"};
	if(oQuote.CSS!='') {sUrl += "&css=" + oQuote.CSS};
	if(oQuote.Centseperator!='') {sUrl += "&cs=" + oQuote.Centseperator};
	if(oQuote.Numseperator!='') {sUrl += "&ns=" + oQuote.Numseperator};
	if(oQuote.Upimage!='') {sUrl += "&ui=1"};
	if(oQuote.Downimage!='') {sUrl += "&di=1"};
	
	//console.log(sUrl);
	//document.write(sUrl);
	if(document.getElementById(oQuote.sDiv)){
		GetQuoteApiContent('GET', sUrl, null, oQuote.sDiv, false);
	}
}

//////////////////////////////////////////////////////////////////////////////////////////////
function GetQuoteApiContent(requestType, sURL, varString, myDiv, bClose){
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
			//keep exchange cap for default return
			if(oQuote.Exchange!='') sReturn = sReturn.replace(/=Exchange=/gi, oQuote.Exchange);
			if(oQuote.Downimage!='') sReturn = sReturn.replace(/=downimage=/gi, oQuote.Downimage);
			if(oQuote.Upimage!='') sReturn = sReturn.replace(/=upimage=/gi, oQuote.Upimage);
			
			var oStoryDiv = document.getElementById(myDiv);
            oStoryDiv.innerHTML=sReturn;
			oStoryDiv.scrollTop = 0;
        }
    }
	
	xmlHttp.open(PostOrGet, sURL, true);
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlHttp.send(varString);
}
