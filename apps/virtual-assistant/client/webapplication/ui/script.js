/*
# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# top-level README.md file.
# ==============================================================================
*/

var endpoint;
var bot;
var context = {};
var payload = {};
var scrollToBottomTime = 500;
var infoTextArea; //element for context display
var debug = false; //if true display context
var user_conversation_index = null;
var socket = null;
var tts_enabled = false;
var browser = "";
var error_servicerecall_limits = {"get_new_user_conversation_index": 2, "init": 2};
var error_servicerecall_currentcnt = {"get_new_user_conversation_index": 0, "init": 0};
var error_systemerrormessages_info = {
	"get_new_user_conversation_index": {
		"text": "There was an error during a service call. We are unable to proceed further. Please check the console for the Error Log. \n Please resolve this server error and refresh the page to continue",
		"targetDivText": "Error during Service Call. Unable to proceed."
	}, "init": {
		"text": "There was an error during a service call. We are unable to proceed further. Please check the console for the Error Log. \n Please resolve this server error and refresh the page to continue",
		"targetDivText": "Error during Service Call. Unable to proceed."
	}, "sendInput": {
		"text": "There was an error during a service call. We are unable to proceed further. Please check the console for the Error Log. \n Please resolve this server error and refresh the page to continue",
		"targetDivText": "Error during Service Call. Unable to proceed."
	}
};

function disableUserInput() {
	$("#input_field").prop('disabled', true);
	$("#submit").prop('disabled', true);
	$("#autosubmitcheck").prop('disabled', true);
	$("#unmuteButton").prop('disabled', true);
}

function enableUserInput() {
	$("#input_field").prop('disabled', false);
	$("#submit").prop('disabled', false);
	$("#autosubmitcheck").prop('disabled', false);
	$("#unmuteButton").prop('disabled', false);
}

// ---------------------------------------------------------------------------------------
// Defines audio src and event handlers for TTS audio
// ---------------------------------------------------------------------------------------
function initTTS() {
	// Set TTS Source as the very first thing
	  let audio = document.getElementById("audio-tts");
	  // Change source to avoid caching
	  audio.src = "/audio/" + user_conversation_index + "/" + new Date().getTime().toString();
	  audio.addEventListener(
	    "onwaiting",
	    function () {
	      console.log("Audio is currently waiting for more data");
	    },
	    false
	  );
	  audio.onplaying = function () {
	    console.log("Audio Playing.");
	  };
	  audio.onwaiting = function () {
	    console.log("Audio is currently waiting for more data");
	  };
	  audio.onended = function () {
	    console.log("Audio onended");
	  };
	  audio.onpause = function () {
	    console.log("Audio onpause");
	  };
	  audio.onstalled = function () {
	    console.log("Audio onstalled");
	    if (browser == "Chrome") {
	    	socket.emit("unpause_asr", { "user_conversation_index": user_conversation_index, "on": "TTS_END" });
	    }
	  };
	  audio.onsuspend = function () {
	    console.log("Audio onsuspend");
	  };
	  audio.oncanplay = function () {
	    console.log("Audio oncanplay");
	  };
	  // Chrome will refuse to play without this
	  let unmuteButton = document.getElementById("unmuteButton");
	  unmuteButton.addEventListener("click", function () {
	    if (unmuteButton.innerText == "Unmute System Speech") {
	      tts_enabled = true;
	      socket.emit("start_tts", { "user_conversation_index": user_conversation_index });
	      unmuteButton.innerText = "Mute System Speech";
	      console.log("TTS Play button clicked");
	      audio.play();
	    } else {
	      tts_enabled = false;
	      socket.emit("stop_tts", { "user_conversation_index": user_conversation_index });
	      unmuteButton.innerText = "Unmute System Speech";
	      console.log("TTS Stop button clicked");
	    }
	  });
	  audio.load();
      audio.play();
}

