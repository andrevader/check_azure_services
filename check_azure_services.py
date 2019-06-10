#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by Andre Ribas
# 8.8 30/04/2019 - Corrigido leitura multiplos subscriptions
# 8.7 29/04/2019 - Corrigido contagem backup
# 8.6 26/04/2019 - Corrigido leitura Backup para data atual
# 8.5 17/04/2019 - Ajuste unidade para ms
# 8.4 12/04/2019 - Correcao bloco monitor para LB, API, ASP, VNG
# 8.3 10/04/2019 - Correcao bloco monitor para APP
# 8.2 09/04/2019 - Correcao bloco monitor para disp SQL, LNG, CONN, BCK, APGW,
# 8.1 08/04/2019 - Correcao bloco monitor para disponibilidade SQL
# 8.0 04/04/2019 - Mudanca leitura subscription e alterado leitura para 1min
# 7.2 03/04/2019 - Correcao variaveis e inclusao o item unidade de metrica
# 7.1 03/04/2019 - Correcao variaveis None em app_mon
# 7.0 14/03/2019 - Incluindo ServiceFabric
# 6.2 07/03/2019 - Correcao if Monitor
# 6.1 01/03/2019 - Corrigindo item Metricas
# 6.0 26/02/2019 - Incluindo AppGateway
# 5.0 10/01/2019 - Incluindo VPN Gateways e ajuste Backup para subs
# 4.0 08/01/2019 - Incluindo Metricas Apps
# 3.1 21/12/2018 - Incluindo App Service Plan
# 3.0 19/12/2018 - Incluindo LoadBalancer e inf Version
# 2.1 17/12/2018 - Corrigido informacoes grafico
# 2.0 13/12/2018 - Incluido APP
# 1.0 12/12/2018 - Incluido SQL
# 0.0 30/11/2018
ver="8.8"
import datetime
import sys
import json
import os
import subprocess
from optparse import OptionParser

def main():
    parser = OptionParser(usage="usage: %prog [options] filename")

    parser.add_option("-s", "--subscription", dest="subscription",
                      help="Informar subscription")
    parser.add_option("-r", "--resourcegroup", dest="resourcegroup",
                      help="Informar resourcegroup")
    parser.add_option("-t", "--typeof", dest="typeof",
                      help="Informar Tipo de Monitoracao")
    parser.add_option("-o", "--options", dest="options",
                      help="Informacoes adicionais")
    parser.add_option("-w", "--warning", dest="warning",
                      help="Informacoes adicionais")
    parser.add_option("-c", "--critical", dest="critical",
                      help="Informacoes adicionais")
    parser.add_option("-m", "--servidor", dest="servidor",
                      help="Informacoes adicionais")
    parser.add_option("-p", "--metric", dest="metric",
                      help="Informacoes adicionais")
    parser.add_option("-n", "--namespace", dest="namespace",
                      help="Informacoes adicionais NameSpace")
    parser.add_option("-u", "--unitmetric", dest="unitmetric",
                      help="Informacoes adicionais NameSpace")
    (options, args) = parser.parse_args()

    mens=0
    if options.typeof == "backup":
        azr_backup( subs=options.subscription, resgrp=options.resourcegroup, value=options.options, mens=0, saida=0, status=0 )
    elif options.typeof == "loadbalance":
        azr_loadbalance( resgrp=options.resourcegroup, value=options.options )
    elif options.typeof == "api":
        azr_apicon( resgrp=options.resourcegroup, value=options.options )
    elif options.typeof == "webapp":
        azr_apps( servidor=options.servidor, app=options.typeof )
    elif options.typeof == "functionapp":
        azr_apps( servidor=options.servidor, app=options.typeof )
    elif options.typeof == "vpn-connection":
        azr_vpnconold( subs=options.subscription, resgrp=options.resourcegroup, value=options.options )
    elif options.typeof == "appservice":
        azr_apsrv( resgrp=options.resourcegroup, value=options.options, metric=options.metric, war=options.warning, crit=options.critical )
    elif options.typeof == "monitor":
        azr_apmon( subs=options.subscription, resgrp=options.resourcegroup, value=options.options, metric=options.metric, 
		namespace=options.namespace, war=int(options.warning), crit=int(options.critical), umetric=options.unitmetric )
    elif options.typeof == "vpngateway":
        azr_vpngw( subs=options.subscription, resgrp=options.resourcegroup, value=options.options)
    #elif options.typeof == "appgateway":
    #    azr_appgw( subs=options.subscription, resgrp=options.resourcegroup, value=options.options)
    elif options.typeof == "servicefabric":
        azr_sf( subs=options.subscription, resgrp=options.resourcegroup, value=options.options )
    else : 
        print "Opcoes: (backup, vpngateway, loadbalance, sql, webapp, functionapp, vpn-connection, api, appservice, appgateway, monitor, servicefabric)" 
        os.system("exit 3")

