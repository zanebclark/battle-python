FROM public.ecr.aws/lambda/python:3.11 as test
# Upgrade pip
RUN python -m pip install --upgrade pip

WORKDIR = ${LAMBDA_TASK_ROOT}

COPY src ./src
COPY pyproject.toml .
RUN touch README.md

RUN pip install -r ./src/requirements.txt
RUN pip install .

CMD ["battle_python.api.lambda_handler"]
