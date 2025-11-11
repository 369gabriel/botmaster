Funcionamento do ```run_topology.py```:
* Inicia um server rpc que provê as seguintes funções:
	* get_all_hosts():
		* retorna um dict com todos os hosts (hostnames e ips)
	* run_command_on_host(host, command):
		* recebe, como parâmetro, um hostname e um comando;
		* o comando é executado dentro daquele host, com o hostname especificado no mininet;
* Além do host rpc, ele executa a topologia passada como argumento, na execução do script, ou uma topologia padrão definida como a linear com k=4;

Funcionamento do ```botmaster.py```
* é o painel de controle da "botnet";
* se conecta com o server rpc e usa as duas funções providas pelo server para obter as informações necessárias e executar comandos;
* Todo o resto das funcionalidades é baseada nessas duas premissas.

Funcionamento do ```attack_logger.py```
* Módulo responsável por registrar todos os ataques lançados em formato CSV;
* Cria automaticamente o arquivo `attack_flows.csv` com os seguintes campos:
  * `timestamp` - Data e hora do ataque em formato ISO 8601
  * `attack_id` - UUID único para cada ataque
  * `attack_type` - Tipo do ataque (ping, tcp_syn, udp, iperf)
  * `attackers` - Lista de hosts atacantes (separados por vírgula)
  * `target_ip` - IP do alvo
  * `target_port` - Porta do alvo (quando aplicável)
  * `duration` - Duração do ataque em segundos
  * `num_attackers` - Número de hosts atacantes
* Fornece função `generate_report()` para gerar relatórios estatísticos dos ataques;
* Os dados são salvos automaticamente sempre que um ataque é lançado pelo botmaster;

# Como usar:
Em outro terminal, inicie um controlador de sua preferência.

Execute o comando a seguir, o arquivo topologia.py é opcional mas recomendado.
```bash
sudo python run_topology.py topologia.py
```
Quando o servidor do mininet e do rpc forem iniciados, você entrará na CLI do mininet, assim, pode iniciar, em outro terminal a interface do botmaster, com:
```bash
python botmaster.py
```

## Funcionalidades do Menu Principal

1. **Gerenciamento de hosts** - Adiciona e gerencia hosts controlados ("infectados")
2. **Lançar teste de tráfego** - Executa ataques DDoS com opções:
   - Ping (ICMP Flood)
   - TCP SYN Flood (via hping3)
   - UDP Flood (via hping3)
   - TCP/UDP Flood (via iperf)
3. **Visualizar relatório de ataques** - Exibe estatísticas dos ataques registrados
4. **Sair** - Encerra o botmaster

## Registro de Ataques (CSV)

Todos os ataques lançados são automaticamente registrados no arquivo `attack_flows.csv`. Este arquivo contém:
- Timestamp de cada ataque
- ID único (UUID)
- Tipo de ataque
- Lista de atacantes
- IP e porta do alvo
- Duração do ataque
- Número de atacantes

O formato do CSV é compatível para análise posterior e comparação com dados de detecção de anomalias.

## TODO

* fazer a segunda opção de spawnar uma subrede;
* colocar o capymoa no controlador;
* colocar MAIS opções de ddos, com ferramentas sinistras;