def resposta (saida, status, mens, perf):
   print "%s \nversion=%s|%s" %(mens, ver, perf)
   sys.exit(saida)
   return; 

def convbit(size):
    power = 2**10
    n = 1
    Dic_powerN = {1:'KB', 2:'MB', 3:'GB', 4:'TB'}
    if size <= power**2 :
        size /=  power
        #return size
        res = "%s %s" %(size, Dic_powerN[n])
        return res
        #return size, Dic_powerN[n]
    else:
        while size   >  power :
            n  += 1
            size /=  power**n
            res = "%s %s" %(size, Dic_powerN[n])
            #return size, Dic_powerN[n]
            return res

def azr_sf( subs, resgrp, value):
    command = 'az sf cluster show --subscription %s -g %s -n %s' %(subs, resgrp, value)
    valor = subprocess.check_output(command, shell=True)
    status="OK"
    saida=0
    item_dict = json.loads(valor)
    vlrst =  item_dict['provisioningState']
    if vlrst != 'Succeeded' :
        saida=2
        status="CRITICAL"
    else :
        saida=0
        status="OK"
    mens = "%s - ServiceFabric %s %s" %(status, value, vlrst)
    perf = "%s=%s;1;2" %(value, saida)
    resposta(saida, status, mens, perf)
    return;

def azr_appgw(ids, local):
    command = 'az network application-gateway show --ids %s' %(ids)
    valor = subprocess.check_output(command, shell=True)
    status="OK"
    saida=0
    item_dict = json.loads(valor)
    vlrst =  item_dict['provisioningState']
    if vlrst != 'Succeeded' :
        saida=2
        status="CRITICAL"
    else :
        saida=0
        status="OK"
    mens = "%s - Application Gateway %s %s" %(status, local, vlrst)
    perf = "%s=%s;1;2" %(local, saida)
    resposta(saida, status, mens, perf)
    return;

def azr_vpngw( subs, resgrp, value):
	command = 'az network vnet-gateway show --subscription "%s" -g %s -n %s' %(subs, resgrp, value)
	valor = subprocess.check_output(command, shell=True)
	status="OK"
	saida=0
	item_dict = json.loads(valor)
	vlrst =  item_dict['provisioningState']
	if vlrst != 'Succeeded' :
		saida=2
		status="CRITICAL"
	else :
		saida=0
		status="OK"
	mens = "%s - Gateway %s %s" %(status, value, vlrst)
	perf = "%s=%s;1;2" %(value, saida)
	resposta(saida, status, mens, perf)
	return;

def azr_vng (ids, vlrent):
	command = 'az network vnet-gateway show --ids %s' %(ids)
	valor = subprocess.check_output(command, shell=True)
	status="OK"
	saida=0
	item_dict = json.loads(valor)
	vlrst =  item_dict['provisioningState']
	if vlrst != 'Succeeded' :
		saida=2
		status="CRITICAL"
		vlrperf=0
	else :
		saida=0
		status="OK"
		vlrperf=1
	mens = "%s - %s status: %s" %(status, vlrent, vlrst)
	perf = "VNG=%s;0;0" %(vlrperf)
	resposta(saida, status, mens, perf)
	return;

