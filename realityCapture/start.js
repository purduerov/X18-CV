/////////////////////////////////////////////////////////////////////
// Copyright (c) Autodesk, Inc. All rights reserved
//
// Permission to use, copy, modify, and distribute this software in
// object code form for any purpose and without fee is hereby granted,
// provided that the above copyright notice appears in all copies and
// that both that copyright notice and the limited warranty and
// restricted rights notice below appear in all supporting
// documentation.
//
// AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS.
// AUTODESK SPECIFICALLY DISCLAIMS ANY IMPLIED WARRANTY OF
// MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.  AUTODESK, INC.
// DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
// UNINTERRUPTED OR ERROR FREE.
/////////////////////////////////////////////////////////////////////

//-------------------------------------------------------------------
// These packages are included in package.json.
// Run `npm install` to install them.
// 'path' is part of Node.js and thus not inside package.json.
//-------------------------------------------------------------------
var express = require('express');           // For web server
var Axios = require('axios');               // A Promised base http client
var bodyParser = require('body-parser');    // Receive JSON format
var https = require('https');               // For HTTPS requests
var fs = require('fs');                     // File system operations
var path = require('path');                 // Path utilities

// Configure axios to handle SSL certificate issues in development
var httpsAgent = new https.Agent({
    rejectUnauthorized: false
});
// Note: Don't set globally for axios 0.18.0, use per-request instead

// Set up Express web server
var app = express();
app.use(bodyParser.json());
app.use(express.static(__dirname + '/www'));
app.use('/photos', express.static(__dirname + '/photos')); // Serve photos folder

// This is for web server to start listening to port 3000
app.set('port', 3000);
var server = app.listen(app.get('port'), function () {
    console.log('Server listening on port ' + server.address().port);
});

//-------------------------------------------------------------------
// Configuration for your Forge account
// Initialize the 2-legged OAuth2 client, and
// set specific scopes
//-------------------------------------------------------------------
var FORGE_CLIENT_ID = 'x7eTsOPqR5SyhWEX7AhjrdPJn66D4TxKn3yKqSPz6uH9rtGj';
var FORGE_CLIENT_SECRET = 'SznYHKjfbXJG016ZpVV7FztSohW8iVHizoZpxgACLl1Dt2DtUad7TWgKQyG4UAOx';
var access_token = '';
var scopes = 'data:read data:write';
const querystring = require('querystring');

//-------------------------------------------------------------------
// PHOTO CONFIGURATION
//-------------------------------------------------------------------
// Option 1: Set your own photo URLs here (must be publicly accessible)
// Example: var CUSTOM_PHOTO_URLS = ['https://example.com/photo1.jpg', 'https://example.com/photo2.jpg'];
// CUSTOM_PHOTO_URLS must be direct image URLs (not gallery pages)
// For Imgur: Use format https://i.imgur.com/IMAGE_ID.jpg (not https://imgur.com/IMAGE_ID)
// IMPORTANT: Forge Photo-to-3D API ONLY accepts JPG/JPEG format, NOT PNG!
// The URLs must return raw image data with Content-Type: image/jpeg, not HTML pages

let dynamicPhotoUrls = [];

app.post('/api/photos', function (req, res) {
    const url = req.body.url;

    if (!url) {
        return res.status(400).send({ error: "No URL provided" });
    }

    dynamicPhotoUrls.push(url);
    console.log("Received URL:", url);

    res.send({ success: true });
});
/*
var CUSTOM_PHOTO_URLS = [
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373103.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373125.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373128.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373129.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373130.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373131.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373132.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373134.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373135.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373139.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373144.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373150.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373154.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775373089/capture_1775373179.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375134.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375139.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375141.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375149.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375155.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375159.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375163.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375165.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375167.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375173.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375177.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375181.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375127/capture_1775375196.jpg',
    'https://3d-reconstruction-cv.s3.us-east-2.amazonaws.com/runs/run_1775375215/capture_1775375275.jpg'
]; // Set to null to use local photos or sample photos
*/
// Option 2: Use ngrok for local photos
// The code will try to auto-detect ngrok URL, or you can set it manually:
// var NGROK_URL = 'https://abc123.ngrok.io';
var NGROK_URL = null; // Will be auto-detected if ngrok is running

