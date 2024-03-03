variable "region" {
  type = string
  default = "us-west-2"
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
  ami_name = "battlesnakes-ubuntu-${local.timestamp}"
  instance_type = "t3.small"
  region = var.region
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  ssh_username = "ubuntu"
}

build {
  source = ["source.amazon-ebs.ubuntu"]

  provisioner "file" {
    source = "./fastapi_nginx.conf"
    destination = "/etc/nginx/sites-enabled/fastapi_nginx.conf"
  }

  provisioner "shell" {
    script = "../scripts/image_setup.sh"
  }
}
