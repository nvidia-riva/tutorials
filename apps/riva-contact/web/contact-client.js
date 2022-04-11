/**
 * Copyright 2020 NVIDIA Corporation. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const id = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
const socketio = io();
const resampleWorker = './resampler.js';

var peer;
var peer_id;
var username = 'User ' + id.toString();
var peer_username;
var peerConn;
var peerCall;
var localStream;
var peerStream;
var audioContext;
var sampleRate;
var rivaRunning = false;
var callActive = false;
var muted = false;
var videoEnabled = true;
var socket = socketio.on('connect', function() {
    console.log('Socket connected to speech server');
});

var scrollToBottomTime = 500;
var displacy;
var ents;
var latencyTimer;
// var reconnectAttempts = 0;
// var reconnectTimerId;

// ---------------------------------------------------------------------------------------
// Latency tracking
// ---------------------------------------------------------------------------------------
class LatencyTimer {
    constructor() {
        this.startTimes = new Array();
        this.latencies = new Array();
    }

    start(data=null) {
        return this.startTimes.push({start: performance.now(), data: data}) - 1;
    }

    end(index) {
        if (index >= this.startTimes.length) {
            return 0;
        }
        var latency = Math.round(performance.now() - this.startTimes[index].start);
        this.latencies.push(latency);
        return {latency: latency, data: this.startTimes[index].data};
    }

    average() {
        const sum = this.latencies.reduce((a, b) => a + b, 0);
        return Math.round((sum / this.latencies.length) || 0);
    }
}

function setPeerUsername(peerName) {
    peer_username = peerName;
    document.getElementById("peer_cam_label").innerHTML = peer_username;
}

// ---------------------------------------------------------------------------------------
// Start Riva, whether triggered locally or by a message from peer
// ---------------------------------------------------------------------------------------
function startRivaService() {
    if (rivaRunning) {
        return;
    }
    document.getElementById('riva-btn').disabled = true;
    latencyTimer = new LatencyTimer();

    if (socket == null) {
        socket = socketio.on('connect', function() {
            console.log('Connected to speech server');
        });    
    } else {
        socket.disconnect();
        socket.connect();
        console.log('Reconnected to speech server');
    }
    
    // Start ASR streaming
    let audioInput = audio_context.createMediaStreamSource(localStream);
    let bufferSize = 4096;
    let recorder = audio_context.createScriptProcessor(bufferSize, 1, 1);
    let worker = new Worker(resampleWorker);
    worker.postMessage({
	    command: 'init',
	    config: {
            sampleRate: sampleRate,
            outputSampleRate: 16000
	    }
    });
    
    // Use a worker thread to resample the audio, then send to server
    recorder.onaudioprocess =  function(audioProcessingEvent) {
        let inputBuffer = audioProcessingEvent.inputBuffer;
        worker.postMessage({
            command: 'convert',
            // We only need the first channel
            buffer: inputBuffer.getChannelData(0)
        });
        worker.onmessage = function(msg) {
            if (msg.data.command == 'newBuffer') {
                socket.emit('audio_in', msg.data.resampled.buffer);
            }
        };
    };

    // connect stream to our recorder
    audioInput.connect(recorder);
    // connect our recorder to the previous destination
    recorder.connect(audio_context.destination);
    rivaRunning = true;

    console.log('Streaming audio to server')

    // Transcription results streaming back from Riva
    socket.on('transcript', function(result) {
        if (result.transcript == undefined) {
            return;
        }
        document.getElementById('input_field').value = result.transcript;
        if (result.is_final) {
            // Erase input field
            $('#input_field').val('');
            // Render the transcript locally
            // TODO: check for error in result.annotations
            showAnnotatedTranscript(username, result.annotations, result.transcript);
            // Send the transcript to the peer to render
            if (peerConn != undefined && callActive) {
                peerConn.send({from: username, type: 'transcript', annotations: result.annotations, text: result.transcript});
            }
            if (result.latencyIndex !== undefined) {
                var latencyResult = latencyTimer.end(result.latencyIndex);
                console.log(latencyResult.data.name + ': ' + latencyResult.latency.toString() + ' ms');
                console.log('Average latency (overall): ' + latencyTimer.average().toString() + ' ms');
            }
        }
    });

    document.getElementById('submit_text').removeAttribute('disabled');
    document.getElementById('input_field').setAttribute('placeholder', 'Enter some text to annotate, or start speaking');
    var connArea = document.getElementById('connection_status');
    toastr.success('Riva is connected.');

    socket.emit('get_supported_entities');
    socket.on('supported_entities', function(response) {
        var entityHeader, entityDiv, ner;
        ents = response.split(',');
        console.log('Supported entities: ' + response);
        // Render a legend from the entity list
        entityHeader = document.createElement('div');
        entityHeader.innerHTML = '<p class=\"mb-1\">Entities being tagged:</p>';
        connArea.appendChild(entityHeader);
        entityDiv = document.createElement('div');
        ner = ents.map(function(type){ 
            return {'start': 0, 'end': 0, 'type': type};
        });
        displacy.render(entityDiv, '', ner, ents);
        connArea.append(entityDiv);
    });
}

// ---------------------------------------------------------------------------------------
// Shows NLP-annotated transcript
// ---------------------------------------------------------------------------------------
function showAnnotatedTranscript(speaker, annotations, text) {

    if(!annotations)
        return;

    var nameContainer = document.createElement('div');
    var textContainer = document.createElement('div');
    if (speaker == username) {
        nameContainer.setAttribute('class', 'd-flex justify-content-end');
        textContainer.setAttribute('class', 'row justify-content-end mx-0');
    }

    nameContainer.innerHTML = "<p class=\"text-info mb-0 mt-1\"><small><strong>" + speaker + ":</strong></small></p>";
    displacy.render(textContainer, text, annotations.ner, annotations.ents);

    $("#transcription_area").append(nameContainer);
    $("#transcription_area").append(textContainer);
    $("#transcription_card").animate({scrollTop: 100000}, scrollToBottomTime);
    // Scroll the full page to the bottom?
    // $("html, body").animate({scrollTop: $(document).height()}, scrollToBottomTime);
}

/**
 * Starts the request of the camera and microphone
 *
 * @param {Object} callbacks
 */
