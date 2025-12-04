# API Gateway Comparison

The comparison is divided into three scenarios:

1. ```1-restart-and-shutdown```
   Gateways are shut down using the kill signals SIGTERM and SIGKILL. Then they are restarted and their downtime is measured.
2. ```2-dynamic reconfiguration```
   Gateways are dynamically reconfigured during runtimer for a HTTP and a gRPC route. The switch latency is measured.
3. ```3-load-test```
   Gateways are tested in a load test, combining multiple numbers of requests and concurrency.



## Setup

All experiments are set up the same way:

* Each scenario directory contains directories named after the respective tested gateway. In these directories, the individual gateways are set up including a docker compose file and configuration file(s).
* The ```/base``` directory contains additional components needed for conducting the experiments, such as echo servers, proto files, and experiment orchestration scripts.
* The ```run_experiments.sh``` file starts and orchestrates the experiments in all variants. 
* The ```/results``` directory contains the raw data collected in the runs of the experiments.
* The ```/analysis``` directory contains Jupyter notebooks with tables and diagrams analyzing the results. 



In order for the experiments to execute, Python needs to be installed. A Python virtual environment can then be created and activated using  ```python3 -m venv venv``` and ```source venv/bin/activate```. The requirements needed to recreate the experiments and to run the Jupyter notebooks can then be installed using ```pip install -r requirements.txt```. 

The Python virtual environment can be removed using ```deactivate``` and ```rm -r venv```. 



## Software Versions Used

* Docker 28.5.1
* Caddy 2.8.4
* HAProxy 3.2.6
* NGINX 1.29.3
* Traefik 3.5
* Tyk 5.10.0
* Redis 7.4.6

* Python 3.14.0