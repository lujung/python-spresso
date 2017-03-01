function arrayBufferToString(buf) {
    return String.fromCharCode.apply(null, new Uint8Array(buf));
}


function stringToArrayBuffer(str) {
    var buf = new ArrayBuffer(str.length);
    var bufView = new Uint8Array(buf);
    for (var i = 0, strLen = str.length; i < strLen; i++) {
        bufView[i] = str.charCodeAt(i);
    }
    return buf;
}


function base64ToArrayBuffer(base64) {
    return stringToArrayBuffer(atob(base64));
}
{% if settings.debug %}
// GCM is important: we need authenticated encryption here!
{% endif %}
var algorithm = {name: 'AES-GCM', length: 256};

var hash_values = window.location.hash.substring(1).split('&');
var tag = decodeURIComponent(hash_values[0]);
var eia = decodeURIComponent(hash_values[1]);


function onReceiveTagKey(event) {
    if (event.source != window.parent.opener) {
        throw "received key from window which is not the opener of the login dialog";
    }
    var tag_key_ab = base64ToArrayBuffer(event.data);

    function importKey() {
        return crypto.subtle.importKey('raw', tag_key_ab, algorithm, false, ['decrypt']);
    }


    function decryptTag(tag_key) {
        var tag_json = JSON.parse(tag);
        return crypto.subtle.decrypt({
            name: algorithm.name,
            iv: base64ToArrayBuffer(tag_json.iv)
        }, tag_key, base64ToArrayBuffer(tag_json.ciphertext));
    }


    function sendEIA(tag_ab) {
        var tag_decrypted = JSON.parse(arrayBufferToString(tag_ab));

        var rp_origin = tag_decrypted.rp_origin;

        var padding_index = rp_origin.indexOf("=");
        if (padding_index >= 0) rp_origin = rp_origin.substr(0, padding_index);

        if (rp_origin != event.origin) {
            throw "received tag_key from origin that does not match the origin contained in the tag"
        }

        window.parent.opener.postMessage(eia, event.origin);
    }

    importKey()
        .then(decryptTag, function (x) {
            console.log("Error importing key!", x, ':', x.name);
        })
        .then(sendEIA, function (x) {
            console.log("Error decrypting tag!", x, ':', x.name);
        });
}

window.addEventListener('message', onReceiveTagKey);
if (window.parent.opener != null) window.parent.opener.postMessage('ready-send-tag-key', '*');
