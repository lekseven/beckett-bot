# {user_id0:{channel_id0,channel_id1...}, user_id1...}, where user_id* - superuser, which use cmd

cmd_channels = {}    # for !mute, !*deny, !purge
rep_channels = {}    # for !say and reports for *deny commands
torpor_users = {}
silence_users = {}
cmd_server = {}

mute_channels = set()
mute_light_channels = set()
ignore_users = set()
emoji_users = set()
game = False
silence_ans = {}
t_start = None
t_finish = None
t_work = None
debug = False

# data_used = []