function requestLocalVideo(callbacks) {
   // Monkeypatch for crossbrowser getUserMedia
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

    // Request audio and video
    // Try getting video, if it fails then go for audio only
    navigator.getUserMedia({ audio: true, video: true }, callbacks.success, 
        function() { // error -- can't access video. Try audio only
            navigator.getUserMedia({ audio: true}, callbacks.success ,callbacks.error);
        }
    );
}

/**
 * Attach the provided stream (video and audio) to the desired video element
 *
 * @param {*} stream
 * @param {*} element_id
 */
function onReceiveStream(stream, element_id) {
    // Retrieve the video element
    var video = document.getElementById(element_id);
    // Set the given stream as the video source
    video.srcObject = stream;
}

function clearStream(element_id) {
    var video = document.getElementById(element_id);
    video.pause();
    video.srcObject = new MediaStream(); // replace the video element with an empty stream
    video.load();
}

/**
 * Receive messages from the peer
 *
 * @param {Object} data
 */
function handleMessage(data) {
    console.log("Message: " + data);

    switch(data.type) {
        case 'startRiva':
            startRivaService();
            break;
        case 'transcript':
            if (data.from != peer_username) {
                setPeerUsername(data.from);
            }
            showAnnotatedTranscript(data.from, data.annotations, data.text);
            break;
        case 'username':
            setPeerUsername(data.from);
            break;
        default:
            console.log('Received unknown message from peer, of type ' + data.type);
    }
}

