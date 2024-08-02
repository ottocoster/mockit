# Setting up environment

`export PYTHONPATH=$PYTHONPATH:$(pwd)`

# Test all devices

```sh
docker compose -f docker-compose_set3.yml up -d
```

```sh
docker exec devices-test_container sh -c "pytest test_ssh_set3.py | tee /output.txt"
```

```sh
docker cp devices-test_container:/output.txt .
```

```sh
docker compose -f docker-compose_set3.yml down
```