// Imgur API - Required for automated workflow (photos folder -> Imgur -> Reality Capture)
// Get your Client ID at: https://api.imgur.com/oauth2/addclient (choose "Anonymous usage")
var IMGUR_CLIENT_ID = process.env.IMGUR_CLIENT_ID || null; // Set in env or here

// Function to auto-detect ngrok URL
function getNgrokUrl() {
    try {
        var http = require('http');
        var url = require('url');
        var ngrokApiUrl = 'http://127.0.0.1:4040/api/tunnels';
        var parsed = url.parse(ngrokApiUrl);
        var options = {
            hostname: parsed.hostname,
            port: parsed.port,
            path: parsed.path,
            method: 'GET',
            timeout: 1000
        };
        
        // Try to get ngrok URL synchronously (with a simple timeout)
        // Note: This is a simplified version - in production you'd want async
        return null; // Will be set dynamically in the upload route
    } catch (e) {
        return null;
    }
}
//-------------------------------------------------------------------

// Debug: Log if credentials are set (without showing the actual values)
console.log('FORGE_CLIENT_ID:', FORGE_CLIENT_ID ? 'Set (' + FORGE_CLIENT_ID.length + ' chars)' : 'NOT SET');
console.log('FORGE_CLIENT_SECRET:', FORGE_CLIENT_SECRET ? 'Set (' + FORGE_CLIENT_SECRET.length + ' chars)' : 'NOT SET');

// // Route /api/forge/oauth
app.get('/api/forge/oauth', function (req, res) {
    Axios({
        method: 'POST',
        url: 'https://developer.api.autodesk.com/authentication/v2/token',
        headers: {
            'content-type': 'application/x-www-form-urlencoded',
        },
        httpsAgent: httpsAgent,
        data: querystring.stringify({
            client_id: FORGE_CLIENT_ID,
            client_secret: FORGE_CLIENT_SECRET,
            grant_type: 'client_credentials',
            scope: scopes
        })
    })
        .then(function (response) {
            // Success
            access_token = response.data.access_token;
            console.log(response);
            res.send('<p>Authentication success!</p><a href="/api/forge/recap/photoscene/add">Add a photoscene</a>');
        })
        .catch(function (error) {
            // Failed
            console.log('Authentication error:', error.response ? error.response.data : error.message);
            console.log('Full error:', error);
            var errorMsg = '<h2>Failed to authenticate</h2>';
            if (!FORGE_CLIENT_ID || !FORGE_CLIENT_SECRET) {
                errorMsg += '<p>Missing FORGE_CLIENT_ID or FORGE_CLIENT_SECRET</p>';
            }
            if (error.response) {
                errorMsg += '<p>Status: ' + error.response.status + '</p>';
                if (error.response.data) {
                    errorMsg += '<pre>' + JSON.stringify(error.response.data, null, 2) + '</pre>';
                }
            } else if (error.message) {
                errorMsg += '<p>Error: ' + error.message + '</p>';
            }
            if (error.code) {
                errorMsg += '<p>Code: ' + error.code + '</p>';
            }
            res.send(errorMsg);
        });
});

// Route /api/forge/recap/photoscene/add
// Creates and initializes a photoscene for reconstruction.
app.get('/api/forge/recap/photoscene/add', function (req, res) {
    Axios({
        method: 'POST',
        url: 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene',
        headers: {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + access_token
        },
        httpsAgent: httpsAgent,
        data: querystring.stringify({
            scenename: 'myscenename',
            scenetype: 'object',
            format: 'obj'
        })
    })
        .then(function (response) {
            // Success
            console.log(response);
            if (response.data.Error) {
                res.send(response.data.Error.msg);
            }
            var photosceneId = response.data.Photoscene.photosceneid;
            var nextLink = '/api/forge/recap/photoscene/upload?photosceneid=' + photosceneId;
            res.send('<p>Photoscene added!</p><a href="' + nextLink + '">Upload files to photoscene</a>');
        })
        .catch(function (error) {
            // Failed
            console.log('Photoscene creation error:', error.response ? error.response.data : error.message);
            console.log('Full error:', error);
            var errorMsg = '<h2>Failed to create a photoscene</h2>';
            if (error.response) {
                errorMsg += '<p>Status: ' + error.response.status + '</p>';
                if (error.response.data) {
                    errorMsg += '<pre>' + JSON.stringify(error.response.data, null, 2) + '</pre>';
                }
            } else if (error.message) {
                errorMsg += '<p>Error: ' + error.message + '</p>';
            }
            res.send(errorMsg);
        });
});