def azr_apmon( subs, resgrp, value, metric, namespace, war, crit, umetric):
	if umetric is None:
		umetric="total"
	nids = '/usr/local/nagios/libexec/azure_ids.json'
	fileids = os.path.isfile(nids)
	if fileids:
		nfile = "/usr/local/nagios/libexec/.azure_ids/%s/azure_services.json" %(subs)
		vlrsubs = subs
	else:
		comsubs = "grep subscription /usr/local/nagios/.azure/clouds.config |awk '{print$3}'|tr -d '\n'"
		nfile = '/usr/local/nagios/libexec/azure_services.json'
		vlrsubs = subprocess.check_output(comsubs, shell=True)
	vlrmt=0
	conmt=0
	vid = 0
	filejson = os.path.isfile(nfile)
	if filejson:
		valor = datetime.datetime.now() - datetime.timedelta(minutes=1)
		vlrnow = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:00Z')
		interval = valor.strftime('%Y-%m-%dT%H:%M:00Z')
	else:
		saida=2
		status="CRITICAL"
		perf = "dados=0;0;0" 
		mens = "%s - Arquivo %s nao encontrado" %(status, nfile)
		resposta (saida, status, mens, perf)
	vid = "/subscriptions/%s/resourceGroups/%s/providers/%s/%s" %(vlrsubs, resgrp, namespace, value )
	if namespace == 'Microsoft.RecoveryServices/vaults':
		if vid in open(nfile).read():
			vid = "/subscriptions/%s/resourceGroups/%s/providers/%s/%s" %(vlrsubs, resgrp, namespace, value )
		else:
			namespace = 'microsoft.recoveryservices/vaults'
			vid = "/subscriptions/%s/resourceGroups/%s/providers/%s/%s" %(vlrsubs, resgrp, namespace, value )
	with open (nfile) as json_data:
		d = json.load(json_data)
		json_data.close()
		vname = 0
		vres = 0
		vtype = 0
		result = 0
		s1 = namespace.replace('/', '_')
		chave=[]
		for chave in d:
			if namespace == 'Microsoft.Sql/servers/databases' :
				vid = chave['id']
				if chave['name'] == value:
					vname = chave['name']
				if chave['resourceGroup'] == resgrp:
					vres = chave['resourceGroup']
				s2 = chave['type'].replace('/', '_')
				s5 = int(s2.find(s1))
				if s5 == 0:
					vtype = chave['type']
				if vname == value and vres == resgrp and s1 == s2:
					result = 0
					break
				else:
					result = 1
			else: 
					if chave['id'] == vid:
						item = chave['name']
						result = 0
						break
					else:
						result = 1
	if result == 1:
		saida=2
		status="CRITICAL"
		perf = "0"
		mens = "%s - Item nao encontrado" %(status)
		resposta (saida, status, mens, perf)
	if metric == "status":
		if namespace == 'Microsoft.Sql/servers/databases' :
			azr_dbsql( ids=vid )
		if namespace == 'Microsoft.Network/connections':
			azr_conn( ids=vid )
		if namespace == 'Microsoft.Network/localNetworkGateways':
			azr_lng( ids=vid )
		if namespace == 'Microsoft.Network/applicationGateways':
			azr_appgw( ids=vid, local=item )
		if namespace == 'microsoft.recoveryservices/vaults' or namespace == 'Microsoft.RecoveryServices/vaults':
			azr_bck( vlrsubs=subs, rgp=resgrp, backup=value )
		if namespace == 'Microsoft.Web/sites':
			azr_app( ids=vid )
		if namespace == 'Microsoft.Network/loadBalancers':
			azr_lb( ids=vid, vlrlb=value )
		if namespace == 'Microsoft.ApiManagement/service':
			azr_api( ids=vid, vlrapi=value )
		if namespace == 'Microsoft.Web/serverFarms':
			azr_asp( ids=vid, vlrent=value )
		if namespace == 'Microsoft.Network/virtualNetworkGateways':
			azr_vng( ids=vid, vlrent=value )
	else:
		command = "az monitor metrics list --resource %s --metric %s --start-time %s --end-time %s --interval PT1M --aggregation %s" %(vid, metric, interval, vlrnow, umetric)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	for x, y in item_dict.iteritems():
		if x == 'value' :
			unidnome = y[0]['unit']
			if unidnome == 'Percent':
				vunidn = '%'
			elif unidnome == 'Seconds':
				vunidn = 'ms'
			elif unidnome == 'MilliSeconds':
				vunidn = 'ms'
			elif unidnome == 'Count':
				vunidn = ''
			else:
				vunidn = unidnome
			nome = y[0]['name']['localizedValue']
			if umetric == 'count':
				vlrmt = y[0]['timeseries'][0]['data'][0]['count']
			elif umetric == 'average':
				vlrmt = y[0]['timeseries'][0]['data'][0]['average']
			elif umetric == 'maximum':
				vlrmt = y[0]['timeseries'][0]['data'][0]['maximum']
			elif umetric == 'minimum':
				vlrmt = y[0]['timeseries'][0]['data'][0]['minimum']
			else:
				vlrmt = y[0]['timeseries'][0]['data'][0]['total']

			if vlrmt is None:
				vlrmt=0

			if unidnome == 'Seconds':
				new = vlrmt*1000
				conmt = float('{0:.2f}'.format(new))
			else:	
				conmt = int('{0:.0f}'.format(vlrmt))
			if conmt > crit and crit > 0:
				saida=2
				status="CRITICAL"
			elif conmt > war and war > 0:
				saida=2
				status="WARNING"
			else :
				saida=0
				status="OK"
	perf = "%s= %s;%s;%s" %(nome, conmt, war, crit)
	mens = "%s - Item: %s Metric: %s Valor %s%s" %(status, value, nome, conmt, vunidn)
	resposta (saida, status, mens, perf)
	return;

