{ pkgs, ... }: {
  # Service definitions
  services = {
    # Enable Docker for container management
    docker.enable = true;

    # Configure PostgreSQL service
    postgres = {
      enable = true;
      package = pkgs.postgresql_16; # Specify PostgreSQL version 16
      extensions = [ "pgvector" ];    # Enable the pgvector extension
    };

    # Enable Redis service
    redis.enable = true;
  };

  # Additional environment setup can go here
  # For example, installing packages available in the terminal
  packages = [
    pkgs.nodejs_20 # Specify Node.js version 20.x
  ];
}