//-------------------------------------------------------------------
// AUTOMATED WORKFLOW: photos folder -> convert to JPG -> Imgur -> Reality Capture
// Requires: IMGUR_CLIENT_ID (get at https://api.imgur.com/oauth2/addclient)
//-------------------------------------------------------------------
app.get('/api/automated-workflow', function (req, res) {
    var sharp;
    try {
        sharp = require('sharp');
    } catch (e) {
        return res.send('<h2>Error</h2><p>sharp package not found. Run: npm install</p>');
    }
    if (!IMGUR_CLIENT_ID) {
        return res.send('<h2>Error</h2><p>IMGUR_CLIENT_ID not set. Add it to start-server.sh or set env: export IMGUR_CLIENT_ID=your_client_id</p><p>Get one at: <a href="https://api.imgur.com/oauth2/addclient" target="_blank">https://api.imgur.com/oauth2/addclient</a></p>');
    }
    
    var photosDir = path.join(__dirname, 'photos');
    if (!fs.existsSync(photosDir)) {
        return res.send('<h2>Error</h2><p>photos folder not found. Create it and add your images.</p>');
    }
    var files = fs.readdirSync(photosDir);
    var imageExtensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'];
    var photoFiles = files.filter(function (f) {
        return imageExtensions.indexOf(path.extname(f)) !== -1;
    }).sort();
    if (photoFiles.length === 0) {
        return res.send('<h2>Error</h2><p>No images found in photos folder. Add JPG or PNG files.</p>');
    }
    
    // Step 1: Authenticate Forge
    Axios({
        method: 'POST',
        url: 'https://developer.api.autodesk.com/authentication/v2/token',
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
        httpsAgent: httpsAgent,
        data: querystring.stringify({
            client_id: FORGE_CLIENT_ID,
            client_secret: FORGE_CLIENT_SECRET,
            grant_type: 'client_credentials',
            scope: scopes
        })
    })
        .then(function (authRes) {
            access_token = authRes.data.access_token;
            console.log('[Automated] Forge authenticated');
            // Step 2: Convert to JPG and upload to Imgur
            var uploadPromises = photoFiles.map(function (file) {
                var filePath = path.join(photosDir, file);
                var ext = path.extname(file).toLowerCase();
                return sharp(fs.readFileSync(filePath))
                    .jpeg({ quality: 90 })
                    .toBuffer()
                    .then(function (jpgBuffer) {
                        var base64 = jpgBuffer.toString('base64');
                        return Axios({
                            method: 'POST',
                            url: 'https://api.imgur.com/3/image',
                            headers: {
                                'Authorization': 'Client-ID ' + IMGUR_CLIENT_ID,
                                'Content-Type': 'application/json'
                            },
                            data: { image: base64, type: 'base64' }
                        }).then(function (imgurRes) {
                            var link = imgurRes.data.data.link;
                            console.log('[Automated] Uploaded to Imgur:', link);
                            return link;
                        });
                    });
            });
            return Promise.all(uploadPromises);
        })
        .then(function (imgurUrls) {
            console.log('[Automated] All images uploaded to Imgur:', imgurUrls.length);
            // Step 3: Create photoscene
            return Axios({
                method: 'POST',
                url: 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene',
                headers: {
                    'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Bearer ' + access_token
                },
                httpsAgent: httpsAgent,
                data: querystring.stringify({
                    scenename: 'myscenename',
                    scenetype: 'object',
                    format: 'obj'
                })
            }).then(function (psRes) {
                if (psRes.data.Error) {
                    throw new Error(psRes.data.Error.msg || 'Photoscene creation failed');
                }
                return { photosceneId: psRes.data.Photoscene.photosceneid, imgurUrls: imgurUrls };
            });
        })
        .then(function (data) {
            var photosceneId = data.photosceneId;
            var uploadData = { photosceneid: photosceneId, type: 'image' };
            data.imgurUrls.forEach(function (url, i) {
                uploadData['file[' + i + ']'] = url;
            });
            // Step 4: Upload Imgur links to photoscene
            return Axios({
                method: 'POST',
                url: 'https://developer.api.autodesk.com/photo-to-3d/v1/file',
                headers: {
                    'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Bearer ' + access_token
                },
                httpsAgent: httpsAgent,
                data: querystring.stringify(uploadData)
            }).then(function (uploadRes) {
                if (uploadRes.data && uploadRes.data.Error) {
                    throw new Error(uploadRes.data.Error.msg || 'Upload failed');
                }
                return photosceneId;
            });
        })
        .then(function (photosceneId) {
            // Step 5: Start processing
            return Axios({
                method: 'POST',
                url: 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/' + photosceneId,
                headers: {
                    'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Bearer ' + access_token
                },
                httpsAgent: httpsAgent
            }).then(function () {
                return photosceneId;
            });
        })
        .then(function (photosceneId) {
            var progressLink = '/api/forge/recap/photoscene/checkprogress?photosceneid=' + photosceneId;
            var html = '<h2>Automated workflow started!</h2>';
            html += '<p>Converted ' + photoFiles.length + ' image(s) to JPG, uploaded to Imgur, created photoscene, and started 3D processing.</p>';
            html += '<p><a href="' + progressLink + '">Check progress</a></p>';
            html += '<p>Processing may take several minutes. Keep refreshing the progress page until it shows DONE.</p>';
            res.send(html);
        })
        .catch(function (err) {
            var msg = err.response && err.response.data ? JSON.stringify(err.response.data, null, 2) : err.message;
            console.log('[Automated] Error:', msg);
            res.send('<h2>Automated workflow failed</h2><pre>' + msg + '</pre>');
        });
});

