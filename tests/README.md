
# Test all devices

```sh
docker compose -f docker-compose_set1.yml up -d
```

```sh
docker exec devices-test_container sh -c "pytest test_ssh_set1.py | tee /output.txt"
```

```sh
docker cp devices-test_container:/output.txt .
```

```sh
docker compose -f docker-compose_set1.yml down
```
