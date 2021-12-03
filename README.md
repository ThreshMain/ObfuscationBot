# ObfuscationBot

This bot currently uses python's discord.py library to run. In some future release, I'd like to move to discord.js JavaScript library, since discord.py is no longer supported.

## Usage

Bot has mapping configured in config.json, which assigns 3-letter codes to channelIds. All messages in a followed channel starting with that code will be then rerouted to the channel corresponding to the code. Original messages are deleted. All other messages which do not follow this formatting are deleted too to keep the channel clear.

## "Contributing"

Feel free to create issues or PRs, try to keep the project focused on its original purpose. All completely new features should be discussed with @Lomohov as a discord server administrator.

Git repository follows these practises: [https://nvie.com/posts/a-successful-git-branching-model/](https://nvie.com/posts/a-successful-git-branching-model/), what it means in short:
- All PRs should be created against dev branch
- Dev branch has no specific version, thus it will always be labeled "Dev"
- Once there is enough new features to make meaningfull release, new branch from dev is created.
  - Last bugfixes and final testing will be done on this branch
  - The branch is then merged into main, release is created and code is deployed
  - This update changes minor version
- In case of small bugfixes, new branch is created from main, bugfixes are done on this branch and merged back
  - This update changes patch version

This project uses modified [semantic versioning](https://semver.org/). Since by definition, major number represents backwards incompatible API change and this project has so far no API, we are using only `MINOR.PATCH` with additional modifiers for pre-releases.

Any comments, questions or issues with repository address to @stepech