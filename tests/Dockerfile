FROM python

ENV PYTHONWARNINGS=always
ENV PYTHONDONTWRITEBYTECODE=1

ARG PY27=2.7.18
ARG PY35=3.5.10
ARG PY36=3.6.15
ARG PY37=3.7.14
ARG PY38=3.8.14

ENV PYENV_ROOT="/.pyenv"

RUN apt-get install -y git
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git $PYENV_ROOT

ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
RUN --mount=type=cache,target=$PYENV_ROOT/version/$PY27 pyenv install $PY27
RUN --mount=type=cache,target=$PYENV_ROOT/version/$PY35 pyenv install $PY35
RUN --mount=type=cache,target=$PYENV_ROOT/version/$PY36 pyenv install $PY36
RUN --mount=type=cache,target=$PYENV_ROOT/version/$PY37 pyenv install $PY37
RUN --mount=type=cache,target=$PYENV_ROOT/version/$PY38 pyenv install $PY38

COPY . /heartbeat
WORKDIR /heartbeat

RUN --mount=type=cache,target=/root/.cache \
    pip install -U pip tox pytest

RUN printf "$PY27\n$PY35\n$PY36\n$PY37\n$PY38\n" > .python-version