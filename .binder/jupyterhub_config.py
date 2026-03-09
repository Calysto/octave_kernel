# ruff: noqa: F821
c.Spawner.environment = {"DISPLAY": ":99"}

c.KubeSpawner.lifecycle_hooks = {
    "postStart": {"exec": {"command": ["Xvfb", ":99", "-screen", "0", "1024x768x24"]}}
}
