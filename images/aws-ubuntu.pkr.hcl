variable "region" {
  type    = string
  default = "us-west-2"
}

variable "vpc_id" {
  type    = string
  default = "vpc-05d9a2495e008d250"
}

variable "subnet_id" {
  type    = string
  default = "subnet-0ec0cd1e355058e3c"
}

locals { timestamp = regex_replace(timestamp(), "[- TZ:]", "") }

packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = "~> 1.3.0"
    }
  }
}

source "amazon-ebs" "ubuntu" {
  profile       = "personal"
  ami_name      = "battlesnakes-ubuntu-${local.timestamp}"
  instance_type = "t3.small"
  region        = var.region
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  vpc_id       = var.vpc_id
  subnet_id    = var.subnet_id
  ssh_username = "ubuntu"
  tags = {
    "Application" : "battlesnakes"
  }
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "shell" {
    script = "./images/scripts/install_dependencies.sh"
  }

  # I lack required permissions to provision the file to the terminal location.
  # Instead, I provision the file to a less sensitive location and sudo move it
  # to the terminal destination
  provisioner "file" {
    source      = "./images/files/battlesnakes.conf"
    destination = "/tmp/battlesnakes.conf"
  }

  provisioner "file" {
    source      = "./images/files/gunicorn.service"
    destination = "/tmp/gunicorn.service"
  }

  provisioner "file" {
    source      = "./images/files/gunicorn.socket"
    destination = "/tmp/gunicorn.socket"
  }
  #  TODO: Install in /opt

  provisioner "shell" {
    inline = [
      "sudo mv /tmp/battlesnakes.conf /etc/nginx/sites-enabled/battlesnakes.conf",
      "sudo mv /tmp/gunicorn.service /etc/systemd/system/gunicorn.service",
      "sudo mv /tmp/gunicorn.socket /etc/systemd/system/gunicorn.socket",

      "curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.2 python3 -",
      "export PATH=\"/home/ubuntu/.local/bin:$PATH\"",
      "whoami",
      "echo ~ubuntu",
      "cd ~ubuntu",
      "git clone -b ec2 https://github.com/zanebclark/battle-python.git",
      "cd battle-python",
      "poetry install",
      "echo \"LOG_LEVEL=INFO\" | sudo tee -a /etc/environment",

      "sudo systemctl daemon-reload",
      "sudo systemctl enable --now gunicorn.socket",
      "sudo systemctl enable gunicorn.service",
      "sudo systemctl start gunicorn.service",

      "sudo service nginx restart",
      "sudo systemctl enable nginx",
      "sudo systemctl start nginx",
    ]
  }
}
