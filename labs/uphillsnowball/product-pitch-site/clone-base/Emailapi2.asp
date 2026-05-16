
var oEmail = {BizID:"", sKey:"", sDiv:"EmailDiv", LangID:"1", InvID:"", InvKey:"", Group:"", List:"", ListSort:"", lo:"1", tos:"", tosLabel:"", tosControl:"", iPopoutDiv:0, sHttp:"https", sJoinEndPoint:"", sRemoveEndPoint:"", Unsubcribe:"1", ShowCompany:"1", ShowName:"1", ShowPhone:"0", ShowTitle:"0", ShowInvType:"0", ShowCust1:"0", ShowCust2:"0", ShowCust3:"0", ShowCust4:"0", ShowCust5:"0", CheckAllList:"0", HideAllList:"0", iStoryWidth:1000, iStoryHeight:1000, iLeftOffset:0, iTopOffset:0, LabelFirstName:"", LabelLastName:"", LabelCompany:"", LabelEmail:"", RequiredName:"0", sServer:"www.b2i.us", reCaptcha:"", sSubscribeText:"", sUnsubscribeText:""};

var isIE11 = !!window.MSInputMethodContext && !!document.documentMode;



//----------------------------------------
function getEmailAlertData(){
	if(oEmail.BizID=='') {
		alert('Business ID missing from Settings/B2i Options.');
		return;
	}
	
	if(getEmailCookie("cInvID")){
		var sTempInvID = getEmailCookie("cInvID");
		if(sTempInvID!='' && sTempInvID.toLowerCase()!='undefined'){
			oEmail.InvID=sTempInvID;
		}else{

			oEmail.InvID="";
			sTempInvID="";
		}
		//console.log(oEmail.InvID);
	}
	
	if(getEmailCookie("cInvKey")){
		var sTempKey = getEmailCookie("cInvKey");
		if(sTempKey!='' && sTempKey.toLowerCase()!='undefined'){
			oEmail.InvKey=sTempKey;
		}else{
			sTempInvID="";
			sTempKey="";
			oEmail.InvID="";
			oEmail.InvKey="";
		}
		//console.log(oEmail.InvKey);
	}
	
	var sUrl = oEmail.sHttp + "://" + oEmail.sServer + "/profiles/investor/EmailAlert2.asp?B=" + oEmail.BizID + "";
	if(oEmail.sKey!='') {sUrl += "&api=" + oEmail.sKey};
	if(oEmail.LangID!='') {sUrl += "&l=" + oEmail.LangID};
	if(oEmail.Group!='') {sUrl += "&g=" + oEmail.Group};
	if(oEmail.List!='') {sUrl += "&lid=" + oEmail.List};
	if(oEmail.ListSort!='') {sUrl += "&ls=" + oEmail.ListSort};
	
	if(oEmail.lo!='1') {sUrl += "&lo=" + oEmail.lo};

	if(oEmail.ShowCompany!='1') {sUrl += "&sc=" + oEmail.ShowCompany}; 
	if(oEmail.ShowName!='1') {sUrl += "&sn=" + oEmail.ShowName}; 
	if (oEmail.RequiredName=='1' || oEmail.RequiredName==true) {sUrl += "&rn=" + oEmail.RequiredName}; 

	if(oEmail.ShowPhone!='0') {sUrl += "&sph=" + oEmail.ShowPhone}; 
	if(oEmail.ShowTitle!='0') {sUrl += "&sti=" + oEmail.ShowTitle}; 
	if(oEmail.ShowInvType!='1') {sUrl += "&sit=" + oEmail.ShowInvType}; 
	
	if(oEmail.ShowCust1!='0') {sUrl += "&sc1=" + oEmail.ShowCust1}; 
	if(oEmail.ShowCust2!='0') {sUrl += "&sc2=" + oEmail.ShowCust2}; 
	if(oEmail.ShowCust3!='0') {sUrl += "&sc3=" + oEmail.ShowCust3}; 
	if(oEmail.ShowCust4!='0') {sUrl += "&sc4=" + oEmail.ShowCust4}; 
	if(oEmail.ShowCust5!='0') {sUrl += "&sc5=" + oEmail.ShowCust5}; 

	if(oEmail.LabelFirstName!='') {sUrl += "&lfn=1"};
	if(oEmail.LabelLastName!='') {sUrl += "&lln=1"};
	if(oEmail.LabelCompany!='') {sUrl += "&lc=1"};
	if(oEmail.LabelEmail!='') {sUrl += "&le=1"};
	if(oEmail.tos!='') {sUrl += "&tos=1"};
	if(oEmail.tosLabel!='') {sUrl += "&tosL=1"};
	if(oEmail.tosControl!='') {sUrl += "&tosC=1"};
	if(oEmail.Unsubcribe!='') {sUrl += "&us=" + oEmail.Unsubcribe};

	if(oEmail.sSubscribeText!='') {sUrl += "&st=1"};
	if(oEmail.sUnsubscribeText!='') {sUrl += "&ut=1"};
	

	if(oEmail.InvID!='' && oEmail.InvKey!='') {
		sUrl += "&i=" + oEmail.InvID + "&ik=" + oEmail.InvKey
	}else{
		if(oEmail.CheckAllList!='0') {sUrl += "&ca=" + oEmail.CheckAllList};
	}
	if(oEmail.HideAllList!='0') {sUrl += "&ha=" + oEmail.HideAllList};
	//if(oEmail.InvKey!='') {sUrl += "&ik=" + oEmail.InvKey};
	
	//console.log(sUrl);
	GlobalEmailAjax('GET', sUrl, null, oEmail.sDiv);
}



