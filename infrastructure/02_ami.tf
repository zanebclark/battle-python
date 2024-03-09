data "aws_ami" "battlesnakes-ubuntu" {
  most_recent = true
  owners      = ["self"]
  filter {
    name   = "tag:Application"
    values = ["battlesnakes"]
  }
}
