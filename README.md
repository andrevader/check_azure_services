# check_azure_services
Script to monitor Azure Services, using Azure CLI.

** Prequisites **

1. Install Azure CLI (for more information, access https://docs.microsoft.com/pt-br/cli/azure/install-azure-cli?view=azure-cli-latest)

** Installation **

1. Access your NAGIOS server as nagios user.

2. Connect your NAGIOS server to Azure services using Azure CLI

```
az login
```

3. Access Azure portal and type your code and user access.

4. Define your azure subscription. 

```
az account set -s <your subscription>
```

