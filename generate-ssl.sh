#!/bin/bash
# ============================================================
# SSL Certificate Generator for Local Network
# ============================================================
# Usage: ./generate-ssl.sh [type]
# Types: self-signed (default) | local-ca | mdns
# ============================================================

set -e

CERT_DIR="certs"
SERVER_IP="192.168.171.184"
HOSTNAME=$(hostname)

echo "============================================================"
echo "🔒 SSL Certificate Generator"
echo "============================================================"

# Create certs directory
mkdir -p "$CERT_DIR"

# Function: Generate Self-Signed Certificate
generate_self_signed() {
    echo ""
    echo "📝 Generating Self-Signed Certificate..."
    echo "   IP: $SERVER_IP"
    echo "   Hostname: $HOSTNAME"
    
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout "$CERT_DIR/key.pem" \
        -out "$CERT_DIR/cert.pem" \
        -days 365 \
        -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/OU=IT Department/CN=$SERVER_IP" \
        -addext "subjectAltName=IP:$SERVER_IP,DNS:$HOSTNAME.local,DNS:localhost"
    
    chmod 600 "$CERT_DIR/key.pem"
    chmod 644 "$CERT_DIR/cert.pem"
    
    echo "✅ Self-signed certificate generated!"
    echo ""
    echo "📁 Files created:"
    echo "   - $CERT_DIR/cert.pem (public certificate)"
    echo "   - $CERT_DIR/key.pem (private key)"
    echo ""
    echo "⚠️  Browser will show warning - click 'Advanced' → 'Proceed'"
    echo ""
    echo "📝 To remove browser warning, install cert.pem on client devices:"
    echo "   Windows: Import to 'Trusted Root Certification Authorities'"
    echo "   Mac: Import to Keychain → Always Trust"
    echo "   Linux: sudo cp $CERT_DIR/cert.pem /usr/local/share/ca-certificates/flask-face.crt && sudo update-ca-certificates"
}

# Function: Generate Local CA
generate_local_ca() {
    echo ""
    echo "📝 Generating Local Certificate Authority..."
    
    # Create CA directory
    mkdir -p "$CERT_DIR/ca"
    
    # Generate CA
    echo "   Step 1/4: Creating CA private key..."
    openssl genrsa -out "$CERT_DIR/ca/ca-key.pem" 4096
    
    echo "   Step 2/4: Creating CA certificate..."
    openssl req -new -x509 -days 3650 \
        -key "$CERT_DIR/ca/ca-key.pem" \
        -out "$CERT_DIR/ca/ca-cert.pem" \
        -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/OU=Certificate Authority/CN=FlaskFace Root CA"
    
    # Generate server key
    echo "   Step 3/4: Creating server private key..."
    openssl genrsa -out "$CERT_DIR/key.pem" 4096
    
    # Create CSR
    openssl req -new -key "$CERT_DIR/key.pem" \
        -out "$CERT_DIR/server.csr" \
        -subj "/C=ID/ST=Jakarta/L=Jakarta/O=FlaskFace/OU=Web Server/CN=$SERVER_IP"
    
    # Create SAN config
    cat > "$CERT_DIR/server.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = $SERVER_IP
DNS.1 = $HOSTNAME.local
DNS.2 = flask-face.local
DNS.3 = localhost
EOF
    
    # Sign certificate
    echo "   Step 4/4: Signing certificate with CA..."
    openssl x509 -req -in "$CERT_DIR/server.csr" \
        -CA "$CERT_DIR/ca/ca-cert.pem" \
        -CAkey "$CERT_DIR/ca/ca-key.pem" \
        -CAcreateserial \
        -out "$CERT_DIR/cert.pem" \
        -days 365 \
        -extfile "$CERT_DIR/server.ext"
    
    # Cleanup
    rm "$CERT_DIR/server.csr" "$CERT_DIR/server.ext"
    
    # Set permissions
    chmod 600 "$CERT_DIR/ca/ca-key.pem"
    chmod 644 "$CERT_DIR/ca/ca-cert.pem"
    chmod 600 "$CERT_DIR/key.pem"
    chmod 644 "$CERT_DIR/cert.pem"
    
    echo "✅ Local CA and server certificate generated!"
    echo ""
    echo "📁 Files created:"
    echo "   CA Files:"
    echo "   - $CERT_DIR/ca/ca-cert.pem (CA certificate - INSTALL THIS!)"
    echo "   - $CERT_DIR/ca/ca-key.pem (CA private key - KEEP SECURE!)"
    echo "   Server Files:"
    echo "   - $CERT_DIR/cert.pem (server certificate)"
    echo "   - $CERT_DIR/key.pem (server private key)"
    echo ""
    echo "🔑 IMPORTANT: Install CA certificate on ALL client devices:"
    echo "   Windows: Import ca-cert.pem to 'Trusted Root Certification Authorities'"
    echo "   Mac: Import ca-cert.pem to Keychain → Always Trust"
    echo "   Linux: sudo cp $CERT_DIR/ca/ca-cert.pem /usr/local/share/ca-certificates/flask-face-ca.crt && sudo update-ca-certificates"
    echo ""
    echo "✅ After installing CA, no browser warnings for any certificate signed by this CA!"
}

