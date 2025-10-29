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
Como usar:
Em outro terminal, inicie um controlador de sua preferência.

Execute o comando a seguir, o arquivo topologia.py é opcional mas recomendado.
```bash
sudo python run_topology.py topologia.py
```
Quando o servidor do mininet e do rpc forem iniciados, você entrará na CLI do mininet, assim, pode iniciar, em outro terminal a interface do botmaster, com:
```bash
python botmaster.py
```

## TODO

* fazer a segunda opção de spawnar uma subrede;
* colocar o capymoa no controlador;
* colocar MAIS opções de ddos, com ferramentas sinistras;
