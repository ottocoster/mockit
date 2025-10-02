# Navigate to the tests directory
cd /home/osboxes/Documents/Slurpit/mockit/tests

# Start the test environment
docker compose -f compose-dev_ssh_telnet.yml up -d --build

# Run the tests
docker exec devices-test_container sh -c "pytest test_ssh_telnet.py -v"

# Clean up when done
docker compose -f compose-dev_ssh_telnet.yml down