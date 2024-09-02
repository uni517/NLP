//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var pauseButton = document.getElementById("pauseButton");
//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);
pauseButton.addEventListener("click", pauseRecording);

var check1Button = document.getElementById("vehicle1");
var check2Button = document.getElementById("vehicle2");
var check3Button = document.getElementById("vehicle3");
var check11Button = document.getElementById("vehicle11");
var check21Button = document.getElementById("vehicle21");
var check31Button = document.getElementById("vehicle31");
check1Button.addEventListener("click", en_check_button, true);
check2Button.addEventListener("click", en_check_button_audio, true);
check3Button.addEventListener("click", en_check_button, true);
check11Button.addEventListener("click", zh_check_button, true);
check21Button.addEventListener("click", zh_check_button, true);
check31Button.addEventListener("click", zh_check_button_audio, true);
//check3Button.addEventListener("click", en_check_button_audio, true);




var zh_display_box = document.getElementById("zhtext");
var en_array = [];
var zh_array = [];
function en_check_button(){
	var sentence = "";
	if (en_array[0] != '' & check1Button.checked){
		sentence += en_array[0]+'\n';
	}
	if (en_array[1] != '' & check3Button.checked){
		sentence += en_array[1]+'\n';
	}
	zh_display_box.textContent = sentence
}
function zh_check_button(){
	var sentence = "";
	if (zh_array[0] != '' & check11Button.checked){
		sentence += zh_array[0]+'\n';
	}
	if (zh_array[1] != '' & check21Button.checked){
		sentence += zh_array[1]+'\n';
	}
	zh_display_box.textContent = sentence;
}
function en_check_button_audio(){
	//對話翻譯語音
	if (check2Button.checked){
		var audio2 = document.getElementById('myAudioElement2') || new Audio();
		var xhr2=new XMLHttpRequest();
		xhr2.open("POST","/js_audio2",true);
		xhr2.responseType = 'blob';
		xhr2.onload = function(evt) {
		var blob = new Blob([xhr2.response], {type: 'audio/wav'});
		var objectUrl = URL.createObjectURL(blob);
		audio2.src = objectUrl;
		// Release resource when it's loaded
		audio2.onload = function(evt) {
		URL.revokeObjectURL(objectUrl);
		};
		audio2.play();
		};
		xhr2.send();
	}
	
}
function zh_check_button_audio(){
	if (check31Button.checked){
		var audio3 = document.getElementById('myAudioElement2') || new Audio();
		var xhr3=new XMLHttpRequest();
		xhr3.open("POST","/js_audio3",true);
		xhr3.responseType = 'blob';
		xhr3.onload = function(evt) {
		var blob = new Blob([xhr3.response], {type: 'audio/wav'});
		var objectUrl = URL.createObjectURL(blob);
		audio3.src = objectUrl;
		// Release resource when it's loaded
		audio3.onload = function(evt) {
		URL.revokeObjectURL(objectUrl);
		};
		audio3.play();
		};
		xhr3.send();
	}
}


function startRecording() {
	console.log("recordButton clicked");

	/*
		Simple constraints object, for more advanced audio features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/
    
    var constraints = { audio: true, video:false }

 	/*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

	recordButton.disabled = true;
	stopButton.disabled = false;
	pauseButton.disabled = false

	/*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device
		*/
		audioContext = new AudioContext();

		

		/*  assign to gumStream for later use  */
		gumStream = stream;
		
		/* use the stream */
		input = audioContext.createMediaStreamSource(stream);
		/* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
		rec = new Recorder(input,{numChannels:1})
		//start the recording process
		rec.record()

		console.log("Recording started");

	}).catch(function(err) {
	  	//enable the record button if getUserMedia() fails
    	recordButton.disabled = false;
    	stopButton.disabled = true;
    	pauseButton.disabled = true
	});
}

function pauseRecording(){
	console.log("pauseButton clicked rec.recording=",rec.recording );
	if (rec.recording){
		//pause
		rec.stop();
		pauseButton.innerHTML="Resume";
	}else{
		//resume
		rec.record()
		pauseButton.innerHTML="Pause";

	}
}

function stopRecording() {
	console.log("stopButton clicked");

	//disable the stop button, enable the record too allow for new recordings
	stopButton.disabled = true;
	recordButton.disabled = false;
	pauseButton.disabled = true;

	//reset button just in case the recording is stopped while paused
	pauseButton.innerHTML="Pause";
	
	//tell the recorder to stop the recording
	rec.stop();

	//stop microphone access
	gumStream.getAudioTracks()[0].stop();

	//create the wav blob and pass it on to createDownloadLink
	rec.exportWAV(createDownloadLink);
}





function createDownloadLink(blob) {
	upload(blob);
	function upload(blob) {
	  var xhr=new XMLHttpRequest();
	  
	  //取radiobutton值
	  var value="";
	  var radio=document.getElementsByName("language");
	  for(var i=0;i<radio.length;i++){
	  if(radio[i].checked==true){
	  value=radio[i].value;
	  console.log(value);
	  break;
	  }
	  }

	  xhr.onload=function() {
		  //中文語音回傳文字
		  if(this.readyState === 4 & value === "1") {
			en_array[0] = '';
			en_array[1] = '';
			en_array[2] = '';
			var str = JSON.parse(xhr.responseText);
			zh_array[0]=str["zh_asr"];
			zh_array[1]=str["zh_translation"];

		   //英文語音回傳文字
		  }else if(this.readyState === 4 & value === "2"){
			console.log(xhr.responseText);
			zh_array[0] = '';
			zh_array[1] = '';
			zh_array[2] = '';
			var str = JSON.parse(xhr.responseText);
			if(str["en_asr"] != ""){

				let box = document.getElementById("DialogBox");

				var Odiv1 = document.createElement("div");
				var Odiv2 = document.createElement("div");
				var Op = document.createElement("p");

				Odiv1.className='outgoing_msg'
				Odiv2.className='sent_msg'
				Op.textContent=str["en_asr"]

				box.appendChild(Odiv1);
				Odiv1.appendChild(Odiv2);
				Odiv2.appendChild(Op);
				
				var Odiv3 = document.createElement("div");
				var Odiv4 = document.createElement("div");
				var Opp = document.createElement("p");

				Odiv3.className='received_msg'
				Odiv4.className='received_withd_msg'
				Opp.textContent=str["dialog_generate"]

				box.appendChild(Odiv3);
				Odiv3.appendChild(Odiv4);
				Odiv4.appendChild(Opp);

				en_array[0] = str["en_translation"];
				en_array[1] = str["en_dic_translation"];


				//對話語音
				var audio1 = document.getElementById('myAudioElement1') || new Audio();
				var xhrr=new XMLHttpRequest();
				xhrr.open("POST","/js_audio1",true);
				xhrr.responseType = 'blob';
				xhrr.onload = function(evt) {
				var blob = new Blob([xhrr.response], {type: 'audio/wav'});
				var objectUrl = URL.createObjectURL(blob);

				audio1.src = objectUrl;
				// Release resource when it's loaded
				audio1.onload = function(evt) {
				URL.revokeObjectURL(objectUrl);
				};
				audio1.play();
				};
				xhrr.send();

				
				
				
			}
			
			
		  }
		  
	  };
	  
	  var filename = new Date().toISOString();
	  var fd=new FormData();
	  fd.append("audio_data", blob, filename);
	  if (value === "2"){
		xhr.open("POST","/js_call2",true);
		xhr.send(fd);
	  }else{
		xhr.open("POST","/js_call1",true);
		xhr.send(fd);
	  }
	}




}


