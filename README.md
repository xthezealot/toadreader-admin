# Toad Reader Admin

## Dev

1. Run `./devserver.py` to start the dev server
2. Open `http://localhost:8002` in your browser

# Setup server

1. `dnf install caddy`

2. `nano /etc/caddy/Caddyfile`

    ```
    admin.demo.toadreader.com {
      request_body {
        max_size 250mb
      }

      root * /srv/toadreader-admin
      try_files {path} {path}.html {path}/index.html
      file_server
      encode
    }
    ```

3. `caddy reload`

## Deploy

1. Upload `src` files to server in `/srv/toadreader-admin`

2. On server:
   ```sh
   find /srv/toadreader-admin -type f -exec sed -i 's|http://localhost:4567|https://api.demo.toadreader.com|g' {} +
   ```
