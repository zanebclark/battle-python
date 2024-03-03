resource "aws_security_group" "battlesnake-sg" {
  name        = "battlesnake-sg"
  description = "Allow API Access"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Not sure"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Unfettered outbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "battlesnake-server" {
  ami                         = "ami-08f7912c15ca96832"
  instance_type               = "t3.small"
  key_name                    = "battlesnakes-server"
  subnet_id                   = aws_subnet.public-us-west-2a.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.battlesnake-sg.id]
  user_data                   = file("userdata.tpl")
  tags                        = {
    "Name" = "battlesnake-server"
  }

}
