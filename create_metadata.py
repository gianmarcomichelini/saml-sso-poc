from saml2.config import Config as Saml2Config
from saml2.metadata import entity_descriptor
from saml2 import xmldsig

def write_metadata(config_dict, filename):
    conf = Saml2Config()
    conf.load(config_dict)
    with open(filename, "w") as f:
        f.write(str(entity_descriptor(conf)))

sp_meta_config = {
    "entityid": "http://localhost:8000/metadata",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [("http://localhost:8000/acs", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST")]
            },
            "authn_requests_signed": False,
            "want_assertions_signed": True,
            "signing_algorithm": xmldsig.SIG_RSA_SHA256,
            "digest_algorithm": xmldsig.DIGEST_SHA256,
        }
    },
    "key_file": "certs/sp.key",
    "cert_file": "certs/sp.crt",
}

idp_meta_config = {
    "entityid": "http://localhost:9000/idp/metadata",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": [("http://localhost:9000/sso", "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect")]
            },
            "name_id_format": ["urn:oasis:names:tc:SAML:2.0:nameid-format:transient"],
            "want_authn_requests_signed": False,
            "signing_algorithm": xmldsig.SIG_RSA_SHA256,
            "digest_algorithm": xmldsig.DIGEST_SHA256,
        }
    },
    "key_file": "certs/idp.key",
    "cert_file": "certs/idp.crt",
}

if __name__ == "__main__":
    write_metadata(sp_meta_config, "sp_metadata.xml")
    write_metadata(idp_meta_config, "idp_metadata.xml")
    print("Metadata generated.")