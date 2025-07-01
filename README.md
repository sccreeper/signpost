# Signpost

A self-hosted URL redirect service written using Flask and HTMX.

## Installation and running

Clone the repository (`git clone https://github.com/sccreeper/signpost.git`).

It is designed to be run in a Docker container (`./docker_run.sh`), and the following environment variables will have to be set:

- `SECRET` - Secret to be used for Flask session management. 
- `RATE_LIMIT` - How many requests per second to allow. Will obtain Cloudflare IP address if [`CF-Connecting-IP`](https://developers.cloudflare.com/fundamentals/reference/http-headers/#cf-connecting-ip) header is present.
- `HOST` - Host the website is running on, i.e. `example.com`. Used for generating QR codes.

The admin page can then be accessed at `localhost:8080/admin/login`. The default password is `password`. 

## License 

MIT