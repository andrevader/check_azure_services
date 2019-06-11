# check_azure_services
Script to monitor Azure Services, using Azure CLI.

**Prequisites**

1. Install Azure CLI (for more information, access https://docs.microsoft.com/pt-br/cli/azure/install-azure-cli?view=azure-cli-latest)

**Installation**

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

5. As nagios user, execute this command to create your information azure file.

```
/usr/bin/az resource list > /usr/local/nagios/libexec/azure_services.json
```

6. Download and copy the script to your nagios script directory (ex /usr/local/nagios/libexec)


**Configuration**

	-s", "--subscription" : Define your ID subscription
    -r", "--resourcegroup": Define your ResourceGroup
    -t", "--typeof": Define your monitoring item
		- Options: backup, vpngateway, loadbalance, sql, webapp, functionapp, vpn-connection, api, appservice, appgateway, monitor, servicefabric
    -o", "--options", dest="options": Define your item name (ex. db name, storage name)
    -w", "--warning", dest="warning": Define your Warning thresholds;
    -c", "--critical", dest="critical": Define your Critical thresholds;
    -m", "--servidor", dest="servidor": Define your server
    -p", "--metric", dest="metric": Define your metric (If not use "monitor" in --typeof, select status)
    -n", "--namespace", dest="namespace": Define your value of Type Azure (ex. 'Microsoft.Web/sites')
    -u", "--unitmetric", dest="unitmetric": Define your metric unit (If necessary)

Examples:

- Monitoring Backup
```
/usr/local/nagios/libexec/check_azure_services.py -t monitor -s <subscription> -r <resourcegroup> -o <namevault> -w 0 -c 0 -p status -n 'Microsoft.RecoveryServices/vaults' 
```

- Monitoring DB
```
/usr/local/nagios/libexec/check_azure_services.py -t monitor -s <subscription> -r <resourcegroup> -o <namevault> -w 0 -c 0 -p status -n 'Microsoft.Sql/servers/databases' 
```

- Monitoring Request Failed in AppInsights
```
/usr/local/nagios/libexec/check_azure_services.py -t monitor -s <subscription> -r <resourcegroup> -o <namevault> -w 0 -c 0 -p requests/failed -n 'microsoft.insights/components' 
```