// ---------------------------------------------------------------------------------------
// Initializes input audio (mic) stream processing
// ---------------------------------------------------------------------------------------
function initializeRecorderAndConnectSocket() {
  let namespace = "/";
  let mediaStream = null;
  
  // audio recorder functions
  let initializeRecorder = function (stream) {
    // https://stackoverflow.com/a/42360902/466693
    mediaStream = stream;
    // get sample rate
    audio_context = new AudioContext();
    sampleRate = audio_context.sampleRate;
    let audioInput = audio_context.createMediaStreamSource(stream);
    let bufferSize = 4096;
    // record only 1 channel
    let recorder = audio_context.createScriptProcessor(bufferSize, 1, 1);
    // specify the processing function
    recorder.onaudioprocess = function (audioProcessingEvent) {
      // socket.emit('sample_rate', sampleRate);
      // The input buffer is the song we loaded earlier
      let inputBuffer = audioProcessingEvent.inputBuffer;
      // Loop through the output channels (in this case there is only one)
      for (let channel = 0; channel < 1; channel++) {
        let inputData = inputBuffer.getChannelData(channel);
        function floatTo16Bit(inputArray, startIndex) {
          let output = new Int16Array(inputArray.length / 3 - startIndex);
          for (let i = 0; i < inputArray.length; i += 3) {
            let s = Math.max(-1, Math.min(1, inputArray[i]));
            output[i / 3] = s < 0 ? s * 0x8000 : s * 0x7fff;
          }
          return output;
        }
        outputData = floatTo16Bit(inputData, 0);
        socket.emit("audio_in", 
        		{ "user_conversation_index": user_conversation_index, "audio": outputData.buffer });
      }
    };
    // connect stream to our recorder
    audioInput.connect(recorder);
    // connect our recorder to the previous destination
    recorder.connect(audio_context.destination);
  };

  console.log("socket connection");
  if (socket == null) {
    socket = io.connect(
      location.protocol + "//" + document.domain + ":" + location.port + namespace
    );
    socket.on("connect", function () {
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then(initializeRecorder)
        .catch(function (err) {
          console.log(">>> ERROR on Socket Connect");
        });
    });
  } else {
    socket.disconnect();
    socket.connect();
  }
  
  // To stop open tts buffer from previous session, if any.
  socket.emit("stop_tts", { "user_conversation_index": user_conversation_index });
  socket.emit("pause_asr", { "user_conversation_index": user_conversation_index });
  
  socket.on('onCompleteOf_unpause_asr', function(data) {
      if (data["user_conversation_index"]==user_conversation_index) {
    	  enableUserInput();
      }
  });
}

// -----------------------------------------------------------------------------
// Retrieves a new "user conversation index" from RivaDM
// -----------------------------------------------------------------------------
function get_new_user_conversation_index() {
  $.ajax({
    url: endpoint + "get_new_user_conversation_index",
    type: "get",
    processData: false,
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data, textStatus, jQxhr) {
      error_servicerecall_currentcnt["get_new_user_conversation_index"] = 0;
      if (data) {
    	  user_conversation_index = data;
    	  initializeRecorderAndConnectSocket();
    	  init();
      } else {
    	  console.log("No new_user_conversation_index");
    	  showSystemErrorMessage("get_new_user_conversation_index", "No new_user_conversation_index");
          disableUserInput();
      }
    },
    error: function (jqXhr, textStatus, errorThrown) {
      console.log(errorThrown);
      if (error_servicerecall_currentcnt["get_new_user_conversation_index"] < error_servicerecall_limits["get_new_user_conversation_index"]) {
  		  // If Rivadm doesn't response, wait and try it again
      	  error_servicerecall_currentcnt["get_new_user_conversation_index"] = error_servicerecall_currentcnt["get_new_user_conversation_index"] + 1;
          setTimeout(get_new_user_conversation_index(), 3000);
      } else {
          error_servicerecall_currentcnt["get_new_user_conversation_index"] = 0;  
          showSystemErrorMessage("get_new_user_conversation_index", errorThrown);
          disableUserInput();
      }
    },
  });
}