// Helper route to get ngrok URL
app.get('/api/ngrok/url', function (req, res) {
    Axios.get('http://127.0.0.1:4040/api/tunnels', { httpsAgent: httpsAgent, timeout: 2000 })
        .then(function (response) {
            if (response.data && response.data.tunnels && response.data.tunnels.length > 0) {
                var ngrokUrl = response.data.tunnels[0].public_url;
                res.json({ ngrokUrl: ngrokUrl, success: true });
            } else {
                res.json({ error: 'No ngrok tunnels found', success: false });
            }
        })
        .catch(function (error) {
            res.json({ error: 'Ngrok not running or not accessible. Make sure ngrok is running on port 4040', success: false });
        });
});

app.post('/api/photos', function (req, res) {
    const url = req.body.url;

    if (!url) {
        return res.status(400).send({ error: "No URL provided" });
    }

    dynamicPhotoUrls.push(url);

    console.log(" New URL:", url);
    console.log(" Current array:", dynamicPhotoUrls);

    res.send({ success: true });
});
app.get('/api/photos', (req, res) => {
    console.log(" Fetching current URLs:", dynamicPhotoUrls);
    res.json(dynamicPhotoUrls);
});

app.post('/api/photos/reset', (req, res) => {
    dynamicPhotoUrls = [];
    console.log(" Array reset:", dynamicPhotoUrls);

    res.send({ success: true });
});



