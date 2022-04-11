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

require('dotenv').config({path: 'env.txt'});

const socketIo = require('socket.io');
const path = require('path');
const fs = require('fs');
const https = require('https');
const cors = require('cors');
const express = require('express');
const session = require('express-session')({
    secret: "gVkYp3s6",
    resave: true,
    saveUninitialized: true,
    genid: function(req) {
        return uuid.v4();
    }
});
const uuid = require('uuid');
// const ss = require('socket.io-stream');
const { ExpressPeerServer } = require('peer');
const sharedsession = require("express-socket.io-session");

const ASRPipe = require('./modules/asr');
const nlp = require('./modules/nlp');

const app = express();
const port = ( process.env.PORT );
var server, peerServer;
var sslkey = './certificates/key.pem';
var sslcert = './certificates/cert.pem';

/**
 * Set up Express Server with CORS and SocketIO
 */
function setupServer() {
    // set up Express
    app.use(cors());
    app.use(express.static('web')); // ./web is the public dir for js, css, etc.
    app.use(session);
    app.get('/', function(req, res) {
         res.sendFile('./web/index.html', { root: __dirname });
    });
    server = https.createServer({
        key: fs.readFileSync(sslkey),
        cert: fs.readFileSync(sslcert)
    }, app);

    // start peer-js server at https://ip:port/peerjs
    // for negotiating peer-to-peer connections for the video chat
    peerServer = ExpressPeerServer(server, {
        port: process.env.PEERJS_PORT,
        sslkey: sslkey,
        sslcert: sslcert
    });
    app.use('/peerjs', peerServer);

    io = socketIo(server);
    io.use(sharedsession(session, {autoSave:true}));
    server.listen(port, () => {
        console.log('Running server on port %s', port);
    });

    // Listener, once the client connects to the server socket
    io.on('connect', (socket) => {
        console.log('Client connected from %s', socket.handshake.address);

        // Initialize Riva
        console.log('Initializing Riva ASR');
        socket.handshake.session.asr = new ASRPipe();
        socket.handshake.session.asr.setupASR();
        socket.handshake.session.asr.mainASR(function(result){
            var nlpResult;
            if (result.transcript == undefined) {
                return;
            }
            // Log the transcript to console, overwriting non-final results
            process.stdout.write(''.padEnd(process.stdout.columns, ' ') + '\r')
            if (!result.is_final) {
                process.stdout.write('TRANSCRIPT: ' + result.transcript + '\r');
            } else {
                process.stdout.write('TRANSCRIPT: ' + result.transcript + '\n');
            }
            socket.handshake.session.lastLineLength = result.transcript.length;

            // Final transcripts also get sent to NLP before returning
            if (result.is_final) {
                nlp.getRivaNer(result.transcript)
                .then(function(nerResult) {
                    result.annotations = nerResult;
                    socket.emit('transcript', result);
                }, function(error) {
                    result.annotations = {err: error};
                    socket.emit('transcript', result);
                });
            } else {
                socket.emit('transcript', result);
            }
        });

        // incoming audio
        socket.on('audio_in', (data) => {
            socket.handshake.session.asr.recognizeStream.write({audio_content: data});
        });

        // NLP-only request
        socket.on('nlp_request', (data) => {
            nlp.getRivaNer(data.text)
            .then(function(nerResult) {
                socket.emit('transcript', {
                    transcript: data.text,
                    is_final: true,
                    annotations: nerResult,
                    latencyIndex: data.latencyIndex
                });
            }, function(error) {
                socket.emit('transcript', {transcript: data.text, annotations: {err: error}, latencyIndex: data.latencyIndex});
            });
        });

        // Get the list of supported entities
        socket.on('get_supported_entities', () => {
            socket.emit('supported_entities', process.env.RIVA_NER_ENTITIES);
        });

        socket.on('peerjs_id', (peerjs_id) => {
            socket.handshake.session.peerjs_id = peerjs_id;
            console.log('Client at %s has PeerJS ID %s', socket.handshake.address, peerjs_id);
        });

        socket.on('disconnect', (reason) => {
            console.log('Client at %s disconnected. Reason: ', socket.handshake.address, reason);
        });
    });
};

setupServer();