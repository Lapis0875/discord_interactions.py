from annotations import UserCommandOption, BooleanCommandOption, StringCommandOption, IntegerCommandOption, \
    ChannelCommandOption, RoleCommandOption

print(f"{3!r}")
print(f"{3!s}")
print(f"{int!r}")
print(f"{int!s}")


def test_arg_hint(
    integer: IntegerCommandOption(name='IntegerArg', description='Integer Command Option Type Hint Test', required=True, default=False),
    string: StringCommandOption(name='StringArg', description='String Command Option Type Hint Test', required=False, default=False),
    boolean: BooleanCommandOption(name='BooleanArg', description='Boolean Command Option Type Hint Test', required=False, default=True),
    user: UserCommandOption(name='UserArg', description='discord.User Command Option Type Hint Test', required=False, default=False),
    channel: ChannelCommandOption(name='ChannelArg', description='discord.abc.GuildChannel Command Option Type Hint Test', required=False, default=False),
    role: RoleCommandOption(name='RoleArg', description='discord.Role Command Option Type Hint Test', required=False, default=False)
) -> None:
    print(integer)
    print(string)
    print(boolean)
    print(user)


print(test_arg_hint.__annotations__)
print(test_arg_hint.__annotations__['integer'].name)