function setCallHandlers() {
    peerCall.on('stream', function(stream) {
        peerStream = stream;
        if (!callActive) {
            toastr.success('Call connected.');
        }
        callActive = true;
        // Display the stream of the other user in the peer-camera video element
        onReceiveStream(stream, 'peer-camera');
    });

    peerCall.on('error', function(error) { // TODO: improve peerjs error handling
        bootbox.alert(error);
        console.log(error);
    });
}

function setDataConnHandlers() {
    // Use the handleMessage to callback when a message comes in
    peerConn.on('data', handleMessage);

    // Handle when the call finishes
    peerConn.on('close', function() {
        toastr.info('Call with ' + peer_username + ' has ended.');
        console.log('Peer data connection ended');
        callActive = false;
        clearStream('peer-camera');
        $("#call").html('Call');
    });
}

// ---------------------------------------------------------------------------------------
// When the document is ready
// ---------------------------------------------------------------------------------------
$(document).ready(function () {
    // Activate tooltips
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });

    // Start DisplaCy for the NER rendering
    displacy = new displaCyENT('http://localhost:8000', {})

    /**
     * The iceServers on this example are public and can be used for a demo project.
     * They are intended for low-volume use; please do not abuse them.
     * They also may be discontinued without notice.
     */
    peer = new Peer(id, {
        host: document.domain,
        port: location.port,
        path: '/peerjs',
        debug: 3,
        secure: true,
        config: {
            'iceServers': [
                { url: 'stun:stun1.l.google.com:19302' },
                {
                    url: 'turn:numb.viagenie.ca',
                    credential: 'NVDemo',
                    username: 'cparisien@nvidia.com'
                }
            ]
        }
    });

    // Once the initialization succeeds:
    // Show the ID that allows other user to connect to your session.
    peer.on('open', function() {
        document.getElementById("your_id").innerHTML = "Your ID: <strong>" + peer.id + "</strong>";

        // Report my own ID to the server
        if (socket) {
            socket.emit('peerjs_id', peer.id);
        }
    });

    peer.on('connection', function(connection) {
        peerConn = connection;
        peer_id = connection.peer;
        setPeerUsername(peerConn.metadata.username);
        console.log("Received connection request from " + peer_username);
        setDataConnHandlers();
    });

    peer.on('error', function(err){
        bootbox.alert(err.message);
        console.error(err.message);
    });

    /**
     * Handle the on receive call event
     */
    peer.on('call', function(call) {
        bootbox.confirm("Incoming video call. Accept?", function(acceptsCall) {
            if(acceptsCall) {
                // Answer the call with your own video/audio stream
                peerCall = call;
                peerCall.answer(localStream);
                $("#call").html('End');
                setCallHandlers();
                startRivaService();
            } else {
                console.log("Call denied !");
            }
        });
    });

    /**
     * Request browser audio and video, and show the local stream
     */
    requestLocalVideo({
        success: function(stream){
            localStream = stream;
            audio_context = new AudioContext();
            sampleRate = audio_context.sampleRate;
            console.log("Sample rate of local audio: " + sampleRate)

            onReceiveStream(stream, 'my-camera');
        },
        error: function(err){
            bootbox.alert("Cannot get access to your camera and microphone.");
            console.error(err);
        }
    });

    // Allow us to launch Riva with only the local speaker
    document.getElementById('riva-btn').removeAttribute("disabled");

});

// ---------------------------------------------------------------------------------------
// Click on user name button
// ---------------------------------------------------------------------------------------
$(document).on("click", "#name_btn", function (e) {
    // Prevent reload of page after submitting of form
    e.preventDefault();
    username = $('#name').val();
    console.log("username: " + username);
    document.getElementById("self_cam_label").innerHTML = username;
    if (peerConn != undefined) {
        peerConn.send({from: username, type: 'username'});
    }
});

