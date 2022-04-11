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

var nlpProto = 'src/riva_proto/riva_nlp.proto';
var protoRoot = __dirname + '/protos/';
var grpc = require('grpc');
var protoLoader = require('@grpc/proto-loader');
const { request } = require('express');
var protoOptions = {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
    includeDirs: [protoRoot]
};
var nlpPkgDef = protoLoader.loadSync(nlpProto, protoOptions);

var rNLP = grpc.loadPackageDefinition(nlpPkgDef).nvidia.riva.nlp;
var nlpClient = new rNLP.RivaLanguageUnderstanding(process.env.RIVA_API_URL, grpc.credentials.createInsecure());

var supported_entities = process.env.RIVA_NER_ENTITIES.split(',');

// Find the longest common subsequence that begins at the start of the mention,
// since the NER tagger may produce unintended non-contiguous spans
findMentionMatch = function(text, start, mention) {
	var comparisons = []; // 2D Array; longest common subsequence ending at this i-j index
	var maxSubStrLength = 0;
	var lastMaxSubStrIndex = -1;
    var i, j, char1, char2, startIndex;

	for (i = start; i < text.length; ++i) {
		comparisons[i] = new Array();

		for (j = 0; j < mention.length; ++j) {
			char1 = text.charAt(i);
			char2 = mention.charAt(j);

			if (char1 === char2) {
				if (i > start && j > 0) {
					comparisons[i][j] = comparisons[i - 1][j - 1] + 1;
				} else {
					comparisons[i][j] = 1;
				}
			} else {
				comparisons[i][j] = 0;
			}

            // We only keep track of the matches that begin at char 0 of mention
			if (comparisons[i][j] > maxSubStrLength && comparisons[i][j] === j + 1) {
				maxSubStrLength = comparisons[i][j];
				lastMaxSubStrIndex = i;
			}
		}
	}

	if (maxSubStrLength > 0) {
		startIndex = lastMaxSubStrIndex - maxSubStrLength + 1;
		return {substr: text.substr(startIndex, maxSubStrLength), start: startIndex};
	}

	return null;
}

// Compute the entity spans from NER results on the text
// Spans are only the first instance of the token
// Start/end character spans from the Riva API are forthcoming in a later release
function computeSpans(text, results) {
    var spans = [];
    var searchStart = 0;
    var match, prefix;

    results.forEach(mention => {
        match = findMentionMatch(text.toLowerCase(), searchStart, mention.token);
        if (match == null) {
            return;
        }
        prefix = match.substr.trim();
        searchStart = match.start + prefix.length;
        spans.push({'start': match.start, 'end': searchStart, 'type': mention.label[0].class_name.toLowerCase()})
    });
    return spans;
};

function getRivaNer(text) {
    // Submit a Riva NER request
    var entities;
    req = {
        text: [text],
        model: {
            model_name: process.env.RIVA_NER_MODEL
        }
    };

    return new Promise(function(resolve, reject) {
        nlpClient.ClassifyTokens(req, function(err, resp_ner) {
            if (err) {
                console.log('[Riva NLU] Error during NLU request (riva_ner): ' + err);
                reject(err);
            } else {
                entities = computeSpans(text, resp_ner.results[0].results);
                if (entities.length > 0) {
                    console.log('[Riva NLU] NER response results');
                    console.log(entities);
                }
                resolve({ner: entities, ents: supported_entities});
            }
        });
    });
};

module.exports = {getRivaNer};