//----------------------------------------
function GlobalEmailAjax(requestType, sURL, varString, myDiv){
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
			
			if(oEmail.tosLabel!='') sReturn = sReturn.replace(/=tosLabel=/gi, oEmail.tosLabel);
			
			if(oEmail.LabelFirstName!='') sReturn = sReturn.replace(/=LabelFirstName=/gi, oEmail.LabelFirstName);
			if(oEmail.LabelLastName!='') sReturn = sReturn.replace(/=LabelLastName=/gi, oEmail.LabelLastName);
			if(oEmail.LabelCompany!='') sReturn = sReturn.replace(/=LabelCompany=/gi, oEmail.LabelCompany);
			if(oEmail.LabelEmail!='') sReturn = sReturn.replace(/=LabelEmail=/gi, oEmail.LabelEmail);
			
			var oStoryDiv = document.getElementById(myDiv);
            oStoryDiv.innerHTML=sReturn;
			oStoryDiv.scrollTop = 0;
        }
    }

	if(!isIE11){
		xmlHttp.responseType = 'text';
	}

	xmlHttp.open(PostOrGet, sURL, true);
	xmlHttp.overrideMimeType('text/xml; charset=iso-8859-1');
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlHttp.send(varString);
}


//----------------------------------------
function B2iSaveEmailAlert(){
	var sURL=oEmail.sHttp + "://" + oEmail.sServer + "/profiles/investor/EmailAlert2Save.asp";
	var ListIDs=GetListOfEmailChecked();
	var sRemove = document.getElementById("sListRemove").value;
	//console.log("sRemove:" + sRemove);
	var BizID = document.getElementById("BizID").value;
	var InvID = oEmail.InvID;
	var InvKey = oEmail.InvKey;
	var sformKey;
	var sFirstName;
	var sLastName;
	var sCompany;
	var sEmail;
	var sPhone='';
	var sTitle='';
	var iInvType=1;
	var sError='';
	var sSubscribeText;
	var seaCust1='';
	var seaCust2='';
	var seaCust3='';
	var seaCust4='';
	var seaCust5='';
	
	var SaveButton = document.getElementById("b2iEmailAlertSubmit");
	SaveButton.disabled = true;
	
	//new blank form load
	if(document.getElementById("Email")){
		sEmail = document.getElementById("Email").value;
		if (sEmail!=undefined){
			var stEmail = sEmail.replace(" ", "");
		}
	}
	
	//reloaded with cookie value
	if(sEmail==undefined || sEmail==''){
		if(document.getElementById("eaEmail")){
			sEmail = document.getElementById("eaEmail").value;
			var stEmail = sEmail.replace(" ", "");
			if(stEmail==''){
				sError='Email required<br>';
			}
		}
	}


	if(document.getElementById("formKey")){
		sformKey = document.getElementById("formKey").value;
	}

	if (validateEmail(stEmail)) {
	} else {
		sError='Error: Email invalid<br>';
	}

	
	if(document.getElementById("eaFirstName")){
		sFirstName = document.getElementById("eaFirstName").value;
		if((oEmail.RequiredName=='1' || oEmail.RequiredName==true) && sFirstName==''){
			sError=sError + 'Error: First name required<br>';
		}
		if(sFirstName!=''){0
			var stFirstName = sFirstName.replace(" ", "");
		}
	}
	if(document.getElementById("eaLastName")){
		sLastName = document.getElementById("eaLastName").value;
		if( (oEmail.RequiredName=='1' || oEmail.RequiredName==true) && sLastName==''){
			sError=sError + 'Error: Last name required<br>';
		}
		if(sLastName!=''){
			var stLastName = sLastName.replace(" ", "");
		}
	}
	if (oEmail.tos!=""){
		var oTos = document.getElementById("tos")
		if(!oTos.checked){
			sError=sError + 'You must agree to the Terms of Use to continue<br>';
		}
	}

	var ListSelected;
	ListSelected=false;
	var EmailList = document.getElementsByName('PubEmail');
	for(var i=0; i< EmailList.length; ++i){
		if(EmailList[i].checked){
			ListSelected=true;
			break;
		}
	}
	if(ListSelected==false){
		sError=sError + 'Error: Select a list<br>';
	}

	if(document.getElementById("eaCompany")){
		sCompany = document.getElementById("eaCompany").value;
	}
	
	
	if(document.getElementById("eaTitle")){
		sTitle = document.getElementById("eaTitle").value;
	}
	
	if(document.getElementById("eaPhone")){
		sPhone = document.getElementById("eaPhone").value;
	}
	

	var InvType;
	if(document.getElementById("eaInvType")){
		InvType = document.getElementById("eaInvType");
		iInvType = InvType.options[InvType.selectedIndex].value;
	}


	if(document.getElementById("SubscribeText")){
		sSubscribeText = document.getElementById("SubscribeText").value;
	}

	
	var varString = "b=" + escape(BizID);
	
	if(oEmail.InvID!=""){
		varString += "&i=" + escape(oEmail.InvID);
	}
	if(oEmail.InvKey!=""){
		varString += "&ik=" + escape(oEmail.InvKey);
	}
	if(ListIDs!=undefined && ListIDs!=""){
		varString += "&list=" + escape(ListIDs);
	}
	if(sFirstName!=undefined){
		varString += "&fn=" + escape(sFirstName);
	}
	if(sLastName!=undefined){
		varString += "&ln=" + escape(sLastName);
	}
	if(sCompany!=undefined){
		varString += "&c=" + escape(sCompany);
	}
	if(sEmail!=undefined){
		varString += "&e=" + escape(sEmail);
	}


	if(sPhone!=undefined && sPhone!=''){
		varString += "&ph=" + escape(sPhone);
	}
	if(sTitle!=undefined && sTitle!=''){
		varString += "&t=" + escape(sTitle);
	}
	if(iInvType!=1){
		varString += "&invt=" + escape(iInvType);
	}



	if(document.getElementById("eaCust1")){
		seaCust1 = document.getElementById("eaCust1").value;
		if(seaCust1 !=undefined && seaCust1!=''){
			varString += "&eaCust1=" + escape(seaCust1);
		}
	}

	if(document.getElementById("eaCust2")){
		seaCust2 = document.getElementById("eaCust2").value;
		if(seaCust2 !=undefined && seaCust2!=''){
			varString += "&eaCust2=" + escape(seaCust2);
		}
	}

	if(document.getElementById("eaCust3")){
		seaCust3 = document.getElementById("eaCust3").value;
		if(seaCust3 !=undefined && seaCust3!=''){
			varString += "&eaCust3=" + escape(seaCust3);
		}
	}

	if(document.getElementById("eaCust4")){
			seaCust4= document.getElementById("eaCust4").value;
		if(seaCust4 !=undefined && seaCust4!=''){
			varString += "&eaCust4=" + escape(seaCust4);
		}
	}

	if(document.getElementById("eaCust5")){
		seaCust5 = document.getElementById("eaCust5").value;
		if(seaCust5 !=undefined && seaCust5!=''){
			varString += "&eaCust5=" + escape(seaCust5);
		}
	}




	if (sRemove!=''){
		varString += "&Remove=" + escape(sRemove);
	}
	if (sSubscribeText!=undefined){
		varString += "&st=1";
	}

	if(sformKey!=""){
		varString += "&formKey=" + escape(sformKey);
	}
	
	var oB2iSaveReturn = document.getElementById("B2iSaveReturn");
	if(sError!=''){
		oB2iSaveReturn.innerHTML=sError;
		oB2iSaveReturn.style.display="block";
		SaveButton.disabled = false;
		return;
	}else{
		oB2iSaveReturn.innerHTML='';
		if(sEmail)
			document.getElementById("B2iSavedEmail").innerHTML=sEmail;
			
		console.log(varString);
		
		var oStoryDiv = document.getElementById('B2iSaveReturn');
		oStoryDiv.className="b2iChanged";
		DoEmailFormSave(2, sURL, varString, 'B2iSaveReturn');
	}
}