def azr_asp(ids,vlrent):
	command = "az appservice plan show --ids %s" %(ids)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	saida=0
	vlrst = item_dict['provisioningState']
	if vlrst == "Succeeded" :
		saida=0
		status="OK"
		vlrperf=1
	else:
		saida=2
		status="CRITICAL"
		vlrperf=0
	mens = "%s - API %s status: %s" %(status, vlrent, vlrst)
	perf = "API=%s;0;0" %(vlrperf)
	resposta (saida, status, mens, perf)
	return;
	

def azr_apsrv( resgrp, value, metric, war, crit):
	command = "az appservice plan show -g %s  -n %s" %(resgrp, value)
	valor = datetime.datetime.now() - datetime.timedelta(minutes=5)
	vlrnow = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:00Z')
	interval = valor.strftime('%Y-%m-%dT%H:%M:00Z')
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	saida=0
	chave = []
	if item_dict['provisioningState'] == "Succeeded" :
		newcom = "az monitor metrics list --resource %s --resource-group %s --resource-type Microsoft.Web/serverFarms --metric %s --start-time %s --end-time %s --interval PT5M" %(value, resgrp, metric, interval, vlrnow)
		vlrcomm = subprocess.check_output(newcom, shell=True)
		json_comm = json.loads(vlrcomm)
   		for x, y in json_comm.iteritems():
			if x == 'value' :
				vlrmt = y[0]['timeseries'][0]['data'][0]['average']
				conmt = '{0:.0f}'.format(vlrmt)
				if conmt > crit :
					saida=2
					status="CRITICAL"
				elif conmt > war :
					saida=1
					status="WARNING"
				else :
					saida=0
					status="OK"
		menserr = "%s Uso: %s%%" %(value, conmt)
	else :
		saida=2
		status="CRITICAL"
		menserr = "Status: %s" %(item_dict['provisioningState'])
	mens = "%s - %s (v %s)|%s=%s;%s;%s" %(status, menserr, ver, value, conmt, war, crit)
	print mens
	sys.exit(saida)
	return;

