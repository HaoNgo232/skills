import unittest
from adapters import REGISTRY, get_adapter, DispatchOptions
from adapters.cline_adapter import ClineAdapter
from adapters.opencode_adapter import OpenCodeAdapter
from adapters.agy_adapter import AgyAdapter
from adapters.git_utils import calculate_git_delta

class TestAgentDispatcher(unittest.TestCase):

    def test_registry_contains_all_agents(self):
        self.assertIn("cline", REGISTRY)
        self.assertIn("opencode", REGISTRY)
        self.assertIn("agy", REGISTRY)

    def test_identity_verification(self):
        for name in ["cline", "opencode", "agy"]:
            adapter = get_adapter(name)
            identity = adapter.verify_identity()
            self.assertTrue(identity.is_available, f"{name} should be available")
            self.assertIsNotNone(identity.version, f"{name} should report a version")
            # Verify agy version is resolved correctly
            if name == "agy":
                self.assertEqual(identity.version, "1.2.3")

    def test_command_building_cline(self):
        adapter = ClineAdapter()
        opts = DispatchOptions(timeout=60, model="test-model", worktree=True)
        cmd = adapter.build_command("test prompt", opts)
        self.assertIn("--auto-approve", cmd)
        self.assertIn("--timeout", cmd)
        self.assertIn("60", cmd)
        self.assertIn("-m", cmd)
        self.assertIn("test-model", cmd)
        self.assertIn("--worktree", cmd)
        self.assertEqual(cmd[-1], "test prompt")

    def test_command_building_opencode(self):
        adapter = OpenCodeAdapter()
        opts = DispatchOptions(model="test-model")
        cmd = adapter.build_command("test prompt", opts)
        self.assertIn("run", cmd)
        self.assertIn("--auto", cmd)
        self.assertIn("--format", cmd)
        self.assertIn("json", cmd)
        self.assertIn("-m", cmd)
        self.assertIn("test-model", cmd)
        self.assertEqual(cmd[-1], "test prompt")

    def test_command_building_agy(self):
        adapter = AgyAdapter()
        opts = DispatchOptions(model="gemini-custom")
        cmd = adapter.build_command("test prompt", opts)
        self.assertIn("--print", cmd)
        self.assertIn("--dangerously-skip-permissions", cmd)
        self.assertIn("--output-format", cmd)
        self.assertIn("json", cmd)
        self.assertIn("--model", cmd)
        self.assertIn("gemini-custom", cmd)

    def test_git_delta_subtraction(self):
        before = {"dirty_file.txt", "old_file.ts"}
        after = {"dirty_file.txt", "old_file.ts", "new_agent_file.txt"}
        delta = calculate_git_delta(before, after, ".")
        self.assertEqual(delta["newly_modified_files"], ["new_agent_file.txt"])

if __name__ == "__main__":
    unittest.main()
