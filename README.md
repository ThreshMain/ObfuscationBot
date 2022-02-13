# ObfuscationBot

This bot is a project helping run a private discord server. Bot currently consists of two modules. Autopinning and message anonymizing.
#### Config
```ini
[Global]
guildid
modid
welcomechannelid
autojointhreads
sourcelink
welcomemessageid
```
`guildid` Id of the guild, `modid` Id of mod **role**, `welcomechannelid` Id of channel where will bot send his message.
This message serves as an entry point for Anonymizer module as well as quick showcase of enabled features and version.
`autojointhreads` Should bot automatically join new threads? `sourcelink` Link to source code. `welcomemessageid` Id of 
**existing** welcome message. In case you run bot for the first time, just delete this line and bot will fill it on the
first run.
### Anonymizer
Bot relays sent message to anonymize it. Supports attachments. On button interaction, bot creates new channel and listens
for messages sent there, which he then relays to chosen channel.
#### Config:
```ini
[Anonymizer]
enabled
hiddencategoryid
studycategoryid
```
`enabled` decides if the whole module is turned on. `hiddencategoryid` is id of the category where will bot create
channels to privately listen for messages. `studycategoryid` is id of category containing channels which are available
as relay targets. Bot additionaly displays only channels the user has access to.
### Autopinning
Autopinning messages with certain reaction ammount.
#### Config:
```ini
[Autopin]
enabled
emoji
lockemoji
threshold
customthreadthreshold
```
`enabled` decides if the whole module is turned on. `emoji`
represents the emoji considered when calculating votes. `lockemoji` represents emoji used by moderators (defined in
`Global` by `modid`) to prevent message locking. `threshold` represents amount of votes needed to pin a message.
`customthreadthreshold` represents custom threshold value used in threads, `-1` to disable this feature.

## "Contributing"

Feel free to create issues or PRs, try to keep the project focused on its original purpose. 
All completely new features should be discussed with @Lomohov as a discord server administrator. PRs for bugfixes are 
welcome.

To get started, you just need to install `pycord` and set `TOKEN` environmental variable to your bot's token.

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