def azr_apicon( resgrp, value ):
	command = "az resource show -g %s --resource-type connections -n %s --namespace Microsoft.Web" %(resgrp, value)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	chave = []
	saida=0
   	for x, y in item_dict.iteritems():
		if x == 'properties' :
			for a, b in y.iteritems():
				if a == 'statuses' :
					vlrst = b[0]['status'];
					if vlrst != 'Connected' :
						vlrcode = b[0]['error']['code'];
						saida=2
						status="CRITICAL"
						menserr = "Status: %s API: %s Code: %s" %(vlrst, value, vlrcode)
					else :
						saida=0
						status="OK"
						menserr = "Status: %s API: %s" %(vlrst, value)
	mens = "%s - %s (v %s)" %(status, menserr, ver)
	print mens
	sys.exit(saida)
	return;

def azr_api (ids, vlrapi):
	command = "az resource show --ids %s" %(ids)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	saida=0
	status=0
	for x, y in item_dict.iteritems():
		if x == 'properties' :
			for a, b in y.iteritems():
				if a == 'provisioningState' :
					vlrst = b;
					if vlrst != 'Succeeded' :
						saida=2
						status="CRITICAL"
						vlrperf=0
					else :
						saida=0
						status="OK"
						vlrperf=1
	mens = "%s - API %s status: %s" %(status, vlrapi, vlrst)
	perf = "API=%s;0;0" %(vlrperf)
	resposta (saida, status, mens, perf)
	return;

def azr_vpnconold( subs, resgrp, value ):
   command = 'az network vpn-connection show --subscription "%s" -g %s -n %s' %(subs, resgrp, value)
   valor = subprocess.check_output(command, shell=True)
   item_dict = json.loads(valor)
   vlrst = item_dict['connectionStatus']
   if vlrst == "Connected":
        vlrout = item_dict['egressBytesTransferred']
        vlrin = item_dict['ingressBytesTransferred']
        vpnin = convbit(vlrin)
        vpnout = convbit(vlrout)
        saida=0
        status="OK"
        mens = "%s - %s is %s IN: %s OUT: %s|In=%s;0;0; Out=%s;0;0" %(status, value, vlrst, vpnin, vpnout, vlrin, vlrout )
   else :
        saida=2
        status="CRITICAL"
        mens = "%s - %s is %s " %(status, value, vlrst)
   print mens
   sys.exit(saida)
   
   return; 

def azr_conn( ids ):
	command = 'az network vpn-connection show --ids %s' %(ids)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	vlrst = item_dict['connectionStatus']
	if vlrst == "Connected":
		vlrout = item_dict['egressBytesTransferred']
		vlrin = item_dict['ingressBytesTransferred']
		vpnin = convbit(vlrin)
		vpnout = convbit(vlrout)
		saida=0
		status="OK"
		mens = "%s - Connection is %s IN: %s OUT: %s" %(status, vlrst, vpnin, vpnout )
	else :
		saida=2
 		status="CRITICAL"
		vlrin=0
		vlrout=0
		mens = "%s - %s is %s " %(status, value, vlrst)
	perf = "In=%s;0;0; Out=%s;0;0" %(vlrin, vlrout)
	resposta (saida, status, mens, perf)
	return; 

