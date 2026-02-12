# SAML 2.0 Web Browser SSO - Proof of Concept

> A cybersecurity student implementation demonstrating **Delegated Authentication** using the SAML 2.0 Web Browser SSO Profile

---

## Overview

This project implements the **SAML 2.0 Web Browser SSO Profile** using Python, Flask, and `pysaml2`, orchestrated with Docker. It demonstrates the **Push Model** where the Identity Provider "pushes" authentication assertions to the Service Provider.

Built as part of the "Electronic Identity" lecture of the "Advanced Information Systems Security" course at University Polytechnic of Turin, this PoC provides a hands-on understanding of modern federated authentication mechanisms.

---

## Key Concepts

### Delegated Authentication
The Service Provider (SP) delegates user authentication to a trusted Identity Provider (IdP) rather than handling credentials directly.

### Web Browser SSO Profile
A standardized pattern for sharing authentication assertions across domains using standard web browsers.

### SAML Bindings
- **HTTP-Redirect Binding** - SP sends `AuthnRequest` to IdP via URL parameters
- **HTTP-POST Binding** - IdP returns `SAMLResponse` to SP via HTML form submission

### Trust Relationship
Established through X.509 certificate exchange and metadata, ensuring message authenticity (and integrity) and non-repudiation.

---

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│             │         │                  │         │                 │
│   Browser   │────────▶│ Service Provider │────────▶│ Identity Provider│
│  (Client)   │         │   (Port 8000)    │         │   (Port 9000)   │
│             │◀────────│  Relying Party   │◀────────│  Auth Server    │
└─────────────┘         └──────────────────┘         └─────────────────┘
```

### The SSO Flow (Push Model)

1. **Initial Access** - User attempts to access protected resource on SP
2. **Redirect** - SP generates `AuthnRequest` and redirects browser to IdP (HTTP 302)
3. **Authentication** - IdP authenticates user and generates signed assertion
4. **Push Response** - IdP auto-submits HTML form containing assertion back to SP (HTTP POST)
5. **Validation** - SP verifies signature, validates assertion, and establishes session

---

## Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed
- Git for cloning the repository

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/saml-sso-poc.git
cd saml-sso-poc
```

**2. Generate X.509 certificates**

```bash
mkdir -p certs

# Generate Service Provider keys
openssl req -newkey rsa:3072 -new -x509 -days 365 -nodes \
  -out certs/sp.crt -keyout certs/sp.key \
  -subj "/CN=localhost"

# Generate Identity Provider keys
openssl req -newkey rsa:3072 -new -x509 -days 365 -nodes \
  -out certs/idp.crt -keyout certs/idp.key \
  -subj "/CN=localhost"
```

**3. Build Docker images**

```bash
docker-compose build
```

**4. Generate SAML metadata**

```bash
docker-compose run --rm sp python create_metadata.py
```

**5. Start the services**

```bash
docker-compose up
```

### Testing the Flow

1. Navigate to `http://localhost:8000` in your browser
2. Click **Login with SSO**
3. Observe the redirect to `http://localhost:9000` (IdP)
4. Watch the automatic POST submission back to the SP
5. See the success message: `Logged in as: student_user`

---

## Security Features

This implementation includes security controls aligned with SAML 2.0 best practices:

| Feature | Implementation |
|---------|---------------|
| **Digital Signatures** | RSA-SHA256 signatures on all assertions |
| **Signature Verification** | SP validates IdP signatures using trusted certificates |
| **Authentication Statements** | Explicit `AuthnStatement` with timestamp and method |
| **Replay Protection** | `InResponseTo` validation ensures request-response binding |
| **Modern Cryptography** | Enforces SHA-256, rejects deprecated SHA-1 |
| **Certificate Trust** | Mutual trust via X.509 certificate exchange |

---

## Educational Context

This project was developed as part of a cybersecurity curriculum to demonstrate:

- Federated identity management principles
- SAML 2.0 protocol mechanics
- Trust establishment in distributed systems
- Secure authentication delegation patterns
- XML signature verification
