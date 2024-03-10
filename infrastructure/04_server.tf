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
    from_port   = 80
    to_port     = 80
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
  ami                         = data.aws_ami.battlesnakes-ubuntu.id
  instance_type               = "t3.small"
  iam_instance_profile        = aws_iam_instance_profile.battle-python-server-instance-profile.name
  key_name                    = "battlesnakes-server"
  subnet_id                   = aws_subnet.public-us-west-2a.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.battlesnake-sg.id]
  user_data = file("scripts/user_data.sh")
  tags = {
    "Application" : "battlesnakes"
    "Name" = "battlesnake-server"
  }
}

resource "aws_route53_record" "custom_domain" {
  zone_id = "Z01559062PX1OYNVW42PW"
  name    = "zane-b-clark.com"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.battlesnake-server.public_ip]
}

resource "aws_route53_record" "custom_domain_wildcard" {
  zone_id = "Z01559062PX1OYNVW42PW"
  name    = "www.zane-b-clark.com"
  type    = "A"
  ttl     = "300"
  records = [aws_instance.battlesnake-server.public_ip]
}

resource "aws_cloudwatch_metric_alarm" "ec2_cpu" {
  alarm_name                = "cpu-utilization"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "2"
  metric_name               = "CPUUtilization"
  namespace                 = "AWS/EC2"
  period                    = "120" #seconds
  statistic                 = "Average"
  threshold                 = "80"
  alarm_description         = "This metric monitors ec2 cpu utilization"
  insufficient_data_actions = []
  dimensions = {
    InstanceId = aws_instance.battlesnake-server.id
  }
}
