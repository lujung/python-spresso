"use strict";

var login_dialog_redirect_url = "{{ settings.endpoints.get('redirect').path }}";
var loginDialog;
var dimensions = 'width=600, height=400';

function startLoginFailed(response) {}

function startLogin() {
    {% if settings.debug %}
    console.log('startLogin');
    {% endif %}
    loginDialog = window.open("{{ settings.endpoints.get('wait').path }}", 'loginDialog', dimensions);
    var email = document.getElementById('email_input').value;
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
        if (this.status != 200) {
            loginDialog.close();
            return startLoginFailed(this);
        }
        var response = JSON.parse(this.responseText);

        startLoginDialog(
            response.tag_key,
            response.forwarder_domain,
            response.login_session_token
        );
    };
    xhr.open("POST", "{{ settings.endpoints.get('start_login').path }}", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var email_param = encodeURIComponent(email);
    xhr.send("email=" + email_param);
}


function startLoginDialog(tag_key, forwarder_domain, login_session_token) {
    var forwarder_origin = "{{ settings.scheme }}" + '://' + forwarder_domain;

    window.addEventListener("message", onProxyIframeTagKeyRequest);
    loginDialog = window.open(
        login_dialog_redirect_url + '?login_session_token=' + encodeURIComponent(login_session_token),
        'loginDialog',
        dimensions
    );


    function onProxyIframeTagKeyRequest(event) {
        {% if settings.debug %}
        console.log('received proxy iframe ready', event);
        {% endif %}

        if (event.source != loginDialog.frames[0]) {
            throw 'received key request from window that is not the first iframe of the login dialog';
        }

        if (event.origin != forwarder_origin) {
            throw 'received key request from origin that is not the application';
        }

        if (event.data != 'ready-send-tag-key') {
            return;
        }

        {% if settings.debug %}
        console.log('send tag key to proxy iframe');
        {% endif %}
        window.removeEventListener("message", onProxyIframeTagKeyRequest);
        event.source.postMessage(tag_key, forwarder_origin);
        window.addEventListener("message", onReceiveEncryptedIdentityAssertion);


        function onReceiveEncryptedIdentityAssertion(event) {
            {% if settings.debug %}
            console.log('received encrypted identity assertion', event);
            {% endif %}

            if (event.source != loginDialog.frames[0]) {
                throw 'received encrypted identity assertion from window that is not the first iframe of the login' +
                ' dialog';
            }

            if (event.origin != forwarder_origin) {
                throw 'received encrypted identity assertion from origin that is not the application';
            }

            window.removeEventListener("message", onReceiveEncryptedIdentityAssertion, false);

            loginDialog.close();

            var eia = event.data;
            sendEIA(eia, login_session_token);
        }
    }
}

function loginSuccessful(response) {}

function loginFailed(response) {}

function sendEIA(eia, login_session_token) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function (event) {
        if (this.status != 200)  return loginFailed(this);
        loginSuccessful(this);
    };
    xhr.open("POST", "{{ settings.endpoints.get('login').path }}", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var eia_param = encodeURIComponent(eia);
    var login_session_token_param = encodeURIComponent(login_session_token);
    xhr.send("eia=" + eia_param + "&login_session_token=" + login_session_token_param);
}