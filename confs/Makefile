install:
 cp nginx.conf /etc/nginx/conf.d/api.conf
 cp api.service /etc/systemd/system/api.service
 cp edgedb.service /etc/systemd/system/edgedb.service
 cp keycloak.service /etc/systemd/system/keycloak.service
 systemctl daemon-reload
 systemctl enable --now api.service edgedb.service keycloak.service