// Route /api/forge/recap/photoscene/upload
// Adds one or more files to a photoscene.
app.get('/api/forge/recap/photoscene/upload', function (req, res) {
    var photosceneId = req.query.photosceneid;
    
    // Get photos - priority: CUSTOM_PHOTO_URLS > local photos (with ngrok) > sample photos
    var photoUrls = [];
    var photoFiles = [];
    
    // Option 1: Use custom photo URLs if configured
    /*if (CUSTOM_PHOTO_URLS && CUSTOM_PHOTO_URLS.length > 0) {
        photoUrls = CUSTOM_PHOTO_URLS;
        console.log('Using ' + photoUrls.length + ' custom photo URL(s)');
    }*/
    if (dynamicPhotoUrls.length > 0) {
        photoUrls = dynamicPhotoUrls;
    } else {
        // Option 2: Check for local photos
        var photosDir = path.join(__dirname, 'photos');
        if (fs.existsSync(photosDir)) {
            var files = fs.readdirSync(photosDir);
            var imageExtensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'];
            photoFiles = files.filter(function(file) {
                var ext = path.extname(file);
                return imageExtensions.indexOf(ext) !== -1;
            }).sort();
        }
        
        if (photoFiles.length > 0) {
            // Try to get ngrok URL if not set
            var ngrokUrl = NGROK_URL;
            if (!ngrokUrl) {
                // Try to fetch from ngrok API (async, but we'll handle it)
                console.log('Attempting to auto-detect ngrok URL...');
                // For now, we'll proceed and let the user know they need to set it
                // In a production app, you'd want to make this async
            }
            
            // Use ngrok URL if available, otherwise localhost (may not work for Forge API)
            var baseUrl = ngrokUrl ? (ngrokUrl + '/photos/') : 'http://localhost:3000/photos/';
            photoUrls = photoFiles.map(function(file) {
                // URL encode the filename in case it has spaces
                return baseUrl + encodeURIComponent(file);
            });
            console.log('Using ' + photoFiles.length + ' local photo(s):', photoFiles);
            if (!ngrokUrl) {
                console.log('WARNING: Using localhost URLs. Forge API may not be able to access them.');
                console.log('Please visit http://localhost:3000/api/ngrok/url to get your ngrok URL,');
                console.log('then set NGROK_URL in start.js (around line 68)');
                console.log('Or manually set: var NGROK_URL = "https://your-ngrok-url.ngrok.io";');
            } else {
                console.log('Using ngrok URL:', ngrokUrl);
            }
        } else {
            // Option 3: Fall back to sample photos
            photoUrls = [
                'https://s3.amazonaws.com/adsk-recap-public/forge/lion/DSC_1158.JPG',
                'https://s3.amazonaws.com/adsk-recap-public/forge/lion/DSC_1159.JPG',
                'https://s3.amazonaws.com/adsk-recap-public/forge/lion/DSC_1160.JPG',
                'https://s3.amazonaws.com/adsk-recap-public/forge/lion/DSC_1162.JPG',
                'https://s3.amazonaws.com/adsk-recap-public/forge/lion/DSC_1163.JPG',
                'https://s3.amazonaws.com/adsk-recap-public/forge/lion/DSC_1164.JPG',
                'https://s3.amazonaws.com/adsk-recap-public/forge/lion/DSC_1165.JPG'
            ];
            console.log('Using sample photos (no local photos found in /photos folder)');
        }
    }
    
    // Validate photo URLs - ensure they're direct image links
    var validPhotoUrls = [];
    photoUrls.forEach(function(url, index) {
        // Check if URL looks like a direct image link (not a gallery page)
        if (url.indexOf('imgur.com/') !== -1 && url.indexOf('i.imgur.com') === -1) {
            console.log('WARNING: URL ' + (index + 1) + ' appears to be a gallery link, not a direct image link:', url);
            console.log('Convert to: https://i.imgur.com/IMAGE_ID.png or .jpg');
        }
        // Ensure URL has image extension
        var hasImageExt = /\.(jpg|jpeg|png|JPG|JPEG|PNG)(\?|$)/.test(url);
        if (!hasImageExt && url.indexOf('i.imgur.com') !== -1) {
            // Try to add .png extension for Imgur (default to PNG)
            url = url + '.png';
            console.log('Added .png extension to URL:', url);
        }
        validPhotoUrls.push(url);
    });
    
    console.log('Uploading ' + validPhotoUrls.length + ' photo(s) to photoscene:', photosceneId);
    console.log('Photo URLs:', validPhotoUrls);
    console.log('API Endpoint: https://developer.api.autodesk.com/photo-to-3d/v1/file');
    
    // Build the data object with photo URLs
    // The Forge API expects URLs (not binary data) - it will download the images itself
    var uploadData = {
        photosceneid: photosceneId,
        type: 'image'  // Type is 'image' for photo-to-3d API
    };
    validPhotoUrls.forEach(function(url, index) {
        uploadData['file[' + index + ']'] = url;
    });
    
    // Validate API endpoint and request format
    var apiEndpoint = 'https://developer.api.autodesk.com/photo-to-3d/v1/file';
    console.log('Request payload keys:', Object.keys(uploadData));
    console.log('Content-Type: application/x-www-form-urlencoded (correct for form data)');
    
    Axios({
        method: 'POST',
        url: apiEndpoint,  // Validated endpoint
        headers: {
            'content-type': 'application/x-www-form-urlencoded',  // Correct for form-encoded data
            'Authorization': 'Bearer ' + access_token
        },
        httpsAgent: httpsAgent,
        data: querystring.stringify(uploadData)  // Form-encoded string (not binary, not JSON)
    })
        .then(function (response) {
            // Check for errors in response first
            if (response.data.Error) {
                console.log('API Error:', response.data.Error);
                var errorMsg = '<h2>Failed to upload files</h2>';
                errorMsg += '<p><strong>Error Code:</strong> ' + response.data.Error.code + '</p>';
                errorMsg += '<p><strong>Error Message:</strong> ' + response.data.Error.msg + '</p>';
                
                if (response.data.Error.msg.indexOf('image/png') !== -1) {
                    errorMsg += '<p><strong>IMPORTANT:</strong> The Forge Photo-to-3D API does NOT support PNG files!</p>';
                    errorMsg += '<p>You must convert your PNG images to JPG/JPEG format.</p>';
                    errorMsg += '<p>Options:</p><ul>';
                    errorMsg += '<li>Convert PNG to JPG using an image converter</li>';
                    errorMsg += '<li>Re-upload your images as JPG to Imgur</li>';
                    errorMsg += '<li>Update CUSTOM_PHOTO_URLS with JPG image URLs</li>';
                    errorMsg += '</ul>';
                }
                return res.send(errorMsg);
            }
            
            // Success - no errors
            console.log('Upload successful!');
            console.log('Files:', JSON.stringify(response.data.Files));
            var nextLink = '/api/forge/recap/photoscene/process?photosceneid=' + photosceneId;
            res.send('<p>Files added to photoscene!</p><a href="' + nextLink + '">Begin processing photoscene</a>');
        })
        .catch(function (error) {
            // Failed
            console.log('Upload error:', error.response ? error.response.data : error.message);
            var errorMsg = '<h2>Failed to upload files to photoscene</h2>';
            if (error.response) {
                errorMsg += '<p>Status: ' + error.response.status + '</p>';
                if (error.response.data) {
                    errorMsg += '<pre>' + JSON.stringify(error.response.data, null, 2) + '</pre>';
                }
            } else if (error.message) {
                errorMsg += '<p>Error: ' + error.message + '</p>';
            }
            errorMsg += '<p><strong>Troubleshooting:</strong></p>';
            errorMsg += '<ul>';
            errorMsg += '<li>Validate API Endpoint: https://developer.api.autodesk.com/photo-to-3d/v1/file (verified)</li>';
            errorMsg += '<li>Ensure all URLs are direct image links (e.g., https://i.imgur.com/xxx.png, not https://imgur.com/xxx)</li>';
            errorMsg += '<li>URLs must return raw image data with Content-Type: image/png or image/jpeg, not HTML</li>';
            errorMsg += '<li>Request payload: Sending URLs (not binary data) - API downloads images itself</li>';
            errorMsg += '<li>Image formats: ONLY JPG/JPEG are supported - PNG is NOT supported by Forge API</li>';
            errorMsg += '<li>Verify images are publicly accessible and not behind authentication</li>';
            errorMsg += '<li>Check server console logs for detailed error information</li>';
            errorMsg += '</ul>';
            res.send(errorMsg);
        });
});

