# SSH Key Authentication

## Enable in docker-compose.yml
```yaml
environment:
  - AUTHKEY_ENABLED:true
volumes:
  - ./auth_keys/:/auth_keys/
```

## Create SSH key pair, make sure it's called auth.pub and else map a volume toward it.
```bash
ssh-keygen -t rsa -b 4096 -f ./auth_keys/auth
```

## Set correct permissions

### Linux
```bash
chmod 600 auth      # Private key must be readable only by owner
chmod 644 auth.pub  # Public key can be readable by all
```

## Usage
1. Place public key (*.pub) in auth_keys directory
2. Update AUTHKEY_PATH if needed
3. Connect using your private key:
```bash
ssh -i path_to_private_key mockit_username@mockit_ip
```

## Watch our online youtube video to see this feature in action
https://www.youtube.com/watch?v=sp0SX0Uczz0