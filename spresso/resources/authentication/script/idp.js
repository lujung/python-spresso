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


function arrayBufferToBase64(arrayBuffer) {
    return btoa(arrayBufferToString(arrayBuffer));
}

var algorithm = {name: 'AES-GCM', length: 256};
var hash_values = window.location.hash.substring(1).split('&');
var tag = decodeURIComponent(hash_values[0]);
var email = decodeURIComponent(hash_values[1]);
var ia_key = decodeURIComponent(hash_values[2]);
var forwarder_domain = decodeURIComponent(hash_values[3]);
var forwarder_path = "{{ settings.endpoints_ext.get('proxy').path }}";
var sign_path = "{{ settings.endpoints.get('sign').path }}";
var logged_in_as = "{{ email|e }}";

function createProxyIframe(encrypted_ia_json) {
    var tag_param = encodeURIComponent(tag);
    var eia_param = encodeURIComponent(encrypted_ia_json);
    var url = "{{ settings.scheme }}" + '://' + forwarder_domain + forwarder_path + "#" + tag_param + "&" + eia_param;

    var ifrm = document.createElement("IFRAME");
    ifrm.setAttribute("src", url);
    {% if settings.debug %}
    ifrm.style.width = 320 + "px";
    ifrm.style.height = 200 + "px";
    {% else %}
    ifrm.style.display = "none";
    {% endif %}

    document.body.appendChild(ifrm);

    {% if settings.sri %}
    ifrm.integrity = "{{ settings.sri_hash }}";
    {% endif %}

    {% if settings.debug %}
    console.log("LD finished.");
    {% endif %}
}


function encryptIdentityAssertion(ia_json) {
    var ia_key_arrayBuffer = base64ToArrayBuffer(ia_key);
    var iv;


    function importKey() {
        return crypto.subtle.importKey("raw", ia_key_arrayBuffer, algorithm, false, ['encrypt']);
    }


    function encryptIA(ia_key_handle) {
        iv = new Int8Array(12);
        crypto.getRandomValues(iv);
        return crypto.subtle.encrypt({
            name: algorithm.name,
            iv: iv
        }, ia_key_handle, stringToArrayBuffer(ia_json));
    }


    function sendEIAToProxy(encrypted_ia_arrayBuffer) {
        var encrypted_ia_json = JSON.stringify({
            'ciphertext': arrayBufferToBase64(encrypted_ia_arrayBuffer),
            'iv': arrayBufferToBase64(iv)
        });
        createProxyIframe(encrypted_ia_json);
    }

    importKey()
        .then(encryptIA, function (x) {
            console.log("Error importing key!", x);
        })
        .then(sendEIAToProxy, function (x) {
            console.log("Error encrypting IA!", x);
        });
}

function loginFailed(response) {}

function getIdentityAssertion() {
    {% if settings.debug %}
    console.log("LD started.");
    {% endif %}
    var password = document.getElementById("password").value;
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
        if (this.status != 200) {
            document.getElementById('loginform').style.display = 'initial';
            document.getElementById('password').focus();
            return loginFailed(this);
        }
        encryptIdentityAssertion(this.responseText);
    };
    xhr.open("POST", sign_path, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var password_param = encodeURIComponent(password);
    var tag_param = encodeURIComponent(tag);
    var email_param = encodeURIComponent(email);
    xhr.send("password=" + password_param + "&email=" + email_param + "&tag=" + tag_param +
        "&forwarder_domain=" + forwarder_domain);
}


window.onload = function () {
    // Set email address in form field, only for cosmetical reasons.
    document.getElementById('email').appendChild(
        document.createTextNode(email)
    );
    if (email === logged_in_as) {
        // User has session from previous login
        getIdentityAssertion();
        return;
    }
    document.getElementById('loginform').style.display = 'initial';
    document.getElementById('password').focus();
};