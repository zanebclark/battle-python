# Repo Setup Recipe

Instructions on how to create the repo. In some cases, these notes lead down a dead-end. In other cases, they are the key to success. Either way, I forget what I did and need reminding.

## Prerequisites:
1. Python: Install a version of Python supported by AWS SAM
2. GitHub: Create a GitHub Profile
3. AWS Account: Create an AWS Account
4. Check out [these instructions](https://dev.to/aws-builders/minimal-aws-sso-setup-for-personal-aws-development-220k) on setting up SSO for AWS
5. Install the AWS CLI
6. Configure AWS SSO with `aws configure sso`
7. Install the AWS SAM CLI

## Deploy AWS Resources

Execute the following command:
```bash
sam deploy --guided
```

AWS SAM will deploy the resources defined in [template.yaml](./template.yaml) to your AWS account

When this is done, execute the following:
```bash
sam pipeline init --bootstrap
```

Follow the instructions to use a quick-start template and create two environments. AWS SAM will create a template file that GitHub will use to build and deploy your changes to AWS every time you make a change.

## Testing




# Battlesnake API
https://docs.battlesnake.com/api
https://github.com/BattlesnakeOfficial/rules

Encoding: `application/json`
Status: `HTTP 200 OK`
Timeout: In the game object

- GET /
- POST /start
- POST /move
- POST /end

us-west-2 seems to be the best region to choose

use game id values to manage concurrent games

How do I make the most out of the allotted timeout?