// -----------------------------------------------------------------------------
// Call init state
// -----------------------------------------------------------------------------
function init() {
  console.log("init");
  $.ajax({
    url: endpoint,
    type: "post",
    processData: false,
    data: JSON.stringify({
      "text": '',
      "bot": bot,
      "context": context,
      "payload": payload,
      "user_conversation_index": user_conversation_index
    }),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data, textStatus, jQxhr) {
      error_servicerecall_currentcnt["init"] = 0;
      if (data["ok"]) {
    	  if (data["debug"]) {
	        infoTextArea.style.display = "block";
	      }
          context = data["context"];
          payload = {};
          showSystemMessages(data["messages"]);
	      initTTS();
	      listenASR();
		  socket.emit("unpause_asr", { "user_conversation_index": user_conversation_index, "on": "REQUEST_COMPLETE" });
		  if (tts_enabled == false) {
	    	  enableUserInput();
	      } else if (tts_enabled == true && browser == "Firefox") {
	    	  socket.emit("pause_wait_unpause_asr", { "user_conversation_index": user_conversation_index });
	      }
      } else {
        console.log("Data is not okay!")
    	  console.log(data["messages"]);
    	  showSystemErrorMessage("init", data["messages"]);
          disableUserInput();
      }
    },
    error: function (jqXhr, textStatus, errorThrown) {
      console.log(errorThrown);
      if (error_servicerecall_currentcnt["init"] < error_servicerecall_limits["init"]) {
    	  // If Rivadm doesn't response, wait and try it again
    	  error_servicerecall_currentcnt["init"] = error_servicerecall_currentcnt["init"] + 1;
    	  setTimeout(init(), 3000);
      } else {
          error_servicerecall_currentcnt["init"] = 0;  
          showSystemErrorMessage("init", errorThrown);
          disableUserInput();
      }
    },
  });
}

// ---------------------------------------------------------------------------------------
// Send user input to RivaDM by REST
// ---------------------------------------------------------------------------------------
function sendInput(text) {
  socket.emit("pause_asr", { "user_conversation_index": user_conversation_index });
  disableUserInput();
  // escape html tags
  text = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  console.log("sendInput:" + text);
  $.ajax({
    url: endpoint,
    dataType: "json",
    type: "post",
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify({
      "text": text,
      "bot": bot,
      "context": context,
      "payload": payload,
      "user_conversation_index": user_conversation_index
    }),
    processData: false,
    success: function (data, textStatus, jQxhr) {
    	if (data["ok"]) {
    	  if (data["debug"]) {
	        infoTextArea.style.display = "block";
	      }
          context = data["context"];
          payload = {};
	      showSystemMessages(data["messages"]);
	      socket.emit("unpause_asr", { "user_conversation_index": user_conversation_index, "on": "REQUEST_COMPLETE" });
	      if (tts_enabled == false) {
	    	  enableUserInput();
	      } else if (tts_enabled == true && browser == "Firefox") {
	    	  socket.emit("pause_wait_unpause_asr", { "user_conversation_index": user_conversation_index });
	      }
	    } else {
	  	  console.log(data["messages"]);
	  	  showSystemErrorMessage("sendInput", data["messages"]);
	      disableUserInput();
	    }
    },
    error: function (jqXhr, textStatus, errorThrown) {
      console.log(errorThrown);
      showSystemErrorMessage("sendInput", errorThrown);
      disableUserInput();
    },
  });
}

function getTimeSting() {
  var d = new Date();
  var ampm = "";
  var h = d.getHours();
  var m = d.getMinutes();
  if (h==0) {
	  h = "12"; ampm = "am";
  } else if (h<12) {
	  ampm = "am";
  } else if (h==12) {
	  ampm = "pm";
  } else {
	  h = h-12; ampm = "pm";
  }
  if (m>=0 && m<=9) {
	  m = "0" + m
  }
  return h + ":" + m + " " + ampm;
}

