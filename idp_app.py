import os
import shutil
import base64
from flask import Flask, request, render_template_string
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.server import Server
from saml2.config import Config as Saml2Config
from saml2 import xmldsig

app = Flask(__name__)

XMLSEC_PATH = shutil.which("xmlsec1")

idp_settings = {
    "xmlsec_binary": XMLSEC_PATH,
    "entityid": "http://localhost:9000/idp/metadata",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": [
                    ("http://localhost:9000/sso", BINDING_HTTP_REDIRECT),
                ],
            },
            "name_id_format": ["urn:oasis:names:tc:SAML:2.0:nameid-format:transient"],
            "want_authn_requests_signed": False,
            "signing_algorithm": xmldsig.SIG_RSA_SHA256,
            "digest_algorithm": xmldsig.DIGEST_SHA256,
        },
    },
    "key_file": "certs/idp.key",
    "cert_file": "certs/idp.crt",
    "metadata": {"local": ["sp_metadata.xml"]},
}

def get_idp_server():
    conf = Saml2Config()
    conf.load(idp_settings)
    return Server(config=conf)

@app.route("/sso")
def sso():
    server = get_idp_server()
    saml_request = request.args.get('SAMLRequest')
    if not saml_request:
        return "Error: No SAMLRequest found", 400

    req_info = server.parse_authn_request(saml_request, BINDING_HTTP_REDIRECT)
    identity = {"uid": "student_user", "email": "student@polito.it"}

    authn_statement = {
        "class_ref": "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
        "authn_auth": "http://www.w3.org/2000/09/xmldsig#rsa-sha256",
    }

    saml_response = server.create_authn_response(
        identity, userid="student_user",
        in_response_to=req_info.message.id,
        destination="http://localhost:8000/acs",
        sp_entity_id="http://localhost:8000/metadata",
        name_id_policy=req_info.message.name_id_policy,
        sign_response=True,
        sign_assertion=True,
        authn=authn_statement
    )

    saml_response_b64 = base64.b64encode(str(saml_response).encode('utf-8')).decode('utf-8')
    
    return render_template_string('''
        <body onload="document.forms[0].submit()">
            <form method="POST" action="http://localhost:8000/acs">
                <input type="hidden" name="SAMLResponse" value="{{ response }}">
                <noscript><input type="submit" value="Continue"></noscript>
            </form>
        </body>
    ''', response=saml_response_b64)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000, debug=True)