def azr_bck(vlrsubs, rgp, backup):
	command = 'az backup job list --subscription %s -g %s -v %s' %(vlrsubs, rgp, backup)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	chave = []
	countvlr = 0
	vlrout = 0
	nomejob = 0
	vlrres = 0
	counterr = 0
	countsts = "ok"
	nomebck = ""
	bckerr = ""
	vlrdt=0
	saida=0
	for chave in item_dict:
		for x, y in chave.iteritems():
			if x == "properties":
				if vlrdt == 1:
					break
				for ad, dc in y.iteritems():
					if vlrdt == 1:
						break
					if ad == "status" and dc != "Completed" and dc != 'InProgress' and dc != 'CompletedWithWarnings':
						bckerr+= chave["properties"]["entityFriendlyName"]
						bckerr+= " "
						countsts = "erro"
						vlrout = dc
						counterr+=1
					if ad == "entityFriendlyName":
						nomejob = dc
						nomebck += dc
						nomebck += " "
						countvlr+=1
					if ad == "startTime":
						vlrtm = dc.split("T")
						vlrres = vlrtm[0]
						vlrbck = datetime.datetime.now().strftime('%Y-%m-%d')
						if vlrres < vlrbck:
							vlrdt=1
						else:
							countsts = "ok"
	if counterr > 0:
		saida=2
		status="CRITICAL"
		menserr="Erros: %s ( %s)" %(counterr, bckerr)
	else:
		saida=0
		status="OK"
		menserr="Erros: %s " %(counterr)
	mens = "%s - Quantidade de Backups OK: %s, %s" %(status, countvlr, menserr)
	perf = "Backup=%s;0;0" %(countvlr)
	resposta (saida, status, mens, perf)
	return;
	
   
def azr_backup( subs, resgrp, value, mens, saida, status ):
   tempjson = "/tmp/%s_%s.log" %(subs, value)
   command = 'az backup job list --subscription "%s" --resource-group %s -v %s' %(subs, resgrp, value)
   valor = subprocess.check_output(command, shell=True)
   item_dict = json.loads(valor)
   chave = []
   countvlr = 0
   counterr = 0
   nomebck = ""
   bckerr = ""
   for chave in item_dict:
        for x, y in chave.iteritems():
            if x == "properties":
                #print chave["properties"]["entityFriendlyName"]
                for ad, dc in y.iteritems():
                    if ad == "entityFriendlyName":
                        nomejob = dc
                        nomebck += dc
                        nomebck += " "
                        countvlr+=1
                    if ad == "status":
                        if dc != "Completed" and dc != 'InProgress' and dc != 'CompletedWithWarnings':
                            #bckerr+= nomejob
                            bckerr+= chave["properties"]["entityFriendlyName"]
                            bckerr+= " "
                            counterr+=1 
   if counterr > 0:
        saida=2
        status="CRITICAL"
        menserr="Erros: %s (%s)" %(counterr, bckerr) 
   else:
        saida=0
        status="OK"
        menserr="Erros: %s " %(counterr) 
   mens = "%s - Quantidade de Backup: %s, %s" %(status, countvlr, menserr)
   perf = "version=%s" %(ver)
   resposta (saida, status, mens, perf)
   return; 

def azr_dbsql( ids ):
	command = "az sql db show --ids %s" %(ids)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	vlrdb = 0
	dbsize = 0
	dblimit = 0
	dballo = 0
	#chave = []
	for x, y in item_dict.iteritems():
		if x == "status":
			countvlr = y
			if countvlr != "Online":
				saida=2
				status="CRITICAL"
				menserr="Erros: %s (%s)" %(counterr, bckerr)
			else :
				saida=0
				status="OK"
				command = "az sql db list-usages --ids %s" %(ids)
				valor = subprocess.check_output(command, shell=True)
				chave = []
				infor = json.loads(valor)
				for chave in infor:
					for a, b in chave.iteritems():
						if a == "displayName":
							vlrdb = b
						elif a == "currentValue":
							if vlrdb == "Database Size":
								dbsize = b
							else :
								dballo = b
				convsize = convbit(dbsize)
				convallo = convbit(dballo)
	perf = "banco= %s;0;%s" %(convsize, convallo)
	mens =  "%s - Status do Banco %s, Uso: %s Alocado: %s" %(status, countvlr, convsize, convallo)
	resposta (saida, status, mens, perf)
	return;

