resource "aws_dynamodb_table" "battlesnakes_requests" {
  name         = "battlesnakesRequests"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "SnakeGameID"
  range_key    = "turn"

  attribute {
    name = "SnakeGameID"
    type = "S"
  }

  attribute {
    name = "turn"
    type = "N"
  }

  ttl {
    attribute_name = "expireAt"
    enabled        = true
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    "Application" : "battlesnakes"
    "Name" = "battlesnakes_requests"
  }

  lifecycle {
    ignore_changes = [
      write_capacity, read_capacity
    ]
  }
}

resource "aws_dynamodb_table" "battlesnakes_games" {
  name         = "battlesnakesGames"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "SnakeGameID"

  attribute {
    name = "SnakeGameID"
    type = "S"
  }

  attribute {
    name = "GameID"
    type = "S"
  }

  attribute {
    name = "SameID"
    type = "S"
  }

  ttl {
    attribute_name = "expireAt"
    enabled        = true
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }


  global_secondary_index {
    hash_key           = "GameID"
    name               = "GameIDIndex"
    non_key_attributes = ["SnakeID"]
    projection_type    = "INCLUDE"
  }

  tags = {
    "Application" : "battlesnakes"
    "Name" = "battlesnakes_games"
  }

  lifecycle {
    ignore_changes = [
      write_capacity, read_capacity
    ]
  }
}
