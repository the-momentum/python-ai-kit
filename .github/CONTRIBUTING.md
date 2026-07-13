# How to contribute to the Python AI Kit

1. Fork the repository.
2. Clone your fork.
3. Make sure `uv` and [`just`](https://github.com/casey/just) are installed.
4. Generate a project of the chosen template type.
5. Switch there, develop changes.
6. Come back to the forked main repository, create a new branch and move your changes to the corresponding directories here. Remember to include Jinja syntax if some changes are not bound to all template types.
7. If your change touches the structure of `python-ai-kit/app/`, check that `python-ai-kit/AGENTS.md.jinja` still tells the truth
8. Commit your changes and push the entire branch to the remote (`git push -u origin <local_branch_name>`). It will automatically create a Pull Request here.

Your contributions are more than welcome! :)
