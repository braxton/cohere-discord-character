# Cohere Character Bot
Uses the Cohere API to provide an interactive chatbot that can understand context
## Setup
1. Rename `docker-compose.example.yml` to `docker-compose.yml` and fill out the following values:

    - `mariadb` Service
      - `MYSQL_PASSWORD`: The non-root user (character-bot) password
      - `MYSQL_ROOT_PASSWORD`: The root user password
    - `character-bot` Service
      - `COHERE_API_KEY`: Your key for the Cohere API
      - `DISCORD_GUILD_ID`: The guild ID for the server you'll be testing in
      - `DISCORD_BOT_TOKEN`: The token for the Discord bot
      - `DB_PASSWORD`: The same password from the `mariadb` service's `MYSQL_PASSWORD` field


2. Run `build.sh` to create the character-bot image used in `docker-compose.yml`

3. Bring the Docker container online with `docker-compose up`
    - If you would like to detach from the container, tack on the detach flag (`-d`)