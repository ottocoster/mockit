# SSH Key Authentication

## Enable in docker-compose.yml
```yaml
environment:
  AUTHKEY_ENABLED: true
  AUTHKEY_PATH: /auth_keys/auth.pub # Path to public key
```

## Create SSH key pair
```bash
ssh-keygen -t rsa -b 4096 -f ./auth_keys/auth
```

## Usage
1. Place public key (*.pub) in auth_keys directory
2. Update AUTHKEY_PATH if needed
3. Connect using your private key:
```bash
ssh -i path_to_private_key mockit_username@mockit_ip
```