# Brother Chris
### Description
My personal Discord self-bot. Made for educational purposes: to learn Discord
bots and Python.

### Commands
Commands can only be executed by the users specified in the configuration.<br>
Commands can be executed with prefixes specified in the configuration.<br>
An optional argument cannot be passed without also passing all preceding
arguments regardless of if they are optional.

`[]` denotes mandatory arguments. `<>` denotes optional arguments.<br>

* `created <channel>` - Retrieves date and time at which `channel` was created.
If `channel` is not specified, the current channel is used.
* `emojiurl [emoji]` - Retrieves a url to the custom `emoji`.
* `icon <user>` - If `user` is specified, retrieves `user`'s avatar. Otherwise,
retrieves the current server's icon.
* `id <user>` - Retrieves IDs for `user`, current channel, and current server.
    * `user` defaults to the caller of the command.
* `perms <user> <channel>` - Retrieves a list of permissions for `user` in
`channel`.
* `react [emoji] [limit]` - Reacts with `emoji` to a quantity (`limit`) of
previous messages in the current channel.
* `wc <user> <channel> <limit> <colour>` - Generates a word cloud with `colour`
as the background based on a quantity (`limit`) of `user`'s messages from
`channel`.
    * `user` defaults to the caller of the commands.
    * `channel` defaults to the channel in which the command was called.
    * `limit` defaults to 1000.
    * `colour` defaults to transparent. Format is a CSS3-style colour specifier;
    read the [ImageColor documentation](http://effbot.org/imagingbook/imagecolor.htm#color-names)
    for more information.

### Configuration
A file named `Configuration.json` and in the same directory as `Bot.py` is used
for configuration of the bot. Below is the base configuration for the bot; it is
the bare-minimum required for the bot to run properly.

```json
{
    "Bot": {
        "token": "",
        "isSelfBot": true,
        "idUsers": [
            ""
        ],
        "extensions": [
            "cogs.Commands"
        ],
        "prefixes": [
            "!",
            "?"
        ],
        "name": "Brother Chris"
    }
}
```

* `token` - The bot's token.
* `isSelfBot`- `true` if `token` is for a self bot.
* `idUsers` - A list of user IDs which identify who can use the bot. Any other
user's messages with commands are completely ignored.
* `extensions` - A list of extensions for the bot to load.
* `prefixes` - A list of prefixes to use for commands.
* `name` - The bot's name. Only used for logging right now.

Some additional extensions require more configuration. Their configurations go
after the `Bot` object.

#### Permissions
```json
"Permissions": {
    "justify": true,
    "padding": 4
},
```

* `justify` - If `true`, the permission name column of the output is
left-justified and padded with the with a width of `padding`.
* `padding` - _One less_ than the width of space between the name and and value
columns.

#### Welcome
```json
"Welcome": {
    "idDyno": "155149108183695360",
    "channels": [
        ""
    ],
    "msgDyno": "joined the server! Give them a welcome!"
}
```

* `idDyno` - The ID of the bot that sends the messages to listen for.
* `channels` - A list of channel IDs in which to listen for the bot's messages.
* `msgDyno` - The search string used to determine if the bot's message is a
welcome.

#### Word Police
```json
"WordPolice": {
    "idServers": [
        ""
    ],
    "thumbnail": "",
    "words": {
        "book": [
            "cook",
            "look"
        ],
        "books": [
            "cooks",
            "looks"
        ]
    }
}
```

* `idServers` - A list of server IDs in which to listen for messages.
* `thumbnail` - A URL to the thumbnail to use in the embed.
* `words` -

### Running
Run `Bot.py` to run the bot.

```bash
python Bot.py
```

### Requirements
* [Python 3.6](https://www.python.org/downloads/) or higher
* [discord.py](https://github.com/Rapptz/discord.py) async
* [world_cloud](https://github.com/amueller/word_cloud)
* [randomcolor-py](https://github.com/kevinwuhoo/randomcolor-py)
* [emoji](https://github.com/carpedm20/emoji)
