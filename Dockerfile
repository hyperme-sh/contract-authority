FROM python:3.13-alpine@sha256:9ef1a599f863231c3d91e941389bfdc4a2d6070557243d54df1a4e57015b960e AS build
COPY --from=ghcr.io/astral-sh/uv:0.11.26@sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock LICENSE ./
COPY src src
RUN uv sync --frozen --no-dev --no-editable
FROM python:3.13-alpine@sha256:9ef1a599f863231c3d91e941389bfdc4a2d6070557243d54df1a4e57015b960e
COPY --from=build /app/.venv /app/.venv
COPY LICENSE /usr/share/licenses/hypermesh-contract-authority/
ARG SOURCE_REVISION
ENV CONTRACT_AUTHORITY_SOURCE_REVISION=$SOURCE_REVISION
USER 10001:10001
ENTRYPOINT ["/app/.venv/bin/hypermesh-contract-authority"]
