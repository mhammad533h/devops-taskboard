# Viva quick answers

Use these to explain work you actually performed; do not claim an AWS deployment or successful test until you have run and captured it.

**What is the difference between an image and a container?** An image is the built, read-only application package. A container is a running instance of that image with its own writable layer and process.

**What does the Dockerfile do?** It starts from Python 3.12, installs Flask, Psycopg, and Gunicorn, copies the app, switches to a non-root user, and starts the web server on port 8080.

**What does Compose do here?** It defines the `web` and `db` services, their configuration and health checks, the internal network, and a named PostgreSQL volume. The app reaches PostgreSQL at host name `db`.

**Why does data survive `docker compose down`?** The database files live in the `pgdata` named volume, outside the container writable layer. Compose recreates containers and reattaches the volume. `down -v` would delete it.

**How do health checks work?** PostgreSQL's `pg_isready` gates the web startup. `/healthz` opens a database connection for the web health check and the ALB target group. An unhealthy target stops receiving new ALB traffic and can be replaced by the Auto Scaling group.

**What does the ALB do?** It receives HTTP requests and forwards them to healthy EC2 targets. Its DNS name is the public application URL. Cookie stickiness directs a browser to one target for 24 hours in this lab.

**What does Auto Scaling do?** The group keeps two instances running, can add a third when average CPU exceeds the target, and replaces unhealthy instances. A launch template defines how each new instance boots and starts the containers.

**Is this database highly available?** No. Each EC2 host has its own PostgreSQL container and local volume. Stickiness helps one browser see consistent data, but replacement of that host loses its local data. Production needs a shared durable database and backups.

**Why is `.env` excluded from Git and the image?** It contains a database password. Bootstrap creates a random password and stores `.env` with owner-only permissions.

**What does `chmod 640` mean?** Owner can read and write; group can read; everyone else has no access.

**What does Selenium verify?** A real browser reaches the app, checks the page heading, submits a unique task, and sees that task in the DOM. A passing run is evidence of the front end, backend request, and database insert/read working together.