//----------------------------------------
//Do setTimeOut function for 4 min 45 sec
setTimeout(function(){
    var oSaveButton = document.getElementById("b2iEmailAlertSubmit");
	//oSaveButton.disabled=true;
	oSaveButton.value="Reload form";
	oSaveButton.ondoubleclick = function refreshme(){location.reload();};
	oSaveButton.onclick = function refreshme(){location.reload();};
}, 285000);
//----------------------------------------


//----------------------------------------
function validateEmail(email) {
	//var pattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/; other test
	const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	return re.test(String(email).toLowerCase());
}


//----------------------------------------
function DoEmailFormSave(requestType, sURL, varString, myDiv){
	// requestType:  	1 = get Else post
	// sURL: 			page requested
	// varString: 		null if none
	// myDiv:			where to put returned value

	var oStoryDiv = document.getElementById(myDiv);
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
			var sRet = xmlHttp.responseText;
			
			if(oEmail.sSubscribeText!='') sRet = sRet.replace(/=SubscribeText=/gi, oEmail.sSubscribeText);
			if(oEmail.sUnsubscribeText!='') sRet = sRet.replace(/=UnsubscribeText=/gi, oEmail.sUnsubscribeText);

			//console.log('sRet:' + sRet);

			var myJSON = JSON.parse(sRet);
			var jInvID = myJSON.InvID;
			var jInvKey = myJSON.InvKey;
			var jStatus = myJSON.Status;
			

			if(jStatus!=3){
				if(myDiv!='B2iUnsubReturn'){
					if(jInvID!='' && jInvKey!=''){
						oEmail.InvID=jInvID;
						oEmail.InvKey=jInvKey;
						setEmailCookie("cInvID",oEmail.InvID,180);
						setEmailCookie("cInvKey",oEmail.InvKey,180);
						setEmailCookie("cInvk",oEmail.InvKey,180);
						if(document.getElementById("b2iEmailSignUp")){
							document.getElementById("b2iEmailSignUp").style.display="none";
						}
						document.getElementById("b2iEmailSignUpFound").style.display="block";
					}
					
					oStoryDiv.innerHTML=myJSON.sReturn;
					oStoryDiv.className="b2iSaved";
					if(jStatus=='1' && oEmail.sJoinEndPoint!=''){
						document.location=oEmail.sJoinEndPoint;
					}
					
					var SaveButton = document.getElementById("b2iEmailAlertSubmit");
					SaveButton.disabled = false;

				} else {
					oStoryDiv.innerHTML=myJSON.sReturn;
					oStoryDiv.className="b2iSaved";
					if(jStatus=='1' && oEmail.sRemoveEndPoint!=''){
						document.location=oEmail.sRemoveEndPoint;
					}
				}
			}else{
				oStoryDiv.innerHTML=myJSON.sReturn;
				oStoryDiv.className="b2iSaved";
				var SaveButton = document.getElementById("b2iEmailAlertSubmit");
				SaveButton.disabled = false;
			}
        }
    }
	
	if(!isIE11){
		xmlHttp.responseType = 'text';}
	
	xmlHttp.open(PostOrGet, sURL, true);
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlHttp.send(varString);
}