# Function: Setup mDNS
setup_mdns() {
    echo ""
    echo "📝 Setting up mDNS (.local domain)..."
    
    # Check if avahi is installed
    if ! command -v avahi-daemon &> /dev/null; then
        echo "   Installing Avahi (mDNS)..."
        sudo apt-get update -qq
        sudo apt-get install -y avahi-daemon
    fi
    
    # Enable and start avahi
    sudo systemctl enable avahi-daemon
    sudo systemctl start avahi-daemon
    
    # Generate certificate with .local domain
    echo "   Generating certificate for $HOSTNAME.local..."
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout "$CERT_DIR/key.pem" \
        -out "$CERT_DIR/cert.pem" \
        -days 365 \
        -subj "/CN=$HOSTNAME.local" \
        -addext "subjectAltName=DNS:$HOSTNAME.local,DNS:flask-face.local,IP:$SERVER_IP"
    
    chmod 600 "$CERT_DIR/key.pem"
    chmod 644 "$CERT_DIR/cert.pem"
    
    echo "✅ mDNS certificate generated!"
    echo ""
    echo "📁 Files created:"
    echo "   - $CERT_DIR/cert.pem"
    echo "   - $CERT_DIR/key.pem"
    echo ""
    echo "🌐 Access via:"
    echo "   https://$HOSTNAME.local"
    echo "   https://flask-face.local"
    echo "   https://$SERVER_IP"
    echo ""
    echo "⚠️  Browser will still show warning (install cert.pem to remove)"
}

# Function: Verify certificate
verify_certificate() {
    echo ""
    echo "🔍 Certificate Information:"
    echo "============================================================"
    openssl x509 -in "$CERT_DIR/cert.pem" -text -noout | grep -A 2 "Subject:"
    openssl x509 -in "$CERT_DIR/cert.pem" -text -noout | grep -A 1 "Validity"
    openssl x509 -in "$CERT_DIR/cert.pem" -text -noout | grep -A 3 "Subject Alternative Name"
    echo "============================================================"
    echo ""
    echo "📊 Certificate Details:"
    echo "   Issuer: $(openssl x509 -in "$CERT_DIR/cert.pem" -noout -issuer | cut -d= -f2-)"
    echo "   Valid until: $(openssl x509 -in "$CERT_DIR/cert.pem" -noout -enddate | cut -d= -f2)"
    echo "   Key size: $(openssl x509 -in "$CERT_DIR/cert.pem" -noout -text | grep "Public-Key:" | sed 's/.*(\([0-9]*\) bit).*/\1/')-bit RSA"
    echo ""
}

# Main
TYPE="${1:-self-signed}"

case "$TYPE" in
    self-signed|self)
        generate_self_signed
        ;;
    local-ca|ca)
        generate_local_ca
        ;;
    mdns)
        setup_mdns
        ;;
    *)
        echo "❌ Invalid type: $TYPE"
        echo ""
        echo "Usage: $0 [type]"
        echo ""
        echo "Available types:"
        echo "  self-signed  - Quick self-signed certificate (default)"
        echo "  local-ca     - Local Certificate Authority (more secure)"
        echo "  mdns         - Setup mDNS with .local domain"
        echo ""
        exit 1
        ;;
esac

# Verify
verify_certificate

# Next steps
echo "📝 Next Steps:"
echo ""
echo "1. Enable HTTPS in Docker:"
echo "   Edit docker-compose.app.yml:"
echo "   - Uncomment: - \"192.168.171.184:443:443\""
echo "   - Uncomment: - ./certs:/app/certs:ro"
echo ""
echo "2. Rebuild Flask app:"
echo "   docker-compose -f docker-compose.app.yml up -d --build"
echo ""
echo "3. Test HTTPS:"
echo "   curl -k https://$SERVER_IP"
echo "   Open browser: https://$SERVER_IP"
echo ""
echo "4. (Optional) Remove browser warning:"
echo "   Install $CERT_DIR/cert.pem on client devices"
echo "   (or $CERT_DIR/ca/ca-cert.pem for Local CA)"
echo ""
echo "============================================================"
echo "✅ SSL Certificate Setup Complete!"
echo "============================================================"