def azr_loadbalance( resgrp, value ):
	command = "az network lb show -g %s -n %s" %(resgrp, value)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	chave = []
	vlrst=0
	vlrst=0
	saida=0
   	for x, y in item_dict.iteritems():
		if x == "frontendIpConfigurations" :
			vlrip = y[0]['privateIpAddress']
			vlrst = y[0]['provisioningState']
	if vlrst == "Succeeded" :
		saida=0
		status="OK"
		menserr="LB %s status: %s IP: %s" %(value, vlrst, vlrip) 
	else :
		saida=2
		status="CRITICAL"
		menserr="LB %s status: %s IP: %s" %(value, vlrst, vlrip) 
	mens = "%s - %s (v %s)" %(status, menserr, ver)
	print mens
	sys.exit(saida)
	return;

def azr_lb( ids,vlrlb ):
	command = "az network lb show --ids %s" %(ids)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	chave = []
	saida=0
	for x, y in item_dict.iteritems():
		if x == "frontendIpConfigurations" :
			vlrip = y[0]['privateIpAddress']
			vlrst = y[0]['provisioningState']
	if vlrst == "Succeeded" :
		saida=0
		status="OK"
		vlrperf=1
	else:
		saida=2
		status="CRITICAL"
		vlrperf=0
	mens = "%s - LB %s IP: %s" %(status,vlrlb,vlrip)
	perf = "LB=%s;0;0" %(vlrperf)
	resposta (saida, status, mens, perf)
	return;

def azr_lng(ids):
	command = "az network local-gateway show --ids %s" %(ids)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	chave = []
	saida=0
	vlrst = item_dict['provisioningState']
	name = item_dict['name']
	if vlrst == "Succeeded" :
		saida=0
		status="OK"
	else:
		saida=2
		status="NOK"
	mens="%s - %s status: %s" %(status, name, vlrst)
	perf="LNG=%s;0;0" %(saida)
	resposta (saida, status, mens, perf)
	return;

def azr_app(ids):
	command = 'az webapp show --ids %s' %(ids)
	valor = subprocess.check_output(command, shell=True)
	item_dict = json.loads(valor)
	chave = []
	vlrapp=0
	stvlr=0
	for x, y in item_dict.iteritems():
		if x == 'name':
			vlrapp = y
		elif x == 'state':
			stvlr = y
	if stvlr == "Running":
		saida=0
		status="OK"
	else:
		saida=2
		status="CRITICAL"
	mens="%s - Aplicacao %s em %s" %(status, vlrapp, stvlr)
	perf="%s=%s;1;2" %(vlrapp, saida)
	resposta (saida, status, mens, perf)
	return;


def azr_apps( servidor, app ):
   command = 'az %s list --query "[].{name: name, state: state}"' %(app)
   valor = subprocess.check_output(command, shell=True)
   item_dict = json.loads(valor)
   chave = []
   vlrapp=0
   stvlr=0
   for chave in item_dict:
        if chave['name'] == servidor:
            vlrapp = chave['name']
            stvlr = chave['state']
            break
   if vlrapp == 0 :
        saida=2
        status="CRITICAL"
        menserr="Aplicacao %s nao encontrada" %(servidor) 
   elif vlrapp == servidor: 
        if stvlr == "Running": 
            saida=0
            status="OK"
            menserr="Aplicacao %s em %s" %(servidor, stvlr) 
   else: 
        saida=2
        status="CRITICAL"
        menserr="Aplicacao %s em %s" %(servidor, stvlr) 
   mens = "%s - %s" %(status, menserr)
   print mens
   sys.exit(saida)
   return;

if __name__ == '__main__':
    main()
