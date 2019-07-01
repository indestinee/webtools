openssl genrsa -out ./certificate/server-key.pem 1024
openssl req -new -out ./certificate/server-req.csr -key certificate/server-key.pem
openssl x509 -req -in ./certificate/server-req.csr -out ./certificate/server-cert.pem -signkey ./certificate/server-key.pem -days 3650
