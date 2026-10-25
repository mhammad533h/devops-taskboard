# DevOps Taskboard

Original three-tier lab application: a browser interface, a Flask API, and PostgreSQL. Docker Compose starts the web and database containers. A named Docker volume retains database data when containers are recreated.

## Architecture

```text
Browser / Selenium -> Application Load Balancer -> Auto Scaling Group (2 EC2 instances)
                                                    |-> Flask + PostgreSQL + named volume
                                                    |-> Flask + PostgreSQL + named volume
```

This lab design stores data separately on each EC2 instance. ALB cookie stickiness keeps a browser on one target for 24 hours, but data is **not shared** across instances and can be lost when Auto Scaling replaces an instance. A production deployment would use one shared, durable database such as RDS. Do not describe this lab as a highly available database.

## Local or single-EC2 setup

1. Install Docker Engine and the Compose plugin. On Amazon Linux 2023, run `sudo bash scripts/bootstrap-ec2.sh` from this directory; it installs both and starts the app.
2. Copy `.env.example` to `.env` and set a unique `POSTGRES_PASSWORD`. Never commit `.env`.
3. Run `docker compose up -d --build` (use `sudo` on EC2 unless your user is in the Docker group).
4. Open `http://INSTANCE_PUBLIC_IP:8080` (single EC2) or `http://localhost:8080` (local).
5. Run `docker compose ps`, `docker image ls`, and `docker volume ls` for evidence.

The database port is not exposed on the host. Only the web service publishes port 8080. The Flask app connects to `db` by Compose service name over the internal network.

## AWS load balancer and Auto Scaling

`infra/stack.json` creates an internet-facing ALB, target group, launch template, and Auto Scaling group with two desired instances across two provided public subnets in different Availability Zones. It also creates security groups and a CPU target-tracking scaling policy. New instances clone **your public copy** of this repository and run the bootstrap script. Your existing EC2 instances remain useful for a manual Docker demonstration, but the Auto Scaling group creates its own instances.

Prerequisites: AWS CLI credentials, a VPC, two public subnets in different AZs with routes to an internet gateway, an EC2 key pair, and a public Git repository containing these files. Create a fresh repository for your own original code and upload all project files except `.env` and local screenshots. `t3.small` is the default due to the two containers per host. Running an ALB and multiple EC2 instances incurs charges.

```bash
aws cloudformation validate-template --template-body file://infra/stack.json
aws cloudformation deploy \
  --stack-name devops-taskboard \
  --template-file infra/stack.json \
  --parameter-overrides \
    VpcId=vpc-EXAMPLE \
    SubnetIds=subnet-EXAMPLE1,subnet-EXAMPLE2 \
    KeyName=YOUR_KEYPAIR \
    SshCidr=YOUR_PUBLIC_IP/32 \
    RepoUrl=https://github.com/YOU/devops-taskboard.git \
    RepoRef=main
aws cloudformation describe-stacks --stack-name devops-taskboard \
  --query 'Stacks[0].Outputs' --output table
```

Wait until both targets are healthy in EC2 > Target Groups. Browse to the `AppUrl` stack output. If targets remain unhealthy, SSH to an instance and inspect `sudo tail -100 /var/log/cloud-init-output.log`, `sudo docker compose -f /opt/devops-taskboard/compose.yaml ps`, and container logs. The ALB uses HTTP for the lab; use TLS for any real deployment.

## Demonstrate the six practical tasks

### 1. ALB and Auto Scaling (2 marks)

Show the CloudFormation stack resources, ALB DNS name, target group with two healthy EC2 targets, Auto Scaling group desired capacity 2, and the working app through the ALB. For an optional scaling demonstration, change desired capacity to 3 and show the third target registering, then restore to 2. Do not claim CPU scaling occurred unless the activity history shows it.

### 2. Linux administration (1 mark)

On an EC2 instance, run these and capture command output:

```bash
pwd
ls -la
mkdir -p ~/devops-lab/evidence
touch ~/devops-lab/evidence/permissions.txt
chmod 640 ~/devops-lab/evidence/permissions.txt
ls -l ~/devops-lab/evidence/permissions.txt
id
```

Explain `640`: owner read/write, group read, others no access. The bootstrap script also creates `/opt/devops-taskboard` and sets `.env` to mode `600`.

### 3. Docker installation, image, container (2 marks)

```bash
sudo docker --version
sudo docker compose version
cd /opt/devops-taskboard
sudo docker compose build web
sudo docker image ls
sudo docker compose ps
```

Show the `Dockerfile`, its build output, the custom web image, and both running containers.

### 4. Named volume persistence (1 mark)

On a **single instance** or local machine, create a task in the UI and note its exact text. Then run:

```bash
sudo docker volume ls
sudo docker compose down
sudo docker compose up -d --build
sudo docker compose ps
```

Refresh the **same instance** and show the task still exists. Do **not** use `docker compose down -v`; that removes the named volume. `sudo bash scripts/verify-persistence.sh` automates this check against `localhost:8080` and prints PASS or FAIL. On an ALB-backed instance, the script must run locally over SSH so routing stays on that host.

### 5. Compose multi-container app (2 marks)

Show `compose.yaml`, `sudo docker compose ps`, a successful `curl -fsS http://localhost:8080/healthz`, and a browser view. Explain that `depends_on` waits for a healthy database and the app uses the service name `db`.

### 6. Selenium (2 marks)

Install Python, Chrome or Chromium, and the Selenium package on your test machine:

```bash
python -m pip install -r tests/requirements.txt
APP_URL=http://YOUR_ALB_DNS python tests/test_ui.py
```

On Windows PowerShell, set the URL with `$env:APP_URL='http://YOUR_ALB_DNS'`, then run `python tests/test_ui.py`.

Selenium opens the app, verifies the `Taskboard` heading, creates a uniquely named task, then verifies its text appears. Run it against the ALB URL, save the terminal PASS output, and take a browser screenshot. Selenium Manager may download the matching driver on the first run.

## Evidence checklist and viva prompts

Save screenshots or terminal captures of the ALB URL; two healthy targets; ASG desired/min/max; Linux `ls -l` after `chmod`; Docker version, custom image, and running containers; Compose file and two services; named volume before/after container recreation; passing Selenium output and browser. Capture real evidence only after executing each step.

Be ready to explain: image vs container, why `.dockerignore` excludes `.env`, named volume vs container filesystem, why Compose service DNS works, health checks, ALB routing and sticky sessions, what Auto Scaling replaces, and why local volumes on two instances are not a shared database.

## Cleanup

After the viva, `aws cloudformation delete-stack --stack-name devops-taskboard` removes the AWS stack; verify deletion in the console to stop charges. On a manually prepared instance, `docker compose down -v` also deletes that instance's database volume and all stored tasks.

## Sources

- [AWS CloudFormation scaled and load-balanced application walkthrough](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/walkthrough-autoscaling.html)
- [AWS Auto Scaling group resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-autoscaling-autoscalinggroup.html)
- [AWS ALB target group stickiness](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html)
- [Docker Compose plugin installation](https://docs.docker.com/compose/install/linux/)