function startCall() {
    // Connect with the user
    peer_id = document.getElementById("peer_id").value;
    if (!peer_id) {
        return false;
    }

    peerConn = peer.connect(peer_id, {
        metadata: {
            'username': username
        }
    });
    setDataConnHandlers();
    
    // Call the peer
    console.log('Calling peer ' + peer_id);
    peerCall = peer.call(peer_id, localStream);
    $("#call").html('End');
    setCallHandlers();
    setPeerUsername('User ' + peer_id.toString());
    startRivaService();
}

function endCall() {
    callActive = false;

    // Close the media and data connections with the peer
    peerCall.close();
    peerConn.close();

    // $('#peer_id').val("");
    $("#call").html('Call'); // set the call button back
}

// ---------------------------------------------------------------------------------------
// Request a video call with another user
// ---------------------------------------------------------------------------------------
$(document).on("click", "#call", function (e) {
    // Prevent reload of page after submitting of form
    e.preventDefault();

    if (!callActive) {
        startCall();
    } else {
        endCall();
    }
});

// ---------------------------------------------------------------------------------------
// On clicking the Transcription button, start Riva
// ---------------------------------------------------------------------------------------
$(document).on("click", "#riva-btn", function (e) {
    // Send message to peer to also connect to Riva, then start my own connection
    if (peerConn != undefined) {
        peerConn.send({from: username, type: 'startRiva'});
    }
    startRivaService();
});

function setAudioEnabled(enabled) {
    if (!localStream) return;
    for (const track of localStream.getAudioTracks()) {
        track.enabled = enabled;
    }
}

function setVideoEnabled(enabled) {
    if (!localStream) return;
    for (const track of localStream.getVideoTracks()) {
        track.enabled = enabled;
    }
}

// ---------------------------------------------------------------------------------------
// On mute button, which should mute both call audio and Riva ASR
// ---------------------------------------------------------------------------------------
$(document).on("click", "#mute-btn", function (e) {
    if (!muted) {
        if($(this).hasClass("btn-primary")) {
            $("#mute-btn").removeClass("btn-primary").addClass("btn-secondary");
            $("#mute-btn").tooltip('hide')
                .attr('data-original-title', 'Unmute')
                .tooltip('show');         
        }
        setAudioEnabled(false);
        muted = true;
    } else {
        if($(this).hasClass("btn-secondary")) {
            $("#mute-btn").removeClass("btn-secondary").addClass("btn-primary");               
            $("#mute-btn").tooltip('hide')
                .attr('data-original-title', 'Mute')
                .tooltip('show');         
        }
        setAudioEnabled(true);
        muted = false;
    }
});

// ---------------------------------------------------------------------------------------
// On mute button, which should mute both call audio and Riva ASR
// ---------------------------------------------------------------------------------------
$(document).on("click", "#video-btn", function (e) {
    if (videoEnabled) {
        if($(this).hasClass("btn-primary")) {
            $("#video-btn").removeClass("btn-primary").addClass("btn-secondary");
            $("#video-btn").tooltip('hide')
                .attr('data-original-title', 'Video on')
                .tooltip('show');         
        }
        setVideoEnabled(false);
        videoEnabled = false;
    } else {
        if($(this).hasClass("btn-secondary")) {
            $("#video-btn").removeClass("btn-secondary").addClass("btn-primary");               
            $("#video-btn").tooltip('hide')
                .attr('data-original-title', 'Video off')
                .tooltip('show');         
        }
        setVideoEnabled(true);
        videoEnabled = true;
    }
});

// ---------------------------------------------------------------------------------------
// Click on text submit button
// ---------------------------------------------------------------------------------------
$(document).on("submit", "#input_form", function (e) {
    // Prevent reload of page after submitting of form
    e.preventDefault();
    let text = $('#input_field').val();
    console.log("text: " + text);

    socket.emit('nlp_request', {
        text: text,
        latencyIndex: latencyTimer.start({name: 'NLP request'})
    });
    // Erase input field
    $('#input_field').val("");
});
