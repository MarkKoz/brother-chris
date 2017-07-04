# Brother Chris
### Description
My personal Discord self-bot. Made for educational purposes: to learn Discord bots and Python.

### Commands
Commands can only be executed by the user with the an ID equal to `id_ user` (specified in `Configuration.json`).<br />
Commands can be executed with prefix `!` or `?`.<br />
An optional argument cannot be passed without also passing all preceding arguments regardless of if they are optional.

`[]` denotes mandatory arguments. `<>` denotes optional arguments.<br />

* `id <user>` - Retrieves IDs for `user`, current channel, and current server.
    * `user` defaults to the caller of the command.
* `react [emoji] [limit]` - Reacts with `emoji` to a quantity (`limit`) of previous messages in the current channel.
* `wc <user> <channel> <limit> <colour>` - Generates a word cloud with `colour` as the background based on a quantity (`limit`) of `user`'s messages from `channel`.
    * `user` defaults to the caller of the commands.
    * `channel` defaults to the channel in which the command was called.
    * `limit` defaults to 1000.
    * `colour` defaults to transparent. Format is a CSS3-style colour specifier; read the [ImageColor documentation](http://effbot.org/imagingbook/imagecolor.htm#color-names) for more information.

### Running
Create `Configuration.json` in the root directory. Fill in your token and user ID:

```json
{
    "token": "",
    "id_user": "",
    "extensions": ["cogs.Commands"]
}
```

Run `Bot.py` to run the bot.

### Requirements
* [Python 3.6](https://www.python.org/downloads/) or higher
* [discord.py](https://github.com/Rapptz/discord.py) async
* [world_cloud](https://github.com/amueller/word_cloud)
* [randomcolor-py](https://github.com/kevinwuhoo/randomcolor-py)
* [emoji](https://github.com/carpedm20/emoji)
