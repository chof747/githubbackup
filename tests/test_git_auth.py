import ast
import base64
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit, urlunsplit


# Load the functions without initializing the application's MQTT connection.
source = Path(__file__).resolve().parents[1] / "github_backup.py"
tree = ast.parse(source.read_text())
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in {"git_environment", "clean_origin_credentials", "extract_relevant_info"}]
namespace = {"os": os, "base64": base64, "subprocess": subprocess,
             "urlsplit": urlsplit, "urlunsplit": urlunsplit}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), "exec"), namespace)


class GitAuthTests(unittest.TestCase):
    def test_rotation_changes_temporary_git_credentials(self):
        for token in ("old-token", "new-token"):
            env = namespace["git_environment"](token)
            index = int(env["GIT_CONFIG_COUNT"]) - 1
            self.assertEqual(env[f"GIT_CONFIG_KEY_{index}"], "http.https://github.com/.extraheader")
            header = env[f"GIT_CONFIG_VALUE_{index}"]
            self.assertEqual(base64.b64decode(header.split()[-1]).decode(), f"x-access-token:{token}")
            self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")

    def test_existing_origin_is_cleaned_without_changing_repository(self):
        with tempfile.TemporaryDirectory() as path:
            subprocess.run(["git", "init", "-q", path], check=True)
            subprocess.run(["git", "-C", path, "remote", "add", "origin",
                            "https://old-token@github.com/owner/repo.git"], check=True)
            namespace["clean_origin_credentials"](path)
            url = subprocess.check_output(["git", "-C", path, "remote", "get-url", "origin"], text=True).strip()
            self.assertEqual(url, "https://github.com/owner/repo.git")

    def test_new_clone_url_contains_no_token(self):
        repo = {"name": "repo", "clone_url": "https://github.com/owner/repo.git"}
        self.assertEqual(namespace["extract_relevant_info"](repo, "user", "secret")["clone_url"], repo["clone_url"])


if __name__ == "__main__":
    unittest.main()
