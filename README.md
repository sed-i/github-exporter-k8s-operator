# github-exporter-k8s

## Usage (dev)

```bash
charmcraft pack
juju deploy ./github-exporter-k8s_ubuntu@24.04-amd64.charm ghe --resource github-exporter-image=githubexporter/github-exporter:1.3.1
juju config ghe repos="canonical/prometheus-k8s-operator"
curl $(juju status --format=json | jq -r '.applications.ghe.address'):9171/metrics
```
