### Ex - Docker Compose for Elasticsearch and Kibana

Below is a simple example of a Docker Compose file for Elasticsearch and Kibana. You can create or copy this file using a text editor.

```yml
services:
  elasticsearch:
    image: elasticsearch:7.17.22
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - 9200:9200
    networks:
      - my-network

  kibana:
    image: kibana:7.17.22
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - 5601:5601
    depends_on:
      - elasticsearch
    networks:
      - my-network

networks:
  my-network:
    driver: bridge
```

Start Elasticsearch and Kibana by running the following command:

```bash
docker-compose up -d
```

This command starts the containers in the background. Elasticsearch can be accessed at `http://localhost:9200`, while Kibana is accessible at `http://localhost:5601`.

To stop the containers, you can use the following command in the same directory:

```bash
docker-compose stop
```

To remove the containers, you can use the following command:

```bash
docker-compose down
```