SERVICE_NAME=regulonlabs-api.service
SERVICE_PATH=/etc/systemd/system/$(SERVICE_NAME)

DOMAINS=regulonlabs.com regulonlab.com

.PHONY: all help update systemd-install systemd-restart systemd-logs systemd-uninstall \
        nginx-install nginx-restart nginx-reload nginx-uninstall nginx-test ssl-issue

.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "Makefile Targets:"
	@echo "  systemd-install     Install and start systemd service"
	@echo "  systemd-restart     Restart the systemd service"
	@echo "  systemd-logs        Show logs from systemd"
	@echo "  systemd-uninstall   Remove the systemd service"
	@echo "  nginx-install       Install nginx conf for all domains"
	@echo "  nginx-reload        Reload nginx config"
	@echo "  nginx-uninstall     Remove nginx conf for all domains"
	@echo "  nginx-test          Test nginx config"
	@echo "  ssl-issue           Issue SSL certs for all domains"
	@echo "  update              Install + restart systemd + nginx for both domains"
	@echo ""

# --- SYSTEMD ---
systemd-install:
	@echo "Installing systemd service..."
	sudo cp $(SERVICE_NAME) $(SERVICE_PATH)
	sudo systemctl daemon-reload
	sudo systemctl enable $(SERVICE_NAME)
	sudo systemctl start $(SERVICE_NAME)
	@echo "Installed and started systemd service"

systemd-restart:
	sudo systemctl restart $(SERVICE_NAME)
	@echo "Restarted systemd service"

systemd-logs:
	sudo journalctl -u $(SERVICE_NAME) --no-pager --since "10m ago"

systemd-uninstall:
	sudo systemctl stop $(SERVICE_NAME)
	sudo systemctl disable $(SERVICE_NAME)
	sudo rm -f $(SERVICE_PATH)
	sudo systemctl daemon-reload
	@echo "Uninstalled systemd service"

# --- NGINX ---
nginx-install:
	@echo "Installing nginx config for all domains..."
	@for domain in $(DOMAINS); do \
		echo "→ Installing $$domain"; \
		sudo cp $$domain.nginx /etc/nginx/sites-available/$$domain; \
		sudo ln -sf /etc/nginx/sites-available/$$domain /etc/nginx/sites-enabled/$$domain; \
	done
	sudo nginx -t
	sudo systemctl reload nginx
	@echo "Installed and reloaded nginx configs"

nginx-restart:
	sudo systemctl restart nginx
	@echo "Restarted nginx"

nginx-reload:
	sudo nginx -t
	sudo systemctl reload nginx
	@echo "Reloaded nginx config"

nginx-test:
	sudo nginx -t

nginx-uninstall:
	@echo "Removing nginx configs..."
	@for domain in $(DOMAINS); do \
		echo "→ Removing $$domain"; \
		sudo rm -f /etc/nginx/sites-available/$$domain /etc/nginx/sites-enabled/$$domain; \
	done
	sudo systemctl reload nginx
	@echo "Removed nginx configs and reloaded"

ssl-issue:
	@for domain in $(DOMAINS); do \
		echo "→ Issuing SSL certificate for $$domain"; \
		sudo certbot --nginx -d $$domain --redirect --agree-tos --no-eff-email -m you@example.com; \
	done
	@echo "Issued SSL certs for: $(DOMAINS)"

# --- COMBINED ---
update: systemd-install systemd-restart nginx-install
	@echo "Fully updated systemd and nginx configs for all domains"