//----------------------------------------
function B2iUnsubscribe() {
	var sURL=oEmail.sHttp + "://" + oEmail.sServer + "/profiles/investor/EmailAlert2Save.asp";
	var ListIDs=GetListOfEmailChecked();	
	var BizID = document.getElementById("BizID").value;
	var InvID = oEmail.InvID;
	var InvKey = oEmail.InvKey;
	var sEmail;
	var sError='';
	var sUnsubscribeText;
	
	
	if(document.getElementById("eaEmail")){
		sEmail = document.getElementById("eaEmail").value;
		var stEmail = sEmail.replace(" ", "");
		if(stEmail==''){
			sError='Email required<br>';
		}
	}

	if(document.getElementById("UnsubscribeText")){
		sUnsubscribeText = document.getElementById("UnsubscribeText").value;
	}

	var varString = "b=" + escape(BizID);
	varString += "&us=1&list=";
	
	if(oEmail.InvID!=""){
		varString += "&i=" + escape(oEmail.InvID);
	}
	if(oEmail.InvKey!=""){
		varString += "&ik=" + escape(oEmail.InvKey);
	}
		
	if(sEmail!=undefined){
		varString += "&e=" + escape(sEmail);
	}

	if (sUnsubscribeText!=undefined){
		varString += "&ut=1";
	}

	
	var oB2iSaveReturn = document.getElementById("B2iUnsubReturn");
	if(sError!=''){
		oB2iSaveReturn.innerHTML=sError;
		oB2iSaveReturn.style.display="block";
		return;
	}else{
		oB2iSaveReturn.innerHTML='';
		if(sEmail)
			document.getElementById("B2iSavedEmail").innerHTML=sEmail;
	}
	
	var oStoryDiv = document.getElementById('B2iUnsubReturn');
	oStoryDiv.className="b2iChanged";
	DoEmailFormSave(2, sURL, varString, 'B2iUnsubReturn');
}


