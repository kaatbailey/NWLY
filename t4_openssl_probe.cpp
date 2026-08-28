// T4 pre-flight: OpenSSL API-era probe for GridMate SecureSocketDriver.cpp
//
// Reproduces every OpenSSL call site in
//   dev/Code/Framework/GridMate/GridMate/Carrier/SecureSocketDriver.cpp
// (fork commit 413ecaf24d7a534801cac64f50272fe3191d278f)
//
// PREDICTION: compiles with 0 errors and exactly 3 deprecation warnings
//   DTLSv1_2_method (dep. 1.1.0), ERR_load_BIO_strings, ERR_load_SSL_strings (dep. 3.0)
// Any *error* means the local OpenSSL is a different API era than the source
// assumes, and step 5 needs a shim or an openssl-1.1 compat package.
//
// Verified PASS against OpenSSL 3.0.13.
//
//   clang++ -std=c++14 -c t4_openssl_probe.cpp -o /dev/null
//   clang++ -std=c++14 t4_openssl_probe.cpp -o probe -lssl -lcrypto && ./probe
//
#include <openssl/ssl.h>
#include <openssl/bio.h>
#include <openssl/err.h>
#include <openssl/x509.h>
#include <openssl/hmac.h>
#include <openssl/rand.h>
#include <cstdio>

static void info_cb(const SSL* s, int where, int ret) {
    int w = where & ~SSL_ST_MASK;
    const char* str = "undefined";
    if (w & SSL_ST_CONNECT) str = "SSL_connect()";
    else if (w & SSL_ST_ACCEPT) str = "SSL_accept()";
    if (where & SSL_CB_LOOP) {}
    if (where & SSL_CB_ALERT) {
        SSL_alert_type_string_long(ret);
        SSL_alert_desc_string_long(ret);
    }
    if (where & (SSL_CB_READ | SSL_CB_EXIT)) {}
    printf("%s %s\n", str, SSL_state_string_long(s));
}

int main() {
    SSL_library_init();
    ERR_load_crypto_strings();
    ERR_load_BIO_strings();
    ERR_load_SSL_strings();
    SSL_load_error_strings();

    SSL_CTX* ctx = SSL_CTX_new(DTLSv1_2_method());
    SSL_CTX_set_options(ctx, SSL_OP_NO_QUERY_MTU);
    SSL_CTX_set_info_callback(ctx, &info_cb);
    SSL_CTX_set_cipher_list(ctx, "ECDHE-RSA-AES256-GCM-SHA384");
    SSL_CTX_set_ecdh_auto(ctx, 1);
    SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, nullptr);
    SSL_CTX_set_ex_data(ctx, 0, nullptr);
    X509_STORE* store = SSL_CTX_get_cert_store(ctx);
    (void)store;

    BIO* b = BIO_new(BIO_s_mem());
    BIO_set_mem_eof_return(b, -1);
    BUF_MEM* bptr = nullptr;
    BIO_get_mem_ptr(b, &bptr);
    BIO_pending(b);
    BIO_puts(b, "x");
    X509* cert = PEM_read_bio_X509(b, nullptr, nullptr, nullptr);
    EVP_PKEY* key = PEM_read_bio_PrivateKey(b, nullptr, nullptr, nullptr);
    if (cert) { X509_get_serialNumber(cert); X509_get_issuer_name(cert);
                X509_get0_notBefore(cert); X509_get0_notAfter(cert); X509_free(cert); }
    if (key) EVP_PKEY_free(key);

    SSL* ssl = SSL_new(ctx);
    SSL_set_bio(ssl, b, b);
    SSL_set_mtu(ssl, 1400);
    unsigned char buf[EVP_MAX_MD_SIZE];
    SSL_get_finished(ssl, buf, sizeof buf);
    DTLSv1_handle_timeout(ssl);
    struct timeval tv{0,0};
    BIO_ctrl(b, BIO_CTRL_DGRAM_SET_NEXT_TIMEOUT, 0, &tv);
    RAND_bytes(buf, 16);
    unsigned int mdlen = 0;
    HMAC(EVP_sha1(), "k", 1, buf, 16, buf, &mdlen);
    printf("%d %d %d %d\n", DTLS1_VERSION, DTLS1_2_VERSION,
           DTLS1_RT_HEADER_LENGTH, DTLS1_HM_HEADER_LENGTH);
    printf("%d %d\n", SSL3_MT_CLIENT_HELLO, DTLS1_MT_HELLO_VERIFY_REQUEST);
    SSL_free(ssl); SSL_CTX_free(ctx);
    return 0;
}
