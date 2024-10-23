# SIG-SXG
This is a proof of concept project that implements Signed Exchanges (SXG) built on Sig Network. This project is still work in progress

## Workflow

## Workflow

1. Run one of mock signer or sig signer:
   - For mock signer: `node mock-signer.js`
   - For sig signer: `node sig-signer.js`

2. Generate CSR:
   ```
   python generate-csr.py
   ```
   This generates a CSR without signature, sends it to the signer to sign and pack the signed CSR, then dumps it in PEM format.

3. Register a DigiCert account and upload the CSR to obtain a SXG-supported certificate.

4. Host the certificate and public key on a server:
   - Ensure your server is configured to serve these files securely.

5. Generate SXG for each static file on your site:
   ```
   python generate-sxg.py
   ```
   (TODO)

6. Host SXG files alongside your site:
   - Configure your web server to serve both the original files and their SXG counterparts.


## Installation Steps

To set up the environment for this project, follow these steps:

1. Clone the repository and its submodules:
   ```
   git clone --recursive https://github.com/your-repo/SIG-SXG.git
   cd SIG-SXG
   ```

2. Install Conda
   If you don't have Conda installed, download and install it from the [official Conda website](https://docs.conda.io/en/latest/miniconda.html).

3. Create a new Conda environment named 'nearsxg':
   ```
   conda env create -f environment.yml
   conda activate nearsxg
   ```

4. Install project dependencies:
   ```
   npm install
   ```

5. Build the cryptography module:
   ```
   cd cryptography
   ```

6. Install Rust:
   If you don't have Rust installed, you can install it using rustup. Visit https://rustup.rs/ for installation instructions or run:
   ```
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

7. Install build requirements:
   ```
   pip install -r .github/requirements/build-requirements.txt
   ```

8. Build the cryptography module using maturin:
   ```
   maturin build
   # There will be an output python package, install it with pip install path/to/package
   ```

9. Return to the project root directory:
   ```
   cd ..
   ```

10. Build the webpackage:
    ```
    cd webpackage
    go build -o ../gen-signedexchange go/signedexchange/cmd/gen-signedexchange/main.go
    cd ..
    ```