// Route /api/forge/recap/photoscene/process
// Starts photoscene processing.
app.get('/api/forge/recap/photoscene/process', function (req, res) {
    var photosceneId = req.query.photosceneid;
    Axios({
        method: 'POST',
        url: 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/' + photosceneId,
        headers: {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + access_token
        },
        httpsAgent: httpsAgent
    })
        .then(function (response) {
            // Success
            console.log(response);
            if (response.data.Error) {
                res.send(response.data.Error.msg);
            }
            var nextLink = '/api/forge/recap/photoscene/checkprogress?photosceneid=' + photosceneId;
            res.send('<p>Photoscene is being processed!</p><a href="' + nextLink + '">Check progress of photoscene</a>');
        })
        .catch(function (error) {
            // Failed
            console.log(error);
            res.send('Failed to process files in photoscene');
        });
});

// Route /api/forge/recap/photoscene/checkprogress
// Returns the processing progress and status of a photoscene.
app.get('/api/forge/recap/photoscene/checkprogress', function (req, res) {
    var photosceneId = req.query.photosceneid;
    Axios({
        method: 'GET',
        url: 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/' + photosceneId + '/progress',
        headers: {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        httpsAgent: httpsAgent
    })
        .then(function (response) {
            // Success
            console.log(response);
            if (response.data.Error) {
                res.send(response.data.Error.msg);
            }
            if (response.data.Photoscene && response.data.Photoscene.progressmsg == 'DONE') {
                var nextLink = '/api/forge/recap/photoscene/result?photosceneid=' + photosceneId;
                res.send('<p>Photoscene process is complete!</p><a href="' + nextLink + '">View result of photoscene</a>');
            } else {
                var nextLink = '/api/forge/recap/photoscene/delete?photosceneid=' + photosceneId;
                res.send('<p>Photoscene is not ready, this may take a while. Try refreshing <a href="/api/forge/recap/photoscene/checkprogress?photosceneid=' +  photosceneId + '">this page</a>. Progress: ' + response.data.Photoscene.progress + '%...</p>');
            }
            
        })
        .catch(function (error) {
            // Failed
            console.log(error);
            res.send('Failed to check progress of photoscene');
        });
});

// Route /api/forge/recap/photoscene/result
// Returns a time-limited HTTPS link to an output file of the specified format.
app.get('/api/forge/recap/photoscene/result', function (req, res) {
    var photosceneId = req.query.photosceneid;
    Axios({
        method: 'GET',
        url: 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/' + photosceneId + '?format=obj',
        headers: {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        },
        httpsAgent: httpsAgent
    })
        .then(function (response) {
            // Success
            console.log(response);
            if (response.data.Error) {
                res.send(response.data.Error.msg);
            }
            if (response.data.Photoscene && response.data.Photoscene.progressmsg == 'DONE') {
                var nextLink = '/api/forge/recap/photoscene/delete?photosceneid=' + photosceneId;
                res.send('<p>Success! This is the scene link:</p><p>' + response.data.Photoscene.scenelink + '</p>'
                    + 'Would you like to <a href="' + nextLink + '">delete photoscene</a>?');
            } else {
                res.send('Photoscene is not ready. Try refreshing <a href="/api/forge/recap/photoscene/checkprogress?photosceneid=' +  photosceneId + '">this page</a>. Progress: ' + response.data.Photoscene.progress + '%...');
            }
            
        })
        .catch(function (error) {
            // Failed
            console.log(error);
            res.send('Failed to get result of photoscene');
        });
});

// Route /api/forge/recap/photoscene/delete
// Deletes a photoscene and its associated assets (images, output files, ...).
app.get('/api/forge/recap/photoscene/delete', function (req, res) {
    var photosceneId = req.query.photosceneid;
    Axios({
        method: 'DELETE',
        url: 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene/' + photosceneId,
        headers: {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + access_token
        },
        httpsAgent: httpsAgent
    })
        .then(function (response) {
            // Success
            console.log(response);
            if (response.data.Error) {
                res.send(response.data.Error.msg);
            }
            res.send('<p>Photoscene deleted!</p>');
        })
        .catch(function (error) {
            // Failed
            console.log(error);
            res.send('Failed to delete photoscene');
        });
});
