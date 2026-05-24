"""External service integrations for TestGen AI."""

from .github_pusher import push_to_github

__all__ = ["push_to_github"]