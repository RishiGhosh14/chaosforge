# ChaosForge SDK

For source-checkout development, add `packages/sdk` to `PYTHONPATH` and use the
client against a running API:

```python
from chaosforge import ChaosForgeClient

client = ChaosForgeClient(api_key="optional-api-key")
result = client.start_experiment(agent_version="v2", scenario_id="stale-payment-response")
print(result["evaluation"])
```
