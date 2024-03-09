resource "aws_iam_instance_profile" "battle-python-server-instance-profile" {
  name = "battle-python-server-profile"
  role = aws_iam_role.battle-python-server-role.name
}

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.battle-python-server-role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role" "battle-python-server-role" {
  name = "battle-python-server-role"
  path = "/"

  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "ec2.amazonaws.com"
          },
          "Effect" : "Allow"
        }
      ]
    }
  )
}