// ---------------------------------------------------------------------------------------
// Shows responses of RivaDM
// ---------------------------------------------------------------------------------------
function showSystemMessages(messages) {
  if (!messages) return;
  infoTextArea.innerHTML = JSON.stringify(context, null, 4);
  for (let i = 0; i < messages.length; i++) {
      if (messages[i]['type'] == "text") {
    	  showSystemMessageText(messages[i]['payload']['text']);
      }
  }
  document.getElementById("target_div").innerHTML =
    "System replied. Waiting for user input.";
}

// ---------------------------------------------------------------------------------------
// Show text message
// ---------------------------------------------------------------------------------------
function showSystemMessageText(text) {
  console.log("showSystemMessages: " + text);
  let well = $(
    '<table class="message"><tr><td><img src="img/Rivadm.png" class="profile_picture_left"></td>' +
      '<td><div class="arrow-left"></div></td>' +
      '<td><div class="well well_system"><div class="clearfix"><span> ' +
      text +
      "</span></div></div></td>" +
      '<td class="empty_space"></td></tr></table>'
  );
  var currentTime = getTimeSting();
  let welll = $(
    '<div class="balon2 p-2 m-0 position-relative" data-is="Riva - ' + currentTime + '">' +
      '<a class="float-left sohbet2">' +
      text +
      "</a></div>"
  );
  setTimeout(function () {
	$("#communication_area").append(welll.fadeIn("medium"));
	// scroll to bottom of page
	setTimeout(function () {
	  var elem = document.getElementById('communication_area');
	  elem.scrollTop = elem.scrollHeight;
	}, 10);
  }, 1000);
}

//---------------------------------------------------------------------------------------
//Show system error messages
//---------------------------------------------------------------------------------------
function showSystemErrorMessage(errorsource, errorThrown) {
	let infoTextAreaText = errorThrown;
	let text = error_systemerrormessages_info[errorsource]["text"];
  let targetDivText = error_systemerrormessages_info[errorsource]["targetDivText"];
	
	infoTextArea.innerHTML = infoTextAreaText;
	console.log("showSystemMessages: " + text);
	let well = $(
	 '<table class="message"><tr><td><img src="img/Rivadm.png" class="profile_picture_left"></td>' +
	   '<td><div class="arrow-left"></div></td>' +
	   '<td><div class="well well_system"><div class="clearfix"><span> ' +
	   text +
	   "</span></div></div></td>" +
	   '<td class="empty_space"></td></tr></table>'
	);
	var currentTime = getTimeSting();
	let welll = $(
	 '<div class="balon2 p-2 m-0 position-relative" data-is="Riva - ' + currentTime + '">' +
	   '<a class="float-left sohbet2">' +
	   text +
	   "</a></div>"
	);
	setTimeout(function () {
		$("#communication_area").append(welll.fadeIn("medium"));
		// scroll to bottom of page
		setTimeout(function () {
		  var elem = document.getElementById('communication_area');
		  elem.scrollTop = elem.scrollHeight;
		}, 10);
	}, 1000);
	
	document.getElementById("target_div").innerHTML = targetDivText;
}


// ---------------------------------------------------------------------------------------
// Shows message of user
// ---------------------------------------------------------------------------------------
function showUserMessage(text) {
  // escape html tags
  text = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
  // show it on page
  let well = $(
    '<table class="message message_user"><tr><td class="empty_space"></td>' +
      '<td><div class="well"><div class="clearfix"><span> ' +
      text +
      "</span></div></div></td>" +
      '<td><div class="arrow-right"></div></td>' +
      '<td><img src="img/User.png" class="profile_picture_right"></td></tr></table>'
  );
  var currentTime = getTimeSting();
  let welll = $(
    '<div class="balon1 p-2 m-0 position-relative" data-is="You - ' + currentTime + '"><a class="float-right">' +
      text +
      "</a></div>"
  );
  setTimeout(function () {
	$("#communication_area").append(welll);
	// scroll to bottom of page
	setTimeout(function () {
	  var elem = document.getElementById('communication_area');
	  elem.scrollTop = elem.scrollHeight;
	}, 10);
  }, 100);

  document.getElementById("target_div").innerHTML =
    "User responded. Waiting for system output.";
}

