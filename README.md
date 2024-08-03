# Kubernetes Configuration Enumeration and Analysis Tool

## Description

This project is a CLI tool designed to enumerate and analyze Kubernetes cluster configurations. It provides functionalities to dump the cluster configuration and perform various analyses on the configurations.

## Installation

### Prerequisites

- Python 3.12+
- [PDM](https://pdm-project.org/en/latest/)

Install dependencies

```sh
pdm install
```

## Usage

This tool provides several commands to dump and analyze k8s config.

### Dump Cluster Configuration

To dump the configuration of a Kubernetes cluster:

```sh
pdm run kube-enum dump <KUBERNETES_API_URL> [--output <OUTPUT_FILE_PATH>]
```

#### Example

```sh
pdm run kube-enum dump https://my-kubernetes-api-server -o config.json
```

### Analyze Kubernetes Configuration

The `analyze` command provides several subcommands to analyze the dumped Kubernetes configuration.

#### Show Secrets and Environment Variables

```sh
pdm run kube-enum analyze secrets <CONFIG_FILE> [--truncate <LENGTH>] [--skip <STRING>] [--skip-ns <NAMESPACE>]
```

#### Example

```sh
pdm run kube-enum analyze secrets config.json --truncate 20 --skip 'BEGIN' --skip-ns kube-system
```

#### Log None Values

```sh
pdm run kube-enum analyze none-values <CONFIG_FILE>
```

#### Example

```sh
pdm run kube-enum analyze none-values config.json
```

#### Show Verbose Structure

```sh
pdm run kube-enum analyze verbose <CONFIG_FILE>
```

#### Example

```sh
pdm run kube-enum analyze verbose config.json
```

#### Check for Unused Resources

```sh
pdm run kube-enum analyze unused <CONFIG_FILE>
```

#### Example

```sh
pdm run kube-enum analyze unused config.json
```

## Disclaimer

This tool is intended for ethical hacking and security analysis purposes on authorized systems only. Unauthorized use of this tool to access or modify systems without permission is illegal and unethical. Always obtain proper authorization before using this tool on any system.

For any issues or contributions, please refer to the project's repository.
