resource "aws_dynamodb_table" "battlesnakes_requests" {
  name         = "battlesnakesRequests"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "snakeGameID"
  range_key    = "turn"

  attribute {
    name = "snakeGameID"
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
  hash_key     = "snakeGameID"

  attribute {
    name = "snakeGameID"
    type = "S"
  }

  attribute {
    name = "gameID"
    type = "S"
  }

  attribute {
    name = "snakeID"
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
    hash_key           = "gameID"
    name               = "gameIDIndex"
    non_key_attributes = ["snakeID"]
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
