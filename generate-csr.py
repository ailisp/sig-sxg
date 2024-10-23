from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.bindings._rust import x509 as rust_x509
import argparse
import requests
import base64

def generate_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
def write_key_to_file(key, filename):
    with open(filename, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
        ))

def load_key_from_file(filename, password=b"passphrase"):
    with open(filename, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=password,
        )

def generate_csr_raw(country, state, city, organization, common_name, dns_names):
    return x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, city),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(name) for name in dns_names]),
        critical=False,
    ).add_extension(
        x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), # TLS
        critical=False,
    ).add_extension(
        x509.UnrecognizedExtension(x509.ObjectIdentifier("1.3.6.1.4.1.11129.2.1.22"), b"\x04\x00"), # CanSignHttpExchanges
        critical=False,
    )

def sign_csr_raw(csr_builder, key):
    return csr_builder.sign(key, hashes.SHA256())

def sign_csr_raw2(csr_builder, key):
    b = csr_builder.build_raw(key.public_key())
    return rust_x509.sign_x509_csr_raw(b, key, hashes.SHA256(), None)

def generate_csr(key, country, state, city, organization, common_name, dns_names):
    csr_builder = generate_csr_raw(country, state, city, organization, common_name, dns_names)
    return sign_csr_raw(csr_builder, key)

def generate_csr2(key, country, state, city, organization, common_name, dns_names):
    csr_builder = generate_csr_raw(country, state, city, organization, common_name, dns_names)
    return sign_csr_raw2(csr_builder, key)

def write_csr_to_file(csr, filename):
    with open(filename, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

def main():
    parser = argparse.ArgumentParser(description='Generate a CSR with custom attributes.')
    parser.add_argument('--country', required=True, help='Country Name (2 letter code)')
    parser.add_argument('--state', required=True, help='State or Province Name')
    parser.add_argument('--city', required=True, help='Locality Name')
    parser.add_argument('--organization', required=True, help='Organization Name')
    parser.add_argument('--common-name', required=True, help='Common Name')
    parser.add_argument('--dns', type=lambda s: [x.strip() for x in s.split(',')], required=True, help='DNS Names (comma-separated list)')
    
    args = parser.parse_args()

    # key = generate_key()
    # write_key_to_file(key, "./key.pem")
    key = load_key_from_file("./key.pem")
    # csr = generate_csr(key, args.country, args.state, args.city, args.organization, args.common_name, args.dns)
    # csr2 = generate_csr2(key, args.country, args.state, args.city, args.organization, args.common_name, args.dns)
    # write_csr_to_file(csr2, "./csr2.pem")
    # write_csr_to_file(csr, "./csr.pem")

    csr_raw = generate_csr_raw(args.country, args.state, args.city, args.organization, args.common_name, args.dns).build_raw(key.public_key())
    sig = key.sign(csr_raw, padding.PKCS1v15(), hashes.SHA256())
    # Above is a mock, real would be to POST to http://localhost:3001/sign
    # requests.post("http://localhost:3001/sign", json={"path": "sxg", "account": "alice.near", "payload": base64.b64encode(sha256(csr_raw))})
    csr3 = rust_x509.pack_x509(csr_raw, sig)
    write_csr_to_file(csr3, "./csr3.pem")


if __name__ == "__main__":
    main()

# Example CLI call:
# python generate-csr.py --country US --state California --city "San Francisco" --organization "My Company" --common-name mysite.com --dns mysite.com,www.mysite.com,subdomain.mysite.com