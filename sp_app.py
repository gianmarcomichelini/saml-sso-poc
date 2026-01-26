import os
import shutil
from flask import Flask, redirect, request, session
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from saml2 import xmldsig

app = Flask(__name__)
app.secret_key = "PERMANENT_SECRET_KEY_FOR_POC"

XMLSEC_PATH = shutil.which("xmlsec1")

sp_settings = {
    "xmlsec_binary": XMLSEC_PATH,
    "entityid": "http://localhost:8000/metadata",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [
                    ("http://localhost:8000/acs", BINDING_HTTP_POST)
                ],
            },
            "authn_requests_signed": False,
            "want_assertions_signed": True,
            "allow_unsolicited": True,
            "signing_algorithm": xmldsig.SIG_RSA_SHA256,
            "digest_algorithm": xmldsig.DIGEST_SHA256,
        },
    },
    "key_file": "certs/sp.key",
    "cert_file": "certs/sp.crt",
    "metadata": {"local": ["idp_metadata.xml"]},
}

def get_saml_client():
    conf = Saml2Config()
    conf.load(sp_settings)
    return Saml2Client(config=conf)

@app.route("/")
def index():
    return '<a href="/login">Login with SSO</a>'

@app.route("/login")
def login():
    client = get_saml_client()
    req_id, info = client.prepare_for_authenticate()
    session['request_id'] = req_id
    redirect_url = dict(info['headers'])['Location']
    return redirect(redirect_url)

@app.route("/acs", methods=['POST'])
def acs():
    client = get_saml_client()
    try:
        authn_response = client.parse_authn_request_response(
            request.form['SAMLResponse'], BINDING_HTTP_POST
        )
        if authn_response.in_response_to != session.get('request_id'):
             return "Security Error: Unsolicited Response", 400
        return f"Logged in as: {authn_response.get_identity()['uid'][0]}"
    except Exception as e:
        return f"SAML Error: {str(e)}", 403

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)