//---------------------------------------------------------------
function setEmailCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    if (oEmail.sHttp!="https"){
		document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/;SameSite=None;";
	}else{
		document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/;SameSite=None; Secure";
	}
}


//---------------------------------------------------------------
function delEmailCookie() {
	oEmail.InvID="";
	oEmail.InvKey="";
	document.cookie = "cInvID=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;SameSite=None; Secure";
	document.cookie = "cInvKey=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;SameSite=None; Secure";
	document.cookie = "cInvk=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;SameSite=None; Secure";
	getEmailAlertData();
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


//---------------------------------------------------------------
function GetListOfEmailChecked(){
	var sIds='';
	var sUncheckedIds='';
	var element = document.getElementsByName("PubEmail");
	for(var i=0; i < element.length; i++){
		if(element[i].checked){
			if(sIds==''){
				sIds=element[i].value;
			}else{
				sIds+= ',' + element[i].value;
			}
		}else{
			if(sUncheckedIds==''){
				sUncheckedIds=element[i].value;
			}else{
				sUncheckedIds+= ',' + element[i].value;
			}
		}
	}
	
	//console.log(sUncheckedIds);
	var oListRemove = document.getElementById('sListRemove');
	oListRemove.value=sUncheckedIds;
	
	return sIds;
}


//---------------------------------------------------------------
function ToggleHide(sItemID){
	var oitem = document.getElementById(sItemID);
	oitem.classList.toggle("b2iemailhide");
}



//---------------------------------------------------------------
function GetRecaptcha() {
	document.getElementById("b2iEmailAlertSubmit").addEventListener("click",function(evt)
	{

	if (window.grecaptcha) {
		alert("yes");
	}else{
		alert("No");
	}
	
	var response = grecaptcha.getResponse();
	if(response.length == 0) 
	{ 
		//reCaptcha not verified
		alert("please verify you are humann!"); 
		evt.preventDefault();
		return false;
	}

		
	//captcha verified
	//do the rest of your validations here
	
	});
}