function getBrowser() {
	if(navigator.userAgent.indexOf("Chrome") != -1 ) {
		browser = 'Chrome';
    }
    else if(navigator.userAgent.indexOf("Safari") != -1) {
    	browser = 'Safari';
    }
    else if(navigator.userAgent.indexOf("Firefox") != -1 ) {
    	browser = 'Firefox';
    }
}

// ---------------------------------------------------------------------------------------
// Gets parameter by name
// ---------------------------------------------------------------------------------------
function getParameterByName(name, url) {
  let arr = url.split("#");
  let match = RegExp("[?&]" + name + "=([^&]*)").exec(arr[0]);
  return match && decodeURIComponent(match[1].replace(/\+/g, " "));
}

// ---------------------------------------------------------------------------------------
// Get endpoint of RivaDM from URL parameters
// ---------------------------------------------------------------------------------------
function getEndpoint() {
  // Get endpoint from URL
  let endpoint = getParameterByName("e", window.location.href);
  // Use default, if no endpoint is present
  if (endpoint == null) {
    endpoint = window.location.protocol + "//" + window.location.host + "/";
  }
  return endpoint;
}

// ---------------------------------------------------------------------------------------
// Get bot from URL parameters
// ---------------------------------------------------------------------------------------
function getBot() {
  // Get endpoint from URL
  let bot = getParameterByName("bot", window.location.href);
  if (bot == null || bot == "") {
    bot = window.location.pathname;
    bot = bot.replace(/\//g, "");
  }
  //Use default, if no endpoint is present
  if (bot == null) {
    bot = "";
  }
  return bot;
}

// ---------------------------------------------------------------------------------------
// Hack to have same size of input field and submit button
// ---------------------------------------------------------------------------------------
function inputFieldSizeHack() {
  const height = $("#submit_span").outerHeight();
  $("#submit").outerHeight(height);
  $("#input_field").outerHeight(height);
}

// ---------------------------------------------------------------------------------------
// Function to listen to events from ASR Output stream
// ---------------------------------------------------------------------------------------
function listenASR() {
  let eventSource = new EventSource("/stream/"+user_conversation_index);

  eventSource.addEventListener(
    "intermediate-transcript",
    function (e) {
      document.getElementById("input_field").value = e.data;
    },
    false
  );

  eventSource.addEventListener(
    "finished-speaking",
    function (e) {
      document.getElementById("input_field").value = e.data;
      if (document.getElementById("autosubmitcheck").checked == true) {
    	document.getElementById("submit").click();
      }
    },
    false
  );
}


// ---------------------------------------------------------------------------------------
// Function called right after the page is loaded
// ---------------------------------------------------------------------------------------
$(document).ready(function () {
  getBrowser();
  // input field size hack
  inputFieldSizeHack();
  $("#input_field").show();
  $("#submit").show();
  infoTextArea = document.getElementById("info-text");
  disableUserInput();
  // Get endpoint from URL address
  endpoint = getEndpoint(); // eg. "https://10.110.20.130:8009/"
  bot = getBot(); // "rivaWeather"
  get_new_user_conversation_index();
});


// ---------------------------------------------------------------------------------------
// Click on submit button
// ---------------------------------------------------------------------------------------
$(document).on("submit", "#form", function (e) {
  // Prevent reload of page after submitting of form
  e.preventDefault();
  let text = $("#input_field").val();
  console.log("text: " + text);
  if (text != "") {
    // Erase input field
    $("#input_field").val("");
    // Show user's input immediately
    showUserMessage(text);
    // Send user's input to RivaDM
    sendInput(text);
  }
});
