# Autonomous Agent Runtime

Phase A layers autonomous behavior on top of the existing `RuntimeService`:

`WakeupLoop -> Planner -> Task creation -> RuntimeService -> ReflectionEngine -> experience memory`

Run the local demo from the repository root:

```bash
python demo.py
```

Run the focused tests:

```bash
pytest backend/tests/test_autonomous_runtime.py
```
