# ruff: noqa: F821
c.Spawner.environment = {"OCTAVE_EXECUTABLE": "octave", "DISPLAY": ":99"}


async def pre_spawn_hook(spawner):
    import subprocess

    subprocess.Popen(
        ["Xvfb", ":99", "-screen", "0", "1024x768x24"],
        stdout=open("/dev/null", "w"),
        stderr=open("/dev/null", "w"),
    )


c.Spawner.pre_spawn_hook = pre_spawn_hook
