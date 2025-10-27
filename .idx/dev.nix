{ pkgs, ... }: {
  # Service definitions
  services = {
    # Enable Docker for container management
    docker.enable = true;

    # Enable Redis service
    redis.enable = true;
  };

  # Additional environment setup can go here
  packages = [
    pkgs.nodejs_20 # Specify Node.js version 20.x